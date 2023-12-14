import spotipy
from spotipy.oauth2 import SpotifyOAuth
from creds import creds

import time
import json
import asyncio

import interactions
from interactions import slash_option, slash_command, SlashContext, Intents, listen
from interactions import ActionRow, Button, ButtonStyle
from interactions.api.events import MessageCreate
from interactions.api.events import Component


bot = interactions.Client(intents=Intents.DEFAULT | Intents.MESSAGE_CONTENT)

scope = ["user-library-read", "playlist-modify-public", "playlist-modify-private", "playlist-read-private"]

sp = spotipy.Spotify(
  auth_manager=SpotifyOAuth(
    scope=scope, 
    client_id=creds["clientID"], 
    client_secret=creds["clientSecret"], 
    redirect_uri=creds["redirect"]
  )
)

async def add_to_list(song, ctx):
  print(song["uri"])
  sp.playlist_add_items(creds["playlistID"], [song["uri"]])

  component = Button(
    style=ButtonStyle.RED,
    label="Undo",
    custom_id=f"del {song['uri']}",
  )

  m = await ctx.channel.send(
    f"Added **{song['name']}** by **{', '.join([i['name'] for i in song['artists']])}** to the playlist",
    components=component)
  
  await asyncio.sleep(30)
  try:
    await m.delete()
  except:
    pass

@listen()
async def message(event: MessageCreate):
  m = event.message

  if m.author.id == bot.user.id:
    return
  if event.message.channel.id != 862165156518821888 and event.message.channel.id != 1032416666577023107:
    return
  if "-" not in m.content:
    return
  
  split = m.content.split("-")
  song = split[0].strip()
  artist = split[1].strip()

  result = sp.search(q=f"track:\"{song}\" artist:\"{artist}\"", type="track", limit=1)

  if result["tracks"]["total"] == 0:

    result = sp.search(q=song, type="track", limit=1)

    if result["tracks"]["total"] == 0:
      m2 = await m.channel.send(f"Couldn't find anything for **{song}** by **{artist}**")
      await asyncio.sleep(30)
      try:
        await m2.delete()
      except:
        pass
      return
    
    result = result['tracks']['items'][0]
    
    components: list[ActionRow] = [
    ActionRow(
      Button(
        style=ButtonStyle.GREEN,
        label="Yes",
        custom_id=f"add {result['uri']}",
      ),
      Button(
        style=ButtonStyle.RED,
        label="Go Away",
        custom_id=f"nvm {result['uri']}",
      )
    )
    ]
    m2 = await m.channel.send(
      f"Couldn't find **{song}** by **{artist}**\nI did find **{result['name']}** by **{', '.join([i['name'] for i in result['artists']])}**\nis that what you meant?", 
      components=components)
    
    await asyncio.sleep(30)
    try:
      await m2.delete()
    except:
      pass
    return
  
  await add_to_list(result["tracks"]["items"][0], m)

@listen(Component)
async def on_component(event: Component):
  ctx = event.ctx

  match ctx.custom_id[:3]:
    case "del":
      sp.playlist_remove_all_occurrences_of_items(creds["playlistID"], [ctx.custom_id[4:]])
      m = await ctx.message.edit(content="Removed!", components=[])
      await asyncio.sleep(1.5)
      await m.delete()
    case "add":
      await ctx.message.delete()
      await add_to_list(sp.track(ctx.custom_id[4:]), ctx)
    case "nvm":
      await ctx.message.delete()

bot.start(creds["discord"])