import scurrypy, os
from dotenv import load_dotenv

load_dotenv()

OWNER_ID = 582648847881338961
GUILD_ID = 905167903224123473
APPLICATION_ID = 1440875315608948899
VERIFY_CHANNEL_ID = 1440890196517326930
WELCOME_CHANNEL_ID = 1440890422481129546
ACORN_EMOJI_ID = 1440879841334268028
MEMBER_ROLE_ID = 1046627142345170984

client = scurrypy.Client(
    token=os.getenv('DISCORD_TOKEN'),
    application_id=APPLICATION_ID,
    sync_commands=False,
    intents=scurrypy.set_intents(message_content=True, guild_message_reactions=True, guild_members=True),
    prefix='!'
)

@client.prefix_command('rules')
async def on_rules(bot: scurrypy.Client, event: scurrypy.MessageCreateEvent):
    if event.message.author.id != OWNER_ID:
        return
    
    flaming_acorn = bot.emojis.get_emoji('flaming_acorn').mention

    await event.message.send(
        scurrypy.MessagePart(
            embeds=[
                scurrypy.EmbedPart(
                    title="Rules",
                    author=scurrypy.EmbedAuthor(
                        name="Squirrel Stash",
                        icon_url="attachment://wizard.png"
                    ),
                    thumbnail=scurrypy.EmbedThumbnail("attachment://rules_book.png"),
                    description="Before we get started, let's establish some rules first.",
                    fields=[
                        scurrypy.EmbedField(
                            f"{flaming_acorn} Respect",
                            "Please treat others with respect and be mindful of the things you say."
                        ),
                        scurrypy.EmbedField(
                            f"{flaming_acorn} Content",
                            "No malicious or NSFW content, advertising, spam, or discussion of charged topics."
                        ),
                        scurrypy.EmbedField(
                            f"{flaming_acorn} Bot Policy",
                            "If you have any questions, feel free to post it in <#1195785157177782292>."
                        ),
                        scurrypy.EmbedField(
                            f"{flaming_acorn} Warning Policy",
                            "**Kick -> Mute -> Ban** is generally followed depending on severity."
                        )
                    ],
                    footer=scurrypy.EmbedFooter("These rules are subject to change!", "attachment://alert.png")
                )
            ],
            attachments=[
                scurrypy.Attachment('assets/wizard.png', 'wizard'),
                scurrypy.Attachment('assets/rules_book.png', 'rules'),
                scurrypy.Attachment('assets/alert.png', 'warn')
            ]
        )
    )

@client.prefix_command('verify')
async def on_build_verify(bot: scurrypy.Client, event: scurrypy.MessageCreateEvent):
    # MUST be owner AND right channel!
    if event.message.author.id != OWNER_ID:
        return
    if event.message.channel_id != VERIFY_CHANNEL_ID:
        return
    
    resp = await event.message.send(
        scurrypy.MessagePart(
            embeds=[
                scurrypy.EmbedPart(
                    title="Verify",
                    author=scurrypy.EmbedAuthor(
                        name='Squirrel Stash',
                        icon_url='attachment://wizard.png'
                    ),
                    thumbnail=scurrypy.EmbedThumbnail("attachment://plus.png"),
                    description="By reacting to this message, you agree to the rules.",
                )
            ],
            attachments=[
                scurrypy.Attachment('assets/wizard.png', 'wizard'),
                scurrypy.Attachment('assets/plus.png', 'plus')
            ]
        )
    )

    await resp.add_reaction(bot.emojis.get_emoji('acorn'))

@client.event("MESSAGE_REACTION_ADD")
async def on_verify(bot: scurrypy.Client, event: scurrypy.ReactionAddEvent):
    # if correct channel and emoji and NOT the bot...
    if event.channel_id != VERIFY_CHANNEL_ID:
        return
    if event.emoji.id != ACORN_EMOJI_ID:
        return
    if event.user_id == APPLICATION_ID:
        return

    # remove reaction
    msg = await bot.fetch_message(event.channel_id, event.message_id).fetch()

    await msg.remove_user_reaction(bot.emojis.get_emoji('acorn'), event.user_id)

    # add Member role to user
    guild = await bot.fetch_guild(GUILD_ID).fetch()

    await guild.add_guild_member_role(event.user_id, MEMBER_ROLE_ID)

@client.event("GUILD_MEMBER_ADD")
async def on_welcome(bot: scurrypy.Client, event: scurrypy.GuildMemberAddEvent):
    channel = await bot.fetch_channel(WELCOME_CHANNEL_ID).fetch()

    acorn = bot.emojis.get_emoji('acorn').mention
    bullet = bot.emojis.get_emoji('bullet').mention

    await channel.send(
        scurrypy.MessagePart(
            content=f"{acorn} <@{event.user.id}> *has stumbled upon a community of squirrels!* {acorn}",
            embeds=[
                scurrypy.EmbedPart(
                    title=f"Welcome, {event.user.username}!",
                    description=f"""
                        {bullet} Read the rules in <#1046640388456321126>
                        {bullet} Verify in <#1440890196517326930>
                        {bullet} Hope you enjoy the bot!
                        """,
                    author=scurrypy.EmbedAuthor(
                        name='Squirrel Stash',
                        icon_url='attachment://wizard.png'
                    ),
                    thumbnail=scurrypy.EmbedThumbnail("attachment://bookie.png"),
                    image=scurrypy.EmbedImage('attachment://welcome.gif')
                )
            ],
            attachments=[
                scurrypy.Attachment("assets/wizard.png", 'wizard'),
                scurrypy.Attachment("assets/bookie.png", 'bookie'),
                scurrypy.Attachment("assets/welcome.gif", 'welcome')
            ]
        )
    )

@client.event("READY")
async def on_ready(bot: scurrypy.Client, event: scurrypy.ReadyEvent):
    await bot.emojis.fetch_all()

client.run()
