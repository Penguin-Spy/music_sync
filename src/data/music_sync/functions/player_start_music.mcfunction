# ran as each player who's music_sync.remaining score is 0 every 5 minutes
say start music

# nether
#basalt_deltas
execute if biome ~ ~ ~ minecraft:basalt_deltas run function music_sync:music/nether/basalt_deltas
#nether_wastes
#soul_sand_valley
#warped_forest

# overworld
execute if biome ~ ~ ~ #minecraft:is_badlands run function music_sync:music/overworld/badlands
#bamboo_jungle
#cherry_grove
#deep_dark
#desert
#dripstone_caves
#flower_forest
#forest
#frozen_peaks
#grove
#jagged_peaks
#jungle
#lush_caves
#meadow
#old_growth_taiga
#snowy_slopes
#sparse_jungle
#stony_peaks
#swamp
#
#

# extra
#under_water