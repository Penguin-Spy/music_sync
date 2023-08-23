from beet import Context, Function, Language, SoundConfig
from beet.contrib.vanilla import Vanilla
from beet import SoundConfig

# path: title
# last item of path is used as the id
tracks = {
  "music/game/nuance1": "C418 - Key",
  "music/game/hal1":    "C418 - Subwoofer Lullaby",
  "music/game/hal2":    "C418 - Living Mice",
  "music/game/hal3":    "C418 - Haggstrom",
  "music/game/calm1":   "C418 - Minecraft",
  "music/game/nuance2": "C418 - Oxygène",
  "music/game/piano3":  "C418 - Mice on Venus",
  "music/game/piano1":  "C418 - Dry Hands",
  "music/game/piano2":  "C418 - Wet Hands",
  "music/game/calm2":   "C418 - Clark",
  "music/game/calm3":   "C418 - Sweeden",
  "music/game/hal4":    "C418 - Danny",

  "music/game/end/credits":        "C418 - Alpha",
  "music/game/nether/nether2":     "C418 - Dead Voxel",
  "music/game/creative/creative2": "C418 - Blind Spots",
  "music/menu/menu2":              "C418 - Moog City 2",
  "music/game/nether/nether1":     "C418 - Concrete halls",
  "music/game/creative/creative1": "C418 - Biome Fest",
  "music/menu/menu1":              "C418 - Mutation",
  "music/game/creative/creative3": "C418 - Haunt Muskie",
  "music/game/nether/nether3":     "C418 - Warmth",
  "music/menu/menu4":              "C418 - Floating Trees",
  "music/game/creative/creative4": "C418 - Aria Math",
  "music/game/nether/nether4":     "C418 - Ballad of the Cats",
  "music/game/creative/creative6": "C418 - Taswell",
  "music/menu/menu3":              "C418 - Beginning 2",
  "music/game/creative/creative5": "C418 - Dreiton",
  "music/game/end/end":            "C418 - The End",

  "music/game/water/axolotl":     "C418 - Axolotl",
  "music/game/water/dragon_fish": "C418 - Dragon Fish",
  "music/game/water/shuniji":     "C418 - Shuniji",

  "music/game/nether/crimson_forest/chrysopoeia": "Lena Raine - Chrysopoeia",
  "music/game/nether/nether_wastes/rubedo":       "Lena Raine - Rubedo",
  "music/game/nether/soulsand_valley/so_below":   "Lena Raine - So Below",

  "music/game/stand_tall":          "Lena Raine - Stand Tall",
  "music/game/left_to_bloom":       "Lena Raine - Left to Bloom",
  "music/game/ancestry":            "Lena Raine - Ancestry",
  "music/game/wending":             "Lena Raine - Wending",
  "music/game/infinite_amethyst":   "Lena Raine - Infinite Amethyst",
  "music/game/one_more_day":        "Lena Raine - One More Day",
  "music/game/floating_dream":      "Kumi Tanioka - Floating Dream",
  "music/game/comforting_memories": "Kumi Tanioka - Comforting Memories",
  "music/game/an_ordinary_day":     "Kumi Tanioka - An Ordinary Day",

  "music/game/swamp/firebugs":     "Lena Raine - Firebugs",
  "music/game/swamp/aerie":        "Lena Raine - Aerie",
  "music/game/swamp/labyrinthine": "Lena Raine - Labyrinthine",

  "music/game/echo_in_the_wind": "Aaron Cherof - Echo in the Wind",
  "music/game/a_familiar_room":  "Aaron Cherof - A Familiar Room",
  "music/game/bromeliad":        "Aaron Cherof - Bromeliad",
  "music/game/crescent_dunes":   "Aaron Cherof - Crescent Dunes"
}

# Convert the tracks list to sound events, a lang file, and functions to /playsound and /title them
def generate_tracks(ctx: Context):
  lang = {}
  sounds = {}
  for path, title in tracks.items():
    track_id = path.split("/")[-1]  # just use the filename of the path as the track_id

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
      'title @s actionbar {"translate":"record.nowPlaying","with":[{"translate":"music_sync.track.' + track_id + '"}],"color":"light_purple"}'
    ])

  ctx.assets["music_sync:en_us"] = Language(lang)
  ctx.assets["music_sync"].sound_config = SoundConfig(sounds)


# takes a list of sound event definitions (`name:"path/to/sound"`) and converts it to a list of track_ids
# handles event references
# ignores weights
def sounds_to_tracks(event_id, all_events):
  sounds = all_events[event_id]["sounds"]

  out = []

  for sound in sounds:
    if "type" in sound.keys() and sound["type"] == "event":  # recursively parse event references
      out.extend(sounds_to_tracks(sound["name"], all_events))
    else:
      out.append(sound["name"].split("/")[-1])  # just use the filename of the path as the track_id

  return out


def generate_groups(ctx: Context):
  vanilla = ctx.inject(Vanilla)

  vanilla_sounds_path = vanilla.releases[ctx.minecraft_version].object_mapping["assets/minecraft/sounds.json"]
  vanilla_sounds = SoundConfig(source_path=vanilla_sounds_path)

  groups = {}
  for event_id in vanilla_sounds.data.keys():
    if not event_id.startswith("music."): continue

    groups[event_id] = sounds_to_tracks(event_id, vanilla_sounds.data)

  for event_id, tracks in groups.items():
    print(f"{event_id}: {', '.join(tracks)}")

    # function music_sync:music/ID
    cmds = [
      f"scoreboard players set $max music_sync.track {len(tracks)}",
      f"execute unless score {event_id} music_sync.track matches -1.. summon minecraft:marker run function music_sync:get_random",
      f"execute unless score {event_id} music_sync.track matches -1.. run scoreboard players operation {event_id} music_sync.track = $random music_sync.track"
    ]
    for i, track_id in enumerate(tracks):
      cmds.append(f"execute if score {event_id} music_sync.track matches {i} run function music_sync:track/{track_id}")

    ctx.data.functions[f"music_sync:music/{event_id}"] = Function(cmds)
