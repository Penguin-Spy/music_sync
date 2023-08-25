# Copyright © Penguin_Spy 2023
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from beet import Context, SoundConfig
from beet.contrib.vanilla import Vanilla

def get_vanilla_sounds(ctx: Context):
  vanilla = ctx.inject(Vanilla)
  vanilla_sounds_path = vanilla.releases[ctx.minecraft_version].object_mapping["assets/minecraft/sounds.json"]
  ctx.meta["vanilla_sounds_json"] = SoundConfig(source_path=vanilla_sounds_path)
