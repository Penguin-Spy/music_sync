from beet import Context, SoundConfig
from beet.contrib.vanilla import Vanilla

def get_vanilla_sounds(ctx: Context):
  vanilla = ctx.inject(Vanilla)
  vanilla_sounds_path = vanilla.releases[ctx.minecraft_version].object_mapping["assets/minecraft/sounds.json"]
  ctx.meta["vanilla_sounds_json"] = SoundConfig(source_path=vanilla_sounds_path)
