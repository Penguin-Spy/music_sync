from beet import Context, SoundConfig
from beet.contrib.vanilla import Vanilla

# Replaces the vanilla music sound events with empty sounds arrays
# Doesn't touch the credits, dragon fight, or menu music
def beet_default(ctx: Context):
  vanilla = ctx.inject(Vanilla)
  vanilla_sounds_path = vanilla.releases[ctx.minecraft_version].object_mapping["assets/minecraft/sounds.json"]
  vanilla_sounds = SoundConfig(source_path=vanilla_sounds_path)

  sounds = {}
  for event_id in vanilla_sounds.data.keys():
    if not event_id.startswith("music."): continue
    if event_id == "music.credits" or event_id == "music.dragon" or event_id == "music.menu": continue
    sounds[event_id] = {
      "replace": True,
      "sounds": []
    }

  ctx.assets["minecraft"].sound_config = SoundConfig(sounds)


