import sys
import time
import traceback

import pylast
from praw import Reddit

from blottertrax.helper import templates
from blottertrax.config import Config
from blottertrax.database import Database
from blottertrax.services.lastfm import LastFM
from blottertrax.services.youtube import Youtube
from blottertrax.services.soundcloud import Soundcloud
from blottertrax.helper.title_parser import TitleParser
from blottertrax.helper.repost_checker import RepostChecker


class BlotterTrax:
    reddit: Reddit = None
    useragent: str = 'BlotterTrax /r/listentothis submission bot by /u/plebianlinux'
    config: Config = None
    last_fm: LastFM = None
    database: Database = None
    repost_checker: RepostChecker = None
    crash_timeout: int = 10
    services: list = None

    def __init__(self):
        try:
            self.config = Config()
            self.last_fm = LastFM()
            self.database = Database()
            self.services = [Youtube(), Soundcloud(), self.last_fm]
            self.repost_checker = RepostChecker()

            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)

        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        for submission in self.reddit.subreddit(self.config.SUBREDDIT).stream.submissions():
            
            #start by checking if any posts posted 70+ hours ago have broken 100 upvotes, if not hit 100 delete to not check it again
            self._process_successful_post()
            
            #continue to submission processing
            exceeds_threshold = False
            
            if self.database.known_submission(submission) is True:
                continue

            if submission.is_self is True:
                self.database.save_submission(submission)
                # We currently don't do anything further with self posts.  Move to the next post.
                continue

            try:
                parsed_submission = TitleParser.create_parsed_submission_from_submission(submission)
            except LookupError:
                # Can't find artist from submission name, skipping
                self.database.save_submission(submission)
                continue
            
            for service in self.services:
                try:
                    result = service.get_service_result(parsed_submission)

                    if result.exceeds_threshold is True:
                        self._perform_exceeds_threshold_mod_action(submission, result)
                        exceeds_threshold = True

                        break
                except Exception:
                    traceback.print_exc(file=sys.stdout)
                    # Go ahead and continue execution
                    # Don't want to fail completely just because one service failed.
                    pass
                finally:
                    self.database.save_submission(submission)
            
            if parsed_submission.song_title is not None:
                repost = self._repost_process(parsed_submission)
                if repost is True:
                    self._perform_repost_mod_action(submission, templates.submission_repost)
                    continue
            
            # Yeey this post probably isn't breaking the rules 🌈
            try:
                if self.config.SEND_ARTIST_REPLY is True and exceeds_threshold is False:
                    self._reply_with_sticky_post(submission, self.last_fm.get_artist_reply(parsed_submission))
            except (pylast.WSError, LookupError):
                # Can't find artist, continue
                self._repost_process(parsed_submission)
                continue

    def _perform_exceeds_threshold_mod_action(self, submission, service):
        if self.config.REMOVE_SUBMISSIONS is True:
            self._remove_submission_exceeding_threshold(submission, service)
        else:
            submission.report(templates.mod_note_exceeding_threshold.format(service.service_name, service.threshold,
                                                                            service.listeners_count))

    def _remove_submission_exceeding_threshold(self, submission, service):
        reply = templates.submission_exceeding_threshold.format(
            submission.author.name, service.service_name, service.threshold, service.listeners_count, submission.id
        )
        # This is *theoretically* supposed to add a modnote to the removal reason so mods know why.  Currently not working?
        mod_message = templates.mod_note_exceeding_threshold.format(service.service_name, service.threshold,
                                                                    service.listeners_count)
        submission.mod.remove(False, mod_message)
        self._reply_with_sticky_post(submission, reply)
    
    def _perform_repost_mod_action(self, submission, template):
        if self.config.REMOVE_SUBMISSIONS is True:
            self._remove_repost(submission, template)
        else:
            submission.report("repost :(")
    
    def _remove_repost(self, submission, template):
        reply = template
        submission.mod.remove()
        self._reply_with_sticky_post(submission, reply)

    def _process_successful_post(self):
        new_id_list = RepostChecker.get_submissions_before_time(time.time() - 252000)
        for post_id in new_id_list:
            old_submission = self.reddit.submission(id=post_id[0])
            old_score = old_submission.score
            if old_score > 100:
                artist = TitleParser.create_parsed_submission_from_submission(old_submission)
                RepostChecker.add_count(TitleParser.get_prioritized_artist(artist).lower())

    @staticmethod
    def _reply_with_sticky_post(submission, reply_text):
        comment = submission.reply(reply_text)
        comment.mod.distinguish("yes", sticky=True)
    
    def _repost_process(self, parsed_submission):
        #always ran at same place, so saves some space
        self.database.save_submission(parsed_submission)

        return self._process_artist(parsed_submission)
    
    def _process_artist(self, parsed_submission):
        artist_name = TitleParser.get_prioritized_artist(parsed_submission).lower()
        song_name = parsed_submission.song_title
        post_id = parsed_submission.id
        last_posted = RepostChecker.get_artist_timestamp(artist_name)
        current_time = time.time()
        
        if last_posted is None:
            RepostChecker.new_entry(artist_name, song_name, current_time, post_id)
        else:
            #set repost time according to the rules
            allowed_artist_time = min(max(last_posted[1] * 2592000, 604800), 7776000)
            if (current_time - allowed_artist_time) > last_posted[0]:
                if last_posted[1] == 0:
                    #do song test
                    song_posted = RepostChecker.search_song(artist_name, song_name)

                    if song_posted is None or (current_time - 604800) > song_posted[0]:
                        RepostChecker.replace_entry(artist_name, song_name, current_time, post_id)
                    else:
                        return True
                
                else:
                    RepostChecker.replace_entry(artist_name, song_name, current_time, post_id)
            
            else:
                return True
        
        return False
    
    def daemon(self):
        try:
            self._run()
        except Exception:
            traceback.print_exc(file=sys.stdout)
            time.sleep(self.crash_timeout)
            self.daemon()


if __name__ == '__main__':
    BlotterTrax().daemon()
