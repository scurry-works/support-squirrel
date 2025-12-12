import scurrypy, os, dotenv

dotenv.load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = 1440875315608948899
GUILD_ID = 905167903224123473

OWNER_ID = 582648847881338961
VERIFY_CHANNEL_ID = 1440890196517326930
WELCOME_CHANNEL_ID = 1440890422481129546
ACORN_EMOJI_ID = 1400922547679264768
MEMBER_ROLE_ID = 1046627142345170984

from scurry_kit import ScurryKit, EmbedBuilder as E

class MyBot(ScurryKit):
    def __init__(self):
        super().__init__(
            token=TOKEN,
            application_id=APPLICATION_ID,
            prefix='!',
            intents=scurrypy.Intents.set(
                message_content=True, 
                guild_members=True, 
                guild_message_reactions=True,
                guild_emojis_and_stickers=True
            ),
            guild_emojis=True, # for reaction verification
            bot_emojis=True # for embed building
        )

        self.bot_user = self.application(APPLICATION_ID)

client = MyBot()

@client.start_hook
async def on_start(bot: MyBot):
    app = await bot.bot_user.fetch()
    bot.bot_user = app.bot

@client.prefix('rules')
async def on_build_rules(bot: MyBot, msg: scurrypy.Message):
    event: scurrypy.MessageCreateEvent = msg.context

    if event.author.id != OWNER_ID:
        return
    
    flaming_acorn = bot.get_bot_emoji('flaming_acorn').mention

    embed = scurrypy.EmbedPart(
        author=E.user_author(bot.bot_user),
        thumbnail=scurrypy.EmbedThumbnail("attachment://rules_book.png"),
        description="Before we get started, let's establish some rules.",
        fields=[
            E.field(f"{flaming_acorn} Respect",
                "Please treat others with respect and be mindful of the things you say."),
            E.field(f"{flaming_acorn} Content",
                "No malicious or NSFW content, advertising, spam, or discussion of charged topics."),
            E.field(f"{flaming_acorn} Bot Policy",
                "If you have any questions, feel free to post it in <#1195785157177782292>."),
            E.field(f"{flaming_acorn} Warning Policy",
                "**Kick -> Mute -> Ban** is generally followed depending on severity.")
        ],
        footer=E.footer("These rules are subject to change!", 
            "attachment://alert.png")
    )

    attachments = [
        scurrypy.Attachment('assets/rules_book.png', 'rules'),
        scurrypy.Attachment('assets/alert.png', 'warn')
    ]

    await msg.send(
        scurrypy.MessagePart(
            embeds=[embed], 
            attachments=attachments
        )
    )

@client.prefix('verify')
async def on_build_verify(bot: MyBot, msg: scurrypy.Message):
    event: scurrypy.MessageCreateEvent = msg.context

    if event.author.id != OWNER_ID:
        return
    if event.channel_id != VERIFY_CHANNEL_ID:
        return
    
    embed = scurrypy.EmbedPart(
        title='Verify',
        author=E.user_author(bot.bot_user),
        thumbnail=scurrypy.EmbedThumbnail("attachment://plus.png"),
        description="By reacting to this message, you agree to the rules."
    )

    attachments=[
        scurrypy.Attachment('assets/plus.png', 'plus')
    ]

    resp = await msg.send(
        scurrypy.MessagePart(
            embeds=[embed],
            attachments=attachments
        )
    )

    resp_msg = bot.message(resp.channel_id, resp.id)

    await resp_msg.add_reaction(bot.get_guild_emoji(ACORN_EMOJI_ID))

@client.event("MESSAGE_REACTION_ADD")
async def on_verify(bot: MyBot, event: scurrypy.ReactionAddEvent):

    # if correct channel and emoji and NOT the bot...
    if event.channel_id != VERIFY_CHANNEL_ID:
        return
    if event.emoji.id != ACORN_EMOJI_ID:
        return
    if event.user_id == APPLICATION_ID:
        return

    # remove reaction
    msg: scurrypy.Message = bot.message(event.channel_id, event.message_id)

    await msg.remove_user_reaction(bot.get_guild_emoji(ACORN_EMOJI_ID), event.user_id)

    # add Member role to user
    guild = bot.guild(GUILD_ID)

    await guild.add_guild_member_role(event.user_id, MEMBER_ROLE_ID)

@client.event("GUILD_MEMBER_ADD")
async def on_welcome(bot: MyBot, event: scurrypy.GuildMemberAddEvent):
    channel: scurrypy.Channel = bot.channel(WELCOME_CHANNEL_ID)

    acorn = bot.get_bot_emoji('acorn').mention
    bullet = bot.get_bot_emoji('bullet').mention

    embed = scurrypy.EmbedPart(
        author=E.user_author(bot.bot_user),
        title=f"Welcome, {event.user.username}!",
        thumbnail=scurrypy.EmbedThumbnail("attachment://bookie.png"),
        description=f"""
            {bullet} Read the rules in <#1046640388456321126>
            {bullet} Verify in <#1440890196517326930>
            {bullet} Hope you enjoy the bot!
        """,
        image=scurrypy.EmbedImage('attachment://welcome.gif')
    )

    attachments=[
        scurrypy.Attachment("assets/bookie.png", 'bookie'),
        scurrypy.Attachment("assets/welcome.gif", 'welcome')
    ]

    await channel.send(
        scurrypy.MessagePart(
            content=f"{acorn} <@{event.user.id}> *has stumbled upon a community of squirrels!* {acorn}",
            embeds=[embed],
            attachments=attachments
        )
    )

client.run()
