from beet import Context, Function

def generate_tracks(ctx: Context):
    ctx.data["music_sync:hello"] = Function(["say hello"] * 5, tags=["minecraft:load"])