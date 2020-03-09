submission_exceeding_threshold: str = '''
Our apologies /u/{} but your post has been automatically removed because the artist has too many {}. The maximum is {:,} and this link has {:,}.
If you think this is in error, please [contact the mods](https://www.reddit.com/message/compose?to=/r/listentothis&subject=Post removed in error.&message=https://redd.it/{}). 

If you're new to the subreddit, please [read the full subreddit rules](https://www.reddit.com/r/listentothis/wiki/rules).


_Don't blame me, I'm just a bot_ | [_Bugs & Code_](https://github.com/martijnboers/BlotterTrax)
'''

submission_repost: str = '''
>**Artist Reposting**

This post has been removed due to the artist having been posted too recently. No artist may be posted more than once a week and you may not use the same song within a 30 day period. Artists with posts that score more than 100pts may not be posted for the next month; artists that gain multiple posts of 100pts will be put on a cooldown for up to 90 days.

A full explanation of this rule can be found [here](https://www.reddit.com/r/listentothis/wiki/rules).
'''

reply_with_last_fm_info: str = '''
**{}**

> {}

[last.fm]({}): {:,} listeners, {:,} plays

tags: {}
'''

mod_note_exceeding_threshold: str = '{} exceeds {:,}.  Actual: {:,}.'
