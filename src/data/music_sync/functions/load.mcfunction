scoreboard objectives add music_sync.remaining dummy


schedule clear music_sync:second
schedule function music_sync:second 1s