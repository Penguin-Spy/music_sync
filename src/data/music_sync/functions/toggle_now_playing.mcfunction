# re-enable the trigger
scoreboard players reset @s toggle_now_playing
scoreboard players enable @s toggle_now_playing

# swap the tag (with temp tag intermediary)
tag @s[tag=music_sync.show_now_playing] add music_sync.temp.remove_now_playing
tag @s[tag=!music_sync.show_now_playing] add music_sync.show_now_playing
tag @s[tag=music_sync.temp.remove_now_playing] remove music_sync.show_now_playing
tag @s[tag=music_sync.temp.remove_now_playing] remove music_sync.temp.remove_now_playing

# and show current status msg
tellraw @s[tag=music_sync.show_now_playing] {"translate":"music_sync.toggle_now_playing.enabled", "color": "green"}
tellraw @s[tag=!music_sync.show_now_playing] {"translate":"music_sync.toggle_now_playing.disabled", "color": "red"}