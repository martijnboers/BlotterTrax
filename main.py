import sys
import time
import traceback

import pylast
from praw import Reddit

import templates
from config import Config
from database import Database
from repostCheck import RepostCheck
from lastfm import LastFM
from youtube import Youtube
from soundcloud import Soundcloud
from title_parser import TitleParser


class BlotterTrax:
    reddit: Reddit = None
    useragent: str = 'BlotterTrax /r/listentothis submission bot by /u/plebianlinux'
    config: Config = None
    youtube: Youtube = None
    soundcloud: Soundcloud = None
    last_fm: LastFM = None
    database: Database = None
    repostCheck: RepostCheck = None
    crash_timeout: int = 10

    def __init__(self):
        try:
            self.config = Config()
            self.youtube = Youtube()
            self.soundcloud = Soundcloud()
            self.last_fm = LastFM()
            self.database = Database()
            self.repostCheck = RepostCheck()

            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)

        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        for submission in self.reddit.subreddit(self.config.SUBREDDIT).stream.submissions():
            
            #start by checking if any posts posted 70+ hours ago have broken 100 upvotes, if not hit 100 delete to not check it again
            self._archive_succesful_post()
            
            #continue to submission processing
            if self.database.known_submission(submission) is True:
                continue

            if submission.is_self is True:
                self.database.save_submission(submission)
                # We currently don't do anything further with self posts.  Move to the next post.
                continue

            try:
                artist_name = TitleParser.get_artist_name_from_submission_title(submission.title)
            except LookupError:
                # Can't find artist from submission name, skipping
                self.database.save_submission(submission)
                continue
            
            # Get artist for most future use
            prio_artist = TitleParser.get_prioritized_artist(artist_name)
            
            try:
                song_name = TitleParser.get_song_name_from_submission_title(submission.title, artist_name)
            except LookupError:
                self.database.save_submission(submission)

                continue

            # Check Youtube.
            youtube_service = self.youtube.get_service_result(submission.url)
            if youtube_service.exceeds_threshold is True:
                self._perform_exceeds_threshold_mod_action(submission, youtube_service)
                self.database.save_submission(submission)
                continue
            
            # Check Soundcloud.
            soundcloud_service = self.soundcloud.get_service_result(submission.url)
            if soundcloud_service.exceeds_threshold is True:
                self._perform_exceeds_threshold_mod_action(submission, soundcloud_service)
                self.database.save_submission(submission)
                continue

            # Check Last.FM
            try:
                last_fm_service = self.last_fm.get_service_result(prio_artist)
                if last_fm_service.exceeds_threshold is True:
                    self._perform_exceeds_threshold_mod_action(submission, last_fm_service)
                    self.database.save_submission(submission)
                    continue
            except pylast.WSError:
                # Go ahead and continue execution.  Don't want to fail completely just because one service failed.
                pass
            
            if last_fm_service.exceeds_threshold is True:
                self._archive_submission_exceeding_threshold(submission, last_fm_service.service_name,
                                                             last_fm_service.threshold, last_fm_service.listeners_count)
                continue
            
            repost = self._repost_process(prio_artist, song_name, submission)
            if repost is True:
                self._reply_with_sticky_post(submission, templates.submission_repost)
                continue
            
            
            # Yeey this post probably isn't breaking the rules 🌈
            try:
                if self.config.SEND_ARTIST_REPLY is True:
                    self._reply_with_sticky_post(submission, self.last_fm.get_artist_reply(prio_artist))
                # Made it all the way.  Save submission record.
                self.database.save_submission(submission)
            except (pylast.WSError, LookupError):
                # Can't find artist, continue
                self._repost_process(prio_artist, song_name, submission)
                continue

    def _perform_exceeds_threshold_mod_action(self, submission, service):
        if self.config.REMOVE_SUBMISSIONS is True:
            self._remove_submission_exceeding_threshold(submission, service)
        else:
            submission.report(
                '''{} exceeds {:,}.  Actual: {:,}'''.format(service.service_name, service.threshold,
                                                                         service.listeners_count))

    def _remove_submission_exceeding_threshold(self, submission, service):
        reply = templates.submission_exceeding_threshold.format(
            submission.author.name, service.service_name, service.threshold, service.listeners_count, submission.id
        )
        submission.mod.remove()
        self._reply_with_sticky_post(submission, reply)

    def _archive_succesful_post(self):
        newIDList = self.repostCheck.get_old_submissions(time.time())
        print(newIDList)
        for postID in newIDList:
            oldSubmission = self.reddit.submission(id=postID[0])
            oldScore = oldSubmission.score
            if oldScore > 1:
                artist = TitleParser.get_artist_name_from_submission_title(oldSubmission.title)
                self.repostCheck.add_count(TitleParser.get_prioritized_artist(artist).lower())
                print(artist)

    @staticmethod
    def _reply_with_sticky_post(submission, reply_text):
        comment = submission.reply(reply_text)
        comment.mod.distinguish("yes", sticky=True)
    
    def _repost_process(self, artist_name, song_name, submission):
        #always ran at same place, so saves some space
        self.database.save_submission(submission)

        print(artist_name)

        return self._process_artist(artist_name.lower(), song_name, submission.id)
    
    def _process_artist(self, artist_name, song_name, postID):
        lastPosted = self.repostCheck.get_artist_timestamp(artist_name)
        currentTime = time.time()
        
        if lastPosted is None:
            self.repostCheck.new_entry(artist_name, song_name, currentTime, postID)
        else:
            #set repost time according to the rules
            allowedArtistTime = min(max(lastPosted[1] * 2592000, 604800), 7776000)
            if (currentTime - allowedArtistTime) > lastPosted[0]:
                if lastPosted[1] is 0:
                    #do song test
                    songPosted = self.repostCheck.search_song(artist_name, song_name)

                    if songPosted is None:
                        self.repostCheck.replace_entry(artist_name, song_name, currentTime, postID)
                    elif (currentTime - 604800) > songPosted[0]:
                        self.repostCheck.replace_entry(artist_name, song_name, currentTime, postID)
                    else:
                        return True
                
                else:
                    self.repostCheck.replace_entry(artist_name, song_name, currentTime, postID)
            
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
