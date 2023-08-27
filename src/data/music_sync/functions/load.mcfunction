# Copyright © Penguin_Spy 2023
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# keeps track of players' remaining time on soundtracks
scoreboard objectives add music_sync.remaining dummy
# keeps track of the selected soundtrack to play for each event
scoreboard objectives add music_sync.track dummy
# detects when a player leaves (to reset their remaining time bc music stops)
scoreboard objectives add music_sync.leave_game minecraft.custom:minecraft.leave_game

scoreboard objectives add toggle_now_playing trigger {"translate":"music_sync.toggle_now_playing", "fallback": "toggle 'Now playing' display for music sync"}
scoreboard players enable * toggle_now_playing

# Display install notice & license thingy on new install/version change
execute unless score $version music_sync.remaining matches 100 run tellraw @a {"text":"Music Sync (v1.0) for Minecraft 1.20.1 is installed!", "color":"green"}
execute unless score $version music_sync.remaining matches 100 run tellraw @a ["This datapack is licensed under the ",{"text":"Mozilla Public License, v. 2.0","underlined":true,"color":"blue","clickEvent":{"action":"open_url","value":"http://mozilla.org/MPL/2.0/"},"hoverEvent":{"action":"show_text","contents":["http://mozilla.org/MPL/2.0/"]}},"."]
execute unless score $version music_sync.remaining matches 100 run tellraw @a ["The Source Code Form is available at ",{"text":"Penguin-Spy/music_sync","underlined":true,"color":"blue","clickEvent":{"action":"open_url","value":"https://github.com/Penguin-Spy/music_sync"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Penguin-Spy/music_sync"]}},"."]
execute unless score $version music_sync.remaining matches 100 run tellraw @a ["Use ",{"text":"/trigger toggle_now_playing","color":"gray","clickEvent":{"action":"run_command","value":"/trigger toggle_now_playing"},"hoverEvent":{"action":"show_text","contents":["Click to run"]}}," to toggle the 'Now playing' display."]
scoreboard players set $version music_sync.remaining 100

schedule clear music_sync:second
schedule function music_sync:second 1s