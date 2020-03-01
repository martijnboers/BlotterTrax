import sys
import time
import traceback

import pylast
from praw import Reddit

import templates
from config import Config
from database import Database
from lastfm import LastFM
from youtube import Youtube
from soundcloud import Soundcloud


class BlotterTrax:
    reddit: Reddit = None
    useragent: str = 'BlotterTrax /r/listentothis submission bot by /u/plebianlinux'
    config: Config = None
    youtube: Youtube = None
    soundcloud: Soundcloud = None
    last_fm: LastFM = None
    database: Database = None
    crash_timeout: int = 10

    def __init__(self):
        try:
            self.config = Config()
            self.youtube = Youtube()
            self.soundcloud = Soundcloud()
            self.last_fm = LastFM()
            self.database = Database()

            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)

        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        for submission in self.reddit.subreddit(self.config.SUBREDDIT).stream.submissions():
            if self.database.known_submission(submission) is True:
                continue

            if submission.is_self is True:
                self.database.save_submission(submission)
                # We currently don't do anything further with self posts.  Move to the next post.
                continue
            if "playlist" in submission.title.lower():
                # We currently don't do anything with Playlist posts.  Move to the next post.
                self.database.save_submission(submission)
                continue

            try:
                artist_name = self._get_artist_name_from_submission_title(submission.title)
            except LookupError:
                # Can't find artist from submission name, skipping
                self.database.save_submission(submission)
                continue
            
            #get artist for most future use
            prio_artist = self._get_prioritized_artist(artist_name)
            
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

            # Yeey this post probably isn't breaking the rules 🌈
            try:
                if self.config.SEND_ARTIST_REPLY is True:
                    self._reply_with_sticky_post(submission, self.last_fm.get_artist_reply(prio_artist))
                # Made it all the way.  Save submission record.
                self.database.save_submission(submission)
            except (pylast.WSError, LookupError):
                # Can't find artist, continue execution
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

    def _reply_with_sticky_post(self, submission, reply_text):
        comment = submission.reply(reply_text)
        comment.mod.distinguish("yes", sticky=True)

    @staticmethod
    def _get_prioritized_artist(artist_list):
        if artist_list[1] is None:
            return artist_list[0]
        
        return artist_list[1]
    
    @staticmethod
    def _get_artist_name_from_submission_title(post_title):
        #get main artist
        dash_char = ['-', '—']
        double_dash = False
        artist = None
        for dash in dash_char:
            if (dash + dash) in post_title:
                artist = post_title.split(dash + dash)[0].strip()
                double_dash = True
                break
        
        if double_dash is False:
            for dash in dash_char:
                if dash in post_title:
                    artist = post_title.split(dash)[0].strip()
                    break
        
        
        #get feature artist if exists
        feature_list = ['feat.', 'ft.', 'feature', 'featuring']
        lower_title = post_title.lower()
        feature_artist = None
        
        for feature in feature_list:
            if feature in lower_title:
                feat_index = lower_title.index(x)
                
                #remove featuring from artist if exists
                if len(artist) > feat_index:
                    artist = artist[:feat_index].strip()
                
                feat_index += len(x)
                
                #isolate featuring artist
                feature_artist = post_title[featIndex:].strip()
                break
        
        #further process if found
        if feature_artist is not None:
            for end_char in [' -', ')', '[', ' —']:
                if end_char in feature_artist:
                    feature_artist = feature_artist.split(x)[0]
        
        if feature_artist is not None:
            feature_artist = feature_artist.strip()
        
        return_list = [artist, feature_artist]
        
        #if return_list[0] is none there is no way to trust whatever is in [1] anyway as the post title is a mess.
        if return_list[0] is not None:
            return return_list
        
        raise LookupError

    def daemon(self):
        try:
            self._run()
        except Exception:
            traceback.print_exc(file=sys.stdout)
            time.sleep(self.crash_timeout)
            self.daemon()


if __name__ == '__main__':
    BlotterTrax().daemon()
