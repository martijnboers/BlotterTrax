import datetime
from multiprocessing import Lock

import prawcore
from praw import Reddit

from blottertrax.config import Config
from blottertrax.database import Database
from blottertrax.helper import templates
from blottertrax.logger import Logger


class ModMail:
    def __init__(self, lock: Lock):
        self.config = Config()
        self.logger = Logger()
        self.database = Database(lock)

        try:
            self.reddit = Reddit(client_id=self.config.REDDIT.CLIENT_ID, client_secret=self.config.REDDIT.CLIENT_SECRET,
                                 password=self.config.REDDIT.PASSWORD, user_agent=self.config.REDDIT.USER_AGENT,
                                 username=self.config.REDDIT.USER_NAME)

        except KeyError:
            self.logger.exception('Check if the configuration is set right')
            exit()

    def run(self):
        for message in self.reddit.subreddit(self.config.REDDIT.SUBREDDIT).mod.stream.modmail_conversations(state="new"):
            if self.database.known_mod_mail(message) is True:
                continue

            try:
                current_time_utc = datetime.datetime.utcnow()
                self.logger.info(f"Handling message {message.id}")

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

                    if hours_since_creation < self.config.REDDIT.MINIMUM_ACCOUNT_AGE / 3600 \
                            or message.user.comment_karma < self.config.REDDIT.MINIMUM_COMMENT_KARMA:
                        self.logger.info(f"Notifying  {message.user}, that their account is too new")
                        """ Users account is too new, notify them. """
                        message.reply(templates.get_modmail_reply_new_account(
                            message.user.name,
                            message.user.recent_posts[0]),
                            author_hidden=True
                        )
                        message.read()
                        message.archive()
            except prawcore.exceptions.NotFound:
                """ User is likely shadowbanned. """
            except AttributeError:
                """ Likely that the users account has been deleted. """
            finally:
                self.database.save_mod_mail(message)
