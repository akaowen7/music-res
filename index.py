import spotipy
from spotipy.oauth2 import SpotifyOAuth
from creds import creds

import json

import interactions
from interactions import slash_option, slash_command, SlashContext, Intents, listen
from interactions import ActionRow, Button, ButtonStyle
from interactions.api.events import MessageCreate
from interactions.ext.events import Component


bot = interactions.Client(intents=Intents.DEFAULT | Intents.MESSAGE_CONTENT)

scope = "user-library-read"

sp = spotipy.Spotify(
  auth_manager=SpotifyOAuth(
    scope=scope, 
    client_id=creds["clientID"], 
    client_secret=creds["clientSecret"], 
    redirect_uri=creds["redirect"]
  )
)

@slash_command(name="rec", description="Adds a song to the playlist")
@slash_option(name="song", description="The song to add", opt_type=interactions.OptionType.STRING, required=True)
async def rec(ctx: SlashContext, song: str):
  await ctx.respond(song)

@listen()
async def message(event: MessageCreate):
  m = event.message

  if m.author.id == bot.user.id:
    return
  if event.message.channel.id != 862165156518821888:
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
      await m.channel.send(f"Couldn't find anything for `{song}` by `{artist}`")
      return
    
    components: list[ActionRow] = [
    ActionRow(
      Button(
        style=ButtonStyle.GREEN,
        label="Yes",
      ),
      Button(
        style=ButtonStyle.RED,
        label="Go Away",
      )
    )
    ]
    await m.channel.send(f"Couldn't find **{song}** by **{artist}**\nI did find **{result['tracks']['items'][0]['name']}** by **{result['tracks']['items'][0]['artists'][0]['name']}**\nis that what you meant?", 
                         components=components)
    return
  
  print(result["tracks"]["items"][0]["name"])

@listen(Component)
async def on_component(event: Component):
  ctx = event.ctx
  
def add_to_list(song: str):
  p = sp.playlist()

bot.start(creds["discord"])