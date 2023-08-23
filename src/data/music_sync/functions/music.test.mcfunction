scoreboard players set $max music_sync.track 4

execute unless score {ID} music_sync.track matches -1.. summon minecraft:area_effect_cloud run function music_sync:get_random
execute unless score {ID} music_sync.track matches -1.. run scoreboard players operation {ID} music_sync.track = $random music_sync.track

execute if score {ID} music_sync.track matches 0 run say track 0
execute if score {ID} music_sync.track matches 1 run say track 1
execute if score {ID} music_sync.track matches 2 run say track 2
execute if score {ID} music_sync.track matches 3 run say track 3