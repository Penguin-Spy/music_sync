scoreboard players remove @a[scores={music_sync.remaining=1..}] music_sync.remaining 1

# start a new track every 5 minutes (TODO: sync this to the day/night cycle)
scoreboard players add $timer music_sync.remaining 1
execute if score $timer music_sync.remaining matches 300.. run function music_sync:start_music

schedule function music_sync:second 1s