# reset the selected track for each group (also resets the timer (& randomization variables))
scoreboard players reset * music_sync.track

# play a new track for each player whose current track has completed (or has no score for music_sync.remaining)
execute as @a unless score @s music_sync.remaining matches 1.. at @s run function music_sync:player_start_music