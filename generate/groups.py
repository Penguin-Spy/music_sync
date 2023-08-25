from beet import Context, Function, JsonFile
from beet.contrib.vanilla import Vanilla
from beet.contrib.worldgen import WorldgenBiome, WorldgenBiomeTag
from generate.get_vanilla_sounds_json import get_vanilla_sounds

groups_cfg = JsonFile(source_path="generate/groups.json").data
# mapping of sound event -> condition for it to play
group_conditions = groups_cfg["conditions"]

DEFAULT_GROUP = "music.game"

defined_tracks = JsonFile(source_path="generate/tracks.json").data.keys()
referenced_tracks = set()

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
      referenced_tracks.add(sound["name"])
      if sound["name"] not in defined_tracks:
        raise ReferenceError("'" + sound["name"] + "' is not defined in the tracklist, but is referenced by '" + event_id + "'")

  return out


def create_group_trigger(ctx, event_id, condition, tracks):
  if len(tracks) == 0:
    print(f"[info] skipping trigger for '{event_id}' because it contains 0 tracks")
    return

  # function music_sync:group/ID
  cmds = [
    "tag @s add music_sync.played_track",
    f"scoreboard players set $max music_sync.track {len(tracks)}",
    f"execute unless score {event_id} music_sync.track matches -1.. summon minecraft:marker run function music_sync:get_random",
    f"execute unless score {event_id} music_sync.track matches -1.. run scoreboard players operation {event_id} music_sync.track = $random music_sync.track"
  ]
  for i, track_id in enumerate(tracks):
    cmds.append(f"execute if score {event_id} music_sync.track matches {i} run function music_sync:track/{track_id}")

  ctx.data.functions[f"music_sync:group/{event_id}"] = Function(cmds)

  # function music_sync:player_start_music
  if condition:
    return f"execute unless entity @s[tag=music_sync.played_track] if {condition} run function music_sync:group/{event_id}"
  else:
    return f"# no condition for function music_sync:group/{event_id}"

order = groups_cfg["order"]
sort_after = len(order)
def sort_by_cfg(item):
  for i, v in enumerate(order): # return the index in the order list the first matching prefix appears at
    if item.startswith(v):
      return i
  return sort_after # or a value larger than any index in the order list to force it after if no prefix matches


# convert the groups list to a function that plays a random track from the vanilla sounds.json,
# parses the default worldgen to determine which biomes play which music sound events,
# and generates music_sync:player_start_music with the proper conditions for playing each group
def beet_default(ctx: Context):
  vanilla = ctx.inject(Vanilla)
  ctx.require(get_vanilla_sounds)
  vanilla_sounds = ctx.meta["vanilla_sounds_json"]

  group_tracks = {}
  group_trigger_biomes = {}
  # parse sounds.json to create a mapping of event_id -> array of tracks that play
  for event_id in vanilla_sounds.data.keys():
    if not event_id.startswith("music."): continue
    if event_id in groups_cfg["exclude_groups"]: continue

    group_tracks[event_id] = sounds_to_tracks(event_id, vanilla_sounds.data)
    group_trigger_biomes[event_id] = []

  # validate tracklist stuff
  for track_path in defined_tracks:
    if track_path not in referenced_tracks:
      print(f"[warn] '{track_path}' is not referenced by any sound events!")

  # parse default worldgen to get a list of which biomes play which music sound events
  biomes = vanilla.mount("data/minecraft/worldgen/biome").data["minecraft"][WorldgenBiome]
  for biome_id, biome in biomes.items():
    if f"minecraft:{biome_id}" in groups_cfg["exclude_biomes"]: continue
    biome_effects = biome.data["effects"]
    if "music" in biome_effects.keys():
      event_id = biome_effects["music"]["sound"]
      if event_id.startswith("minecraft:"):
        event_id = event_id[10:]
      group_trigger_biomes[event_id].append(biome_id)
    else:
      group_trigger_biomes[DEFAULT_GROUP].append(biome_id)

  # generate a tag & condition for each music group
  for event_id, biomes in group_trigger_biomes.items():
    if not event_id in group_conditions.keys():
      if len(biomes) > 1:
        ctx.data[f"music_sync:{event_id}"] = WorldgenBiomeTag({
          "values": [f"minecraft:{biome}" for biome in biomes]
        })
        group_conditions[event_id] = f"biome ~ ~ ~ #music_sync:{event_id}"
      elif len(biomes) > 0:
        group_conditions[event_id] = f"biome ~ ~ ~ minecraft:{biomes[0]}"
      else:
        print(f"[warn] no biomes trigger event '{event_id}' & no trigger specified. event will not play")
    else:
      if len(biomes) > 0:
        print(f"[warn] using specified condition for '{event_id}' ('{group_conditions[event_id]}') even though '{biomes}' trigger it")

  # parse each group to create the group function & add its condition to music_sync:player_start_music
  start_music_cmds = [
    "say player_start_music",
    "tag @s remove music_sync.played_track"
  ]

  # generate manual conditions first
  for event_id in sorted(group_conditions, key=sort_by_cfg):
    cmd = create_group_trigger(ctx, event_id, group_conditions[event_id], group_tracks[event_id])
    if cmd:
      start_music_cmds.append(cmd)

  ctx.data.functions[f"music_sync:player_start_music"] = Function(start_music_cmds)
