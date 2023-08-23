scoreboard players set $timer music_sync.remaining 0
say global start music

# reset the selected track for each group
scoreboard players reset * music_sync.track

execute as @a[scores={music_sync.remaining=0}] run function music_sync:player_start_music