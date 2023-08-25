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

# takes a list of sound event definitions (`name:"path/to/sound"`) and converts it to a list of track_ids
# handles event references
# ignores weights currently
def sounds_to_tracks(event_id, all_events):
  sounds = all_events[event_id]["sounds"]

  out = []
  for sound in sounds:
    if "type" in sound.keys() and sound["type"] == "event":  # recursively parse event references
      out.extend(sounds_to_tracks(sound["name"], all_events))
    else:
      out.append(sound["name"].split("/")[-1])  # just use the filename of the path as the track_id

  return out


def create_event_trigger(ctx, event_id, condition, tracks):
  if len(tracks) == 0:
    print(f"[info] skipping trigger for '{event_id}' because it contains 0 tracks")
    return

  # only generate function if one doesn't already exist
  if f"music_sync:event/{event_id}" in ctx.data.functions.keys():
    print(f"[info] using existing function for event/{event_id}")
  else:
    # function music_sync:event/ID
    cmds = [
      "tag @s add music_sync.played_track"
    ]
    if len(tracks) > 1: # only generate a randomizer if there's more than one track
      cmds.extend([
        f"scoreboard players set $max music_sync.track {len(tracks)}",
        f"execute unless score {event_id} music_sync.track matches -1.. summon minecraft:marker run function music_sync:get_random",
        f"execute unless score {event_id} music_sync.track matches -1.. run scoreboard players operation {event_id} music_sync.track = $random music_sync.track"
      ])
      for i, track_id in enumerate(tracks):
        cmds.append(f"execute if score {event_id} music_sync.track matches {i} run function music_sync:track/{track_id}")
    else:
      cmds.append(f"function music_sync:track/{tracks[0]}")

    ctx.data.functions[f"music_sync:event/{event_id}"] = Function(cmds)

  # add line to music_sync:player_start_music
  return f"execute unless entity @s[tag=music_sync.played_track] if {condition} run function music_sync:event/{event_id}"

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
  vanilla_sounds = ctx.meta["vanilla_sounds_json"]

  event_tracks = {}
  event_trigger_biomes = {}
  # parse sounds.json to create a mapping of event_id -> array of tracks that play
  for event_id in vanilla_sounds.data.keys():
    if not event_id.startswith("music."): continue
    if event_id in events_cfg["exclude_events"]: continue

    event_tracks[event_id] = sounds_to_tracks(event_id, vanilla_sounds.data)
    event_trigger_biomes[event_id] = []

  # parse default worldgen to get a list of which biomes play which music sound events
  biomes = vanilla.mount("data/minecraft/worldgen/biome").data["minecraft"][WorldgenBiome]
  for biome_id, biome in biomes.items():
    if f"minecraft:{biome_id}" in events_cfg["exclude_biomes"]: continue
    biome_effects = biome.data["effects"]
    if "music" in biome_effects.keys():
      event_id = biome_effects["music"]["sound"]
      if event_id.startswith("minecraft:"):
        event_id = event_id[10:]
      event_trigger_biomes[event_id].append(biome_id)
    else:
      event_trigger_biomes[DEFAULT_EVENT].append(biome_id)

  # generate a tag & condition for each music event
  for event_id, biomes in event_trigger_biomes.items():
    if not event_id in event_conditions.keys():
      if len(biomes) > 1:
        ctx.data[f"music_sync:{event_id}"] = WorldgenBiomeTag({
          "values": [f"minecraft:{biome}" for biome in biomes]
        })
        event_conditions[event_id] = f"biome ~ ~ ~ #music_sync:{event_id}"
      elif len(biomes) > 0:
        event_conditions[event_id] = f"biome ~ ~ ~ minecraft:{biomes[0]}"
      else:
        print(f"[warn] no biomes trigger event '{event_id}' & no trigger specified. event will not play")
    else:
      if len(biomes) > 0:
        print(f"[warn] using specified condition for '{event_id}' ('{event_conditions[event_id]}') even though '{biomes}' trigger it")


  # parse each event to create the event function & add its condition to music_sync:player_start_music
  start_music_cmds = [
    "tag @s remove music_sync.played_track"
  ]
  for event_id in sorted(event_conditions, key=sort_by_cfg):
    cmd = create_event_trigger(ctx, event_id, event_conditions[event_id], event_tracks[event_id])
    if cmd:
      start_music_cmds.append(cmd)

  ctx.data.functions[f"music_sync:player_start_music"] = Function(start_music_cmds)
