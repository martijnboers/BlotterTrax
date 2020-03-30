
## BlotterTrax 
Reddit bot that uses streaming services to enforce popularity limits on new subreddit submissions, [see in action](https://www.reddit.com/user/fmfrequencyjammer/comments/).
  
## Motivation  
This project started to decrease the amount of popular music shared on [/r/listentothis](https://www.reddit.com/r/listentothis) and hereby encourage the sharing of undiscovered and underappreciated artists. This came to light after [a post](https://www.reddit.com/r/listentothis/comments/ensc7g/discussion_this_subreddit_has_a_major_popularity/) pointing out that recent top submissions are breaking the subreddit's rules.
  
## Build status  

![Python application](https://github.com/martijnboers/BlotterTrax/workflows/Python%20application/badge.svg)

  
## Built with  
 1. [PRAW](https://praw.readthedocs.io/en/latest/)
 2. [PyLast](https://github.com/pylast/pylast)  
  
  
## Installation
 1. Copy the config example to config.ini
 `cp conf/config.ini.dist conf/config.ini`
 2. Create API account on [Reddit](https://www.reddit.com/dev/api/), [Last.fm](https://www.last.fm/api/), [YouTube](https://developers.google.com/youtube/v3/getting-started) and [SoundCloud](https://developers.soundcloud.com/)
 3. Fill in the keys and passwords in the `config/config.ini` file
 4. Set `REMOVE_SUBMISSIONS` to true if you want to remove exceeding submission, otherwise it will create a rapport
 5. Set `SEND_ARTIST_REPLY` if you want the bot to reply with a last.fm artist bio
 6. Use Docker to build the image
 `docker build -t blottertrax .`
 7. Create a docker volume for the database
 `docker volume create blottertrax`
 8. Run the container with the volume attached
 `docker run --mount source=blottertrax,target=/usr/src/app/database blottertrax`

And that's it! If it doesn't work you can create an issue
  
## How to use?  
Please set the `SUBREDDIT` in `conf/config.ini` to select the desired subreddit to moderate. This only works when the Reddit account is moderator of the selected subreddit
  
## Contribute  
  
If you have features or bugfixes don't be shy to create a pull requests or bug report!
  
## Credits  

Thanks to:
  - [Nedlinin](https://github.com/Nedlinin)
  - [TcMaX](https://github.com/TcMaX)
  - Electronic music duo [BlotterTrax](https://www.discogs.com/artist/5340327-Blotter-Trax) for the name
  
## License  
You may copy, distribute and modify the software as long as you track changes/dates in source files. Any modifications to or software including (via compiler) GPL-licensed code must also be made available under the GPL along with build & install instructions.
  
GPL © [Martijn Boers](https://github.com/martijnboers)
