# flake8: noqa
from praw.models import Submission

submission_exceeding_threshold: str = '''
Our apologies /u/{} but your post has been automatically removed because the artist has too many {}. The maximum is {:,} and this link has {:,}.
If you think this is in error, please [contact the mods](https://www.reddit.com/message/compose?to=/r/listentothis&subject=Post removed in error.&message=https://redd.it/{}). 

If you're new to the subreddit, please [read the full subreddit rules](https://www.reddit.com/r/listentothis/wiki/rules).

^^Don't ^^blame ^^me, ^^I'm ^^just ^^a ^^bot! [ ^^bugs&code ](https://github.com/martijnboers/BlotterTrax)
'''

submission_repost: str = '''
>**Artist Reposting**

This post has been removed due to the artist having been posted too recently. No artist may be posted more than once a week and you may not use the same song within a 30 day period. Artists with posts that score more than 100pts may not be posted for the next month; artists that gain multiple posts of 100pts will be put on a cooldown for up to 90 days.

A full explanation of this rule can be found [here](https://www.reddit.com/r/listentothis/wiki/rules).
'''

musicbrainz_artist_info: str = '''
**{}** {}
___

- album: {} {}
- tags: {}
- socials: {}

^^Displaying ^^incorrect ^^data? ^^Submit ^^a [^^correction ](https://musicbrainz.org/artist/{})  
^^For ^^reporting ^^bugs ^^or ^^other ^^questions [ ^^click·here ](https://github.com/martijnboers/BlotterTrax)
'''

mod_note_exceeding_threshold: str = '{} exceeds {:,}.  Actual: {:,}.'

self_promotion: str = '''
/u/{}, your submission has been removed from /r/listentothis for:

> **Self Promotion/Personal or Professional Association**

We do not allow personal projects to be posted in /r/listentothis.  If you have a personal or professional connection to the artist (e.g. friend or family member or this is a video you directed or produced, etc), we consider this as doing promotional work on the artist's behalf. Please post this in our [weekly music melting pot thread.](http://www.reddit.com/r/listentothis/search?q=self%3Ayes+%22melting+pot%22+-flair%3Amodpost&restrict_sr=on&sort=new&t=week) or on [any of these subreddits](https://www.reddit.com/u/evilnight/m/redditunes) dedicated to Redditor-made music.

___



___


If you have any questions or believe that there has been an error, you may [PM the moderators](http://www.reddit.com/message/compose?to=/r/listentothis&subject=Please review my post). You may also [click here to see our full rule set](https://www.reddit.com/r/listentothis/wiki/rules).
'''

modmail_reply: str = '''
/u/{},

If you are contacting us about your [recent submission]({}), it was likely removed due to your account being too new to participate in our community.  Please continue to participate by leaving comments on r/listentothis and elsewhere on reddit and then come back to submit some music. As policy, we don't disclose the specific karma minimum for submitting.

Furthermore, please carefully review [our rules](https://www.reddit.com/r/listentothis/wiki/rules) when you return.

^This ^message ^was ^sent ^by ^an ^automated ^bot.  ^If ^you ^believe ^this ^message ^does ^not ^resolve ^your ^issue ^please ^feel ^free ^to ^reply.
'''


def get_modmail_reply_new_account(username: str, recent_submission: Submission):
    return modmail_reply.format(username, recent_submission.permalink)
