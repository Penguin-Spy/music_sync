# Copyright © Penguin_Spy 2023
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from beet import Context, Function, JsonFile
from beet.contrib.vanilla import Vanilla
from beet.contrib.worldgen import WorldgenBiome, WorldgenBiomeTag
from generate.get_vanilla_sounds_json import get_vanilla_sounds
import toml

events_cfg = toml.load("generate/events.toml")
# mapping of sound event -> condition for it to play
event_conditions = events_cfg["conditions"]

DEFAULT_EVENT = "music.game"

# takes a list of sound event definitions (`name:"path/to/sound"`) and converts it to a list of tracks, plus the total weight of all the sounds
def sounds_to_tracks(sounds):
  total_weight = 0
  tracks = []
  for sound in sounds:
    weight = sound["weight"] if "weight" in sound.keys() else 1
    total_weight += weight

    track = {
      "name": sound["name"].split("/")[-1],  # just use the filename of the path as the track_id
      "type": "event" if "type" in sound.keys() and sound["type"] == "event" else "track",
      "weight": sound["weight"] if "weight" in sound.keys() else 1
    }
    tracks.append(track)

  return tracks, total_weight

# creates the event function (music_sync:event/ID)
def create_event(ctx, event_id, tracks, total_weight):
  cmds = [
    "tag @s add music_sync.played_track"
  ]
  if len(tracks) > 1: # only generate a randomizer if there's more than one track
    cmds.extend([
      f"scoreboard players set $max music_sync.track {total_weight}",
      f"execute unless score {event_id} music_sync.track matches -1.. summon minecraft:marker run function music_sync:get_random",
      f"execute unless score {event_id} music_sync.track matches -1.. run scoreboard players operation {event_id} music_sync.track = $random music_sync.track"
    ])
    weight_used = 0 # keep track of how much of the total weight has been used
    for track in tracks:
      weight = track['weight']
      weight_str = f"{weight_used}" if weight == 1 else f"{weight_used}..{weight_used + weight - 1}"
      weight_used += weight
      cmds.append(f"execute if score {event_id} music_sync.track matches {weight_str} run function music_sync:{track['type']}/{track['name']}")
  else:
    cmds.append(f"function music_sync:{tracks[0]['type']}/{tracks[0]['name']}")

  ctx.data.functions[f"music_sync:event/{event_id}"] = Function(cmds)


order = events_cfg["order"]
sort_after = len(order)
def sort_by_cfg(item):
  for i, v in enumerate(order): # return the index in the order list the first matching prefix appears at
    if item.startswith(v):
      return i
  return sort_after # or a value larger than any index in the order list to force it after if no prefix matches


# convert the music sound events list to a function that plays a random track from the vanilla sounds.json,
# parses the default worldgen to determine which biomes play which music sound events,
# and generates music_sync:player_start_music with the proper conditions for playing each event
def beet_default(ctx: Context):
  vanilla = ctx.inject(Vanilla)
  ctx.require(get_vanilla_sounds)
  vanilla_sounds = ctx.meta["vanilla_sounds_json"].data

  # parse default worldgen to get a list of which biomes play which music sound events
  event_trigger_biomes = {
    DEFAULT_EVENT: []
  }
  biomes = vanilla.mount("data/minecraft/worldgen/biome").data["minecraft"][WorldgenBiome]
  for biome_id, biome in biomes.items():
    if f"minecraft:{biome_id}" in events_cfg["exclude_biomes"]: continue
    biome_effects = biome.data["effects"]
    if "music" in biome_effects.keys():
      event_id = biome_effects["music"]["sound"]
      if event_id.startswith("minecraft:"):
        event_id = event_id[10:]
      if event_id not in event_trigger_biomes.keys():
        event_trigger_biomes[event_id] = []
      event_trigger_biomes[event_id].append(biome_id)
    else:
      event_trigger_biomes[DEFAULT_EVENT].append(biome_id)

  # generate a tag & condition for each music event
  for event_id, biomes in event_trigger_biomes.items():
    if event_id not in event_conditions.keys():
      if len(biomes) > 1: # generate tag & condition that uses the tag
        ctx.data[f"music_sync:{event_id}"] = WorldgenBiomeTag({
          "values": [f"minecraft:{biome}" for biome in biomes]
        })
        event_conditions[event_id] = f"biome ~ ~ ~ #music_sync:{event_id}"
      else: # just directly check the biome
        event_conditions[event_id] = f"biome ~ ~ ~ minecraft:{biomes[0]}"
    else:
      if len(biomes) > 0:
        print(f"[warn] using specified condition for '{event_id}' ('{event_conditions[event_id]}') even though '{biomes}' trigger it")

  # validate no events were left behind
  for event_id in vanilla_sounds.keys():
    if not event_id.startswith("music."): continue
    if event_id in events_cfg["exclude_events"]: continue
    if event_id not in event_conditions.keys():
      print(f"[warn] no biomes trigger event '{event_id}' & no trigger specified. event will not play")

  # parse each event to create the event function & add its condition to music_sync:player_start_music
  start_music_cmds = [
    "tag @s remove music_sync.played_track"
  ]
  for event_id in sorted(event_conditions, key=sort_by_cfg):
    sounds = vanilla_sounds[event_id]["sounds"]
    tracks, total_weight = sounds_to_tracks(sounds)

    if len(tracks) == 0:
      print(f"[info] skipping trigger for '{event_id}' because it contains 0 tracks")
      continue

    # only generate function if one doesn't already exist
    if f"music_sync:event/{event_id}" in ctx.data.functions.keys():
      print(f"[info] using existing function for event/{event_id}")
    else:
      create_event(ctx, event_id, tracks, total_weight)

    # add line to music_sync:player_start_music
    start_music_cmds.append(f"execute unless entity @s[tag=music_sync.played_track] if {event_conditions[event_id]} run function music_sync:event/{event_id}")

  ctx.data.functions[f"music_sync:player_start_music"] = Function(start_music_cmds)
