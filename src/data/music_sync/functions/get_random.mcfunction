execute store result score $random music_sync.track run data get entity @s UUID[0] 1
scoreboard players operation $random music_sync.track %= $max music_sync.track
kill @s