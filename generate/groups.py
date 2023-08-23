from beet import Context, Function, SoundConfig, JsonFile
from beet.contrib.vanilla import Vanilla

# mapping of sound event -> condition for it to play
groups_cfg = JsonFile(source_path="generate/groups.json").data

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

# convert the groups list to a function that plays a random track from the vanilla sounds.json, and generates music_sync:player_start_music with the proper conditions for playing each group
def beet_default(ctx: Context):
  vanilla = ctx.inject(Vanilla)
  vanilla_sounds_path = vanilla.releases[ctx.minecraft_version].object_mapping["assets/minecraft/sounds.json"]
  vanilla_sounds = SoundConfig(source_path=vanilla_sounds_path)

  groups = {}
  for event_id in vanilla_sounds.data.keys():
    if not event_id.startswith("music."): continue
    if event_id == "music.credits" or event_id == "music.dragon" or event_id == "music.menu": continue

    groups[event_id] = sounds_to_tracks(event_id, vanilla_sounds.data)

  start_music_cmds = [
    "say player_start_music",
    "tag @s remove music_sync.played_track"
  ]
  for event_id, tracks in groups.items():
    print(f"{event_id}: {', '.join(tracks)}")

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
    if event_id in groups_cfg.keys():
      start_music_cmds.append(f"execute unless entity @s[tag=music_sync.played_track] if {groups_cfg[event_id]} run function music_sync:group/{event_id}")
    else:
      start_music_cmds.append(f"# execute unless entity @s[tag=music_sync.played_track] if ??? run function music_sync:group/{event_id}")

  ctx.data.functions[f"music_sync:player_start_music"] = Function(start_music_cmds)
