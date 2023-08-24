# keeps track of players' remaining time on soundtracks
scoreboard objectives add music_sync.remaining dummy
# keeps track of the selected soundtrack to play for each group
scoreboard objectives add music_sync.track dummy
# detects when a player leaves (to reset their remaining time bc music stops)
scoreboard objectives add music_sync.leave_game minecraft.custom:minecraft.leave_game

schedule clear music_sync:second
schedule function music_sync:second 1s