# keeps track of players' remaining time on soundtracks
scoreboard objectives add music_sync.remaining dummy

# keeps track of the selected soundtrack to play for each group
scoreboard objectives add music_sync.track dummy


schedule clear music_sync:second
schedule function music_sync:second 1s