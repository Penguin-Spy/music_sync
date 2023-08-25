# Copyright © Penguin_Spy 2023
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from beet import Context, Function, Language, SoundConfig, JsonFile
from generate.get_vanilla_sounds_json import get_vanilla_sounds
import toml

# mapping of path -> track title
# last item of path is used as the id
tracks_cfg = JsonFile(source_path="generate/tracks.json").data

exclude_events = toml.load("generate/events.toml")["exclude_events"]

# Convert the tracks list to sound events and functions to /playsound & /title them
def beet_default(ctx: Context):
  ctx.require(get_vanilla_sounds)
  vanilla_sounds = ctx.meta["vanilla_sounds_json"]

  # parse volumes from each usage of all tracks
  track_volumes = {}
  for event_id, event in vanilla_sounds.data.items():
    if not event_id.startswith("music."): continue
    if event_id in exclude_events: continue

    for sound in event["sounds"]:
      if "type" in sound.keys() and sound["type"] == "event": continue  # ignore references
      else:
        if sound["name"] not in tracks_cfg.keys():
          raise ReferenceError("'" + sound["name"] + "' is not defined in the tracklist, but is referenced by '" + event_id + "'")

        if sound["name"] not in track_volumes.keys(): # ensure entry exists
          track_volumes[sound["name"]] = {}
        track = track_volumes[sound["name"]]

        volume = sound["volume"] if "volume" in sound.keys() else 1.0
        if volume in track:  # tally volume occurance
          track[volume] += 1
        else:
          track[volume] = 1

  # validate that all usages use a matching volume (if not, it's a bug that Mojang has to fix)
  for track, volumes in track_volumes.items():
    if len(volumes) > 1:
      print(f"[warn] '{track}' uses inconsistent volume: {volumes}, selecting {max(volumes, key=volumes.get)}")
  # choose the most common volume usage (arbitrary if equal)
  track_volumes = {track: max(volumes, key=volumes.get) for track, volumes in track_volumes.items()}

  # validate tracklist doesn't contain extra entries
  for track_path in tracks_cfg.keys():
    if track_path not in track_volumes:
      print(f"[warn] configured track '{track_path}' is not referenced by any sound events!")


  # generate sounds.json entry and track function using defined length & title, and calculated volume
  sounds = {}
  for path, volume in track_volumes.items():
    track_id = path.split("/")[-1]  # just use the filename of the path as the track_id
    title, length_str = tracks_cfg[path]
    mins, secs = length_str.split(":")
    length = (int(mins) * 60) + int(secs) + 10  # wait at least 10 seconds after each track

    # playsound music_sync:track.ID
    sounds[f"track.{track_id}"] = {
      "sounds": [{
        "name": path,
        "stream": True
      }]
    }
    if volume != 1.0:
      sounds[f"track.{track_id}"]["sounds"][0]["volume"] = volume

    # function music_sync:track/ID
    ctx.data.functions[f"music_sync:track/{track_id}"] = Function([
      f'playsound music_sync:track.{track_id} music @s',
      'title @s[tag=music_sync.show_now_playing] actionbar {"translate":"record.nowPlaying","with":[{"text":"' + title + '"}],"color":"light_purple"}',
      f'scoreboard players set @s music_sync.remaining {length}'
    ])

  ctx.assets["music_sync"].sound_config = SoundConfig(sounds)
