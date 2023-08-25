# count down the remaining time
scoreboard players remove @a[scores={music_sync.remaining=1..}] music_sync.remaining 1

# clear the remaining time when players rejoin (on dimension change is done via advancements)
scoreboard players reset @a[scores={music_sync.leave_game=1..}] music_sync.remaining
scoreboard players reset @a[scores={music_sync.leave_game=1..}] music_sync.leave_game

# start a new track every 10 minutes (TODO: sync this to the day/night cycle)
scoreboard players add $timer music_sync.track 1
execute if score $timer music_sync.track matches 600.. run function music_sync:start_music

schedule function music_sync:second 1s