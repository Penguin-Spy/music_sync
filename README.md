# Music Sync
Sync what specific background music is playing between all players!  

### Features
- All players in the same area (type of biome) will hear the same background music at the same time.
- Otherwise identical functionality to vanilla Minecraft; all tracks play in the same places with the same frequency and the same volume.
- The music volume slider still controls the in-game music volume.

### Usage
- Download the datapack & resourcepack from [Modrinth](https://modrinth.com/datapack/music_sync/version/latest), or the [latest GitHub release](https://github.com/Penguin-Spy/music_sync/releases/latest).
- Add the datapack to your world, and enable the resourcepack (or set it as the server resource pack).

All players must have the resourcepack loaded to hear the synced music. Players without the resourcepack will still hear vanilla music.  
This datapack/resourcepack is intended to be used with vanilla Minecraft 1.20.1. Compatability with other datapacks, mods, or resourcepacks is not garunteed; in particular you will almost definetly not hear any new music tracks added by other things, and no music will play in custom biomes/dimensions.

### Technical details
This datapack uses [beet](https://github.com/mcbeet/beet "The Minecraft pack development kit.") to automatically generate sounds.json entries & functions for every track & sound event used by each biome in the vanilla game.  
It works by replacing all vanilla music sound events with empty arrays (so no sounds play), then creating a new sound event for each individual track, and finally re-implements the logic for when to play each track such that all players with the same conditions get the same track.

# License
Copyright © Penguin_Spy 2023  

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.
