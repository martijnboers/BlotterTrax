submission_exceeding_threshold: str = '''
All apologies /u/{} but your post has been automatically removed because the artist has too many {}. The maximum is {:,}, this link has {:,}.
If you think this is in error, please [contact the mods](https://www.reddit.com/message/compose?to=/r/listentothis&subject=Post+removed+in+error.&message=https://redd.it/{}). 

If you're new to the subreddit, please read the full list of removal reasons.

_Don't blame me,_ [_I'm just a bot_](https://www.youtube.com/watch?v=jqaweMZv4Og)|[_Bugs & Code_](https://github.com/martijnboers/BlotterTrax)
'''

submission_missing_discussion_tag: str = '''
All apologies /u/{} but your post has been automatically removed because it is a text post without the [Discussion] tag 

If you're new to the subreddit, please read the full list of removal reasons.

_Don't blame me,_ [_I'm just a bot_](https://www.youtube.com/watch?v=jqaweMZv4Og)|[_Bugs & Code_](https://github.com/martijnboers/BlotterTrax)
'''

cant_find_artist: str = '''
Can't find the artist on last.fm or artists doesn't have a description.

Make sure you spelled it right or if you can; add this artist to last.fm

_Don't blame me,_ [_I'm just a bot_](https://www.youtube.com/watch?v=jqaweMZv4Og)|[_Bugs & Code_](https://github.com/martijnboers/BlotterTrax)
'''

reply_with_last_fm_info: str = '''
**{}**

> {}

[last.fm]({}): {:,} listeners, {:,} plays

tags: {}
'''