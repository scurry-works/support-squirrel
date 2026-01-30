import os, dotenv

dotenv.load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = 1440875315608948899
GUILD_ID = 905167903224123473

OWNER_ID = 582648847881338961
VERIFY_CHANNEL_ID = 1440890196517326930
WELCOME_CHANNEL_ID = 1440890422481129546
ACORN_EMOJI_ID = 1400922547679264768
MEMBER_ROLE_ID = 1046627142345170984

from scurrypy import (
    Client, Intents, 
    EventTypes, 
    MessageCreateEvent, Channel,
    ReactionAddEvent, GuildMemberAddEvent,
    MessagePart,
    EmbedPart, EmbedThumbnailPart, EmbedImagePart, EmbedFieldPart, EmbedFooterPart
)

from scurry_kit import (
    EmbedBuilder as E, 
    PrefixAddon,
    EventsAddon,
    GuildEmojiCacheAddon, BotEmojisCacheAddon,
    setup_default_logger
)

logger = setup_default_logger()

class BotUser:
    """Quick helper for fetching bot user on startup."""
    
    def __init__(self, client: Client):
        self.user = client.application(APPLICATION_ID)

        client.add_startup_hook(self.init_bot_user)

    async def init_bot_user(self):
        self.user = await self.user.fetch()

client = Client(
    token=TOKEN,
    intents=Intents.set(
        message_content=True, 
        guild_members=True, 
        guild_message_reactions=True,
        guild_emojis_and_stickers=True
    )
)

bot_user = BotUser(client)

# addons
events = EventsAddon(client)
prefixes = PrefixAddon(client, APPLICATION_ID, '!')

# caches 
guild_emojis = GuildEmojiCacheAddon(client)
bot_emojis = BotEmojisCacheAddon(client, APPLICATION_ID)

@prefixes.listen('rules')
async def on_build_rules(bot: Client, channel: Channel):
    event: MessageCreateEvent = channel.context

    if event.author.id != OWNER_ID:
        return
    
    flaming_acorn = bot_emojis.get_emoji('flaming_acorn').mention

    embed = EmbedPart(
        author=E.user_author(bot_user.user),
        thumbnail=EmbedThumbnailPart("https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/rules_book.png"),
        description="Before we get started, let's establish some rules.",
        fields=[
            EmbedFieldPart(f"{flaming_acorn} Respect",
                "Please treat others with respect and be mindful of the things you say."),
            EmbedFieldPart(f"{flaming_acorn} Content",
                "No malicious or NSFW content, advertising, spam, or discussion of charged topics."),
            EmbedFieldPart(f"{flaming_acorn} Bot Policy",
                "If you have any questions, feel free to post it in <#1195785157177782292>."),
            EmbedFieldPart(f"{flaming_acorn} Warning Policy",
                "**Kick -> Mute -> Ban** is generally followed depending on severity.")
        ],
        footer=EmbedFooterPart("These rules are subject to change!", 
            "https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/alert.png")
    )

    await channel.send(MessagePart(embeds=[embed]))

@prefixes.listen('verify')
async def on_build_verify(bot: Client, channel: Channel):
    event: MessageCreateEvent = channel.context

    if event.author.id != OWNER_ID:
        return
    if event.channel_id != VERIFY_CHANNEL_ID:
        return
    
    embed = EmbedPart(
        title='Verify',
        author=E.user_author(bot.bot_user),
        thumbnail=EmbedThumbnailPart("https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/plus.png"),
        description="By reacting to this message, you agree to the rules."
    )

    resp = await channel.send(MessagePart(embeds=[embed]))

    resp_msg = bot.message(resp.channel_id, resp.id)

    await resp_msg.add_reaction(guild_emojis.get_emoji(ACORN_EMOJI_ID))

@events.listen(EventTypes.MESSAGE_REACTION_ADD)
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

@events.listen(EventTypes.GUILD_MEMBER_ADD)
async def on_welcome(bot: Client, event: GuildMemberAddEvent):
    channel = bot.channel(WELCOME_CHANNEL_ID)

    acorn = bot_emojis.get_emoji('acorn').mention
    bullet = bot_emojis.get_emoji('bullet').mention

    import random

    select_thumb = random.choice(['bookie', 'pirate', 'wizard'])

    embed = EmbedPart(
        author=E.user_author(bot_user.user),
        title=f"Welcome, {event.user.username}!",
        thumbnail=EmbedThumbnailPart(f"https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/{select_thumb}.png"),
        description=f"""
            {bullet} Read the rules in <#1046640388456321126>
            {bullet} Verify in <#1440890196517326930>
            {bullet} Hope you enjoy the bot!
        """,
        image=EmbedImagePart('https://raw.githubusercontent.com/scurry-works/support-squirrel/refs/heads/main/assets/welcome.gif')
    )

    await channel.send(
        MessagePart(
            content=f"{acorn} <@{event.user.id}> *has stumbled upon a community of squirrels!* {acorn}",
            embeds=[embed]
        )
    )

client.run()
