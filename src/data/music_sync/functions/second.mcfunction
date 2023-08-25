# count down the remaining time
scoreboard players remove @a[scores={music_sync.remaining=1..}] music_sync.remaining 1

# clear the remaining time when players rejoin (on dimension change is done via advancements)
scoreboard players reset @a[scores={music_sync.leave_game=1..}] music_sync.remaining
scoreboard players reset @a[scores={music_sync.leave_game=1..}] music_sync.leave_game

# toggle 'Now playing' display for players who ran the trigger
execute as @a[scores={toggle_now_playing=1..}] run function music_sync:toggle_now_playing

# start a new track every sunrise/sunset (even in other dimensions)
execute store result score $daytime music_sync.track run time query daytime
execute if score $daytime music_sync.track matches 0..19 run function music_sync:start_music
execute if score $daytime music_sync.track matches 12000..12019 run function music_sync:start_music

schedule function music_sync:second 1s