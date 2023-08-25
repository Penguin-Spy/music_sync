from beet import Context, Function, Language, SoundConfig, JsonFile

# mapping of path -> track title
# last item of path is used as the id
tracks_cfg = JsonFile(source_path="generate/tracks.json").data

# Convert the tracks list to sound events, a lang file, and functions to /playsound and /title them
def beet_default(ctx: Context):
  lang = {}
  sounds = {}
  longest_track = {
    "length": -1
  }
  for path, (title, length_str) in tracks_cfg.items():
    track_id = path.split("/")[-1]  # just use the filename of the path as the track_id
    mins, secs = length_str.split(":")
    length = (int(mins) * 60) + int(secs) + 10  # wait at least 10 seconds after each track
    if length > longest_track["length"] and not track_id == "end":
      longest_track = {
        "id": track_id,
        "length": length,
        "length_str": length_str
      }

    # {"translate": "music_sync.track.ID"}
    lang[f"music_sync.track.{track_id}"] = title

    # playsound music_sync:track.ID
    sounds[f"track.{track_id}"] = {
      "sounds": [{
        "name": path,
        "stream": True
      }]
    }

    # function music_sync:track/ID
    ctx.data.functions[f"music_sync:track/{track_id}"] = Function([
      f'playsound music_sync:track.{track_id} music @s',
      'title @s actionbar {"translate":"record.nowPlaying","with":[{"translate":"music_sync.track.' + track_id + '"}],"color":"light_purple"}',
      f'scoreboard players set @s music_sync.remaining {length}'
    ])

  ctx.assets["music_sync:en_us"] = Language(lang)
  ctx.assets["music_sync"].sound_config = SoundConfig(sounds)

  print("[info] longest track: " + longest_track["id"] + " (" + longest_track["length_str"] +")")
