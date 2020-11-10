import datetime
import sys
from multiprocessing import Lock

import prawcore
from praw import Reddit

from blottertrax.config import Config
from blottertrax.database import Database
from blottertrax.helper import templates


class ModMail:
    def __init__(self, lock: Lock):
        self.config = Config()
        self.logger = Logger()
        self.database = Database(lock)

        try:
            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.config.USER_AGENT,
                                 username=self.config.USER_NAME)

        except KeyError:
            sys.stderr.write('Check if the configuration is set right')
            sys.stderr.flush()

            exit('Check if the configuration is set right')

    def run(self):
        for message in self.reddit.subreddit(self.config.SUBREDDIT).mod.stream.modmail_conversations(state="new"):
            self._process_modmail_message(message)

    def _process_modmail_message(self, message) -> None:

        if self.database.known_mod_mail(message) is True:
            return

        try:
            current_time_utc = datetime.datetime.utcnow()
            print(f"To: {message.user}, Id: {message.id}")

            """
            Ensure no other mod has already replied to this message.
            We don't want to step on active conversations.
            Check the user has a recent submission.
            If not, they might not be contacting about a post.
            """
            if message.last_mod_update is None and len(message.user.recent_posts) > 0:
                account_creation_time = datetime.datetime.fromtimestamp(round(message.user.created_utc))
                account_age = current_time_utc - account_creation_time

                hours_since_creation = account_age.days * 24

                if hours_since_creation < self.config.MINIMUM_ACCOUNT_AGE / 3600 \
                        or message.user.comment_karma < self.config.MINIMUM_COMMENT_KARMA:
                    """ Users account is too new, notify them. """
                    message.reply(templates.get_modmail_reply_new_account(
                        message.user.name,
                        message.user.recent_posts[0]),
                        author_hidden=True
                    )
        except prawcore.exceptions.NotFound:
            """ User is likely shadowbanned. """
        except AttributeError:
            """ Likely that the users account has been deleted. """
        finally:
            message.read()
            message.archive()
            self.database.save_mod_mail(message)
