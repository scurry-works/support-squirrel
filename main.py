# --- Environment setup ---
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("SUPPORT_TOKEN")
APPLICATION_ID = 1440875315608948899
GUILD_ID = 905167903224123473

OWNER_ID = 582648847881338961
VERIFY_CHANNEL_ID = 1440890196517326930
WELCOME_CHANNEL_ID = 1440890422481129546
DOWNLOADS_CHANNEL_ID = 1468694348517347624
ACORN_EMOJI_ID = 1400922547679264768
MEMBER_ROLE_ID = 1046627142345170984

import logging
from rich.logging import RichHandler

logger = logging.getLogger("scurrypy")

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(show_path=False, rich_tracebacks=True)],
)

from scurrypy import Client, Intents
from scurrypy.enums import EventType
from scurrypy.api.user import UserModel
from scurrypy.api.messages import MessagePart, Embed, EmbedThumbnail, EmbedImage, EmbedField, EmbedFooter
from scurrypy.events import ReactionAddEvent, GuildMemberAddEvent, ReadyEvent

from scurrypy.ext.events import EventsAddon
from scurrypy.ext.prefixes import PrefixAddon, PrefixCommandContext
from scurrypy.ext.cache import GuildEmojiCacheAddon, ApplicationEmojisCacheAddon

class BotUser:
    """Quick helper for fetching bot user on startup."""
    
    def __init__(self, client: Client):
        self.user: UserModel = None

        client.add_event_listener(EventType.READY, self.init_bot_user)

    async def init_bot_user(self, event: ReadyEvent):
        self.user = event.user

client = Client(
    token=TOKEN,
    intents=(
        Intents.DEFAULT | 
        Intents.MESSAGE_CONTENT | 
        Intents.GUILD_MEMBERS | 
        Intents.GUILD_MESSAGE_REACTIONS | 
        Intents.GUILD_EXPRESSIONS
    )
)

bot_user = BotUser(client)

events = EventsAddon(client)
prefixes = PrefixAddon(client, APPLICATION_ID, '!')

guild_emojis = GuildEmojiCacheAddon(client)
app_emojis = ApplicationEmojisCacheAddon(client, APPLICATION_ID)

@prefixes.listen('rules')
async def on_build_rules(ctx: PrefixCommandContext):
    
    if ctx.author.id != OWNER_ID:
        return
    
    flaming_acorn = app_emojis.get_emoji('flaming_acorn').mention

    embed = Embed(
        thumbnail=EmbedThumbnail("https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/rules_book.png"),
        description="Before we get started, let's establish some rules.",
        fields=[
            EmbedField(f"{flaming_acorn} Respect",
                "Please treat others with respect and be mindful of the things you say."),
            EmbedField(f"{flaming_acorn} Content",
                "No malicious or NSFW content, advertising, spam, or discussion of charged topics."),
            EmbedField(f"{flaming_acorn} Bot Policy",
                "If you have any questions, feel free to post it in <#1459655310150074368>."),
            EmbedField(f"{flaming_acorn} Warning Policy",
                "**Kick -> Mute -> Ban** is generally followed depending on severity.")
        ],
        footer=EmbedFooter("These rules are subject to change!", 
            "https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/alert.png")
    )

    embed.set_user_author(ctx.author)

    await ctx.send(MessagePart(embeds=[embed]))

@prefixes.listen('verify')
async def on_build_verify(ctx: PrefixCommandContext):
    if ctx.author.id != OWNER_ID:
        return
    if ctx.event.channel_id != VERIFY_CHANNEL_ID:
        return
    
    embed = Embed(
        title='Verify',
        thumbnail=EmbedThumbnail("https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/plus.png"),
        description="By reacting to this message, you agree to the rules."
    )

    embed.set_user_author(bot_user.user)

    await ctx.send(MessagePart(embeds=[embed]))

    await ctx.message.add_reaction(guild_emojis.get_emoji(ACORN_EMOJI_ID))

@events.listen(EventType.MESSAGE_REACTION_ADD)
async def on_verify(bot: Client, event: ReactionAddEvent):

    # if correct channel and emoji and NOT the bot...
    if event.channel_id != VERIFY_CHANNEL_ID:
        return
    if event.emoji.id != ACORN_EMOJI_ID:
        return
    if event.user_id == APPLICATION_ID:
        return

    # remove reaction
    msg = bot.message(event.channel_id, event.message_id)

    await msg.remove_user_reaction(guild_emojis.get_emoji(ACORN_EMOJI_ID), event.user_id)

    # add Member role to user
    guild = bot.guild(GUILD_ID)

    await guild.add_member_role(event.user_id, MEMBER_ROLE_ID)

@events.listen(EventType.GUILD_MEMBER_ADD)
async def on_welcome(bot: Client, event: GuildMemberAddEvent):
    channel = bot.channel(WELCOME_CHANNEL_ID)

    acorn = app_emojis.get_emoji('acorn').mention
    bullet = app_emojis.get_emoji('bullet').mention

    import random

    select_thumb = random.choice(['bookie', 'pirate', 'wizard'])

    embed = Embed(
        title=f"Welcome, {event.user.username}!",
        thumbnail=EmbedThumbnail(f"https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/{select_thumb}.png"),
        description=f"""
            {bullet} Read the rules in <#1046640388456321126>
            {bullet} Verify in <#1440890196517326930>
            {bullet} Hope you enjoy the bot!
        """,
        image=EmbedImage('https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/welcome.gif')
    )

    embed.set_user_author(bot)

    await channel.send(
        MessagePart(
            content=f"{acorn} <@{event.user.id}> *has stumbled upon a community of squirrels!* {acorn}",
            embeds=[embed]
        )
    )

client.run()
