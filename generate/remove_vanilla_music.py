from beet import Context, SoundConfig, JsonFile
from generate.get_vanilla_sounds_json import get_vanilla_sounds

exclude_events = JsonFile(source_path="generate/groups.json").data["exclude_groups"]

# Replaces the vanilla music sound events with empty sounds arrays
# Doesn't touch excluded events
def beet_default(ctx: Context):
  ctx.require(get_vanilla_sounds)
  vanilla_sounds = ctx.meta["vanilla_sounds_json"]

  sounds = {}
  for event_id in vanilla_sounds.data.keys():
    if not event_id.startswith("music."): continue
    if event_id in exclude_events: continue
    sounds[event_id] = {
      "replace": True,
      "sounds": []
    }

  ctx.assets["minecraft"].sound_config = SoundConfig(sounds)


