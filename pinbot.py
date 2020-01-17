import discord
from datetime import date, time
from discord.ext import commands
from pymongo import MongoClient

mClient = MongoClient()
db = mClient['pinbot']
# lines above set up mongodb connection and database

bot = discord.Client()
bot = commands.Bot(command_prefix='s?') # change prefix to whatever you want for command usage

@bot.event
async def on_raw_reaction_add(payload):
    message_channel = bot.get_channel(payload.channel_id)
    pin_user_id = await bot.fetch_user(payload.user_id)
    pin_msg_id = payload.message_id
    pin_fetch_msg = await message_channel.fetch_message(pin_msg_id)
    pin_channel = discord.utils.get(message_channel.guild.text_channels, name='pinbot')
    # lines above get all the information about the pinned message, (channel, user, message id, message object) 
    # and sets up the channel that the message will be "pinned" in.

    pin_db = db[str(message_channel.guild.id)]
    if payload.emoji.name == "📌":
        if pin_fetch_msg.author == bot.user:
            return
        pin_db_log = {
                    "pin_message_id": str(pin_msg_id),
                    "pin_user_name": str(pin_user_id.name),
                    "pinned_from_channel": str(message_channel)
                  }
        # lines above set up what information is saved in the mongodb document (this is used for checking if the
        # message has been pinned before, to  avoid messages being pinned multiple times).it also logs the message
        # author and the channel it was sent in (these 2 aren't needed).

        pin_user_avatar = pin_user_id.avatar_url
        pin_date = str(date.today())
        pin_embed = discord.Embed(type="rich",
                                    title="#" + message_channel.name,
                                    description=str(pin_fetch_msg.content + "\n\n *[Jump to message](" + pin_fetch_msg.jump_url + ")*"),
                                    color=0xFF6322).set_footer(text=pin_user_id.name + " • " + pin_date,
                                    icon_url=pin_user_avatar)
        if len(pin_fetch_msg.attachments) > 0:
            pin_embed.set_image(url=pin_fetch_msg.attachments[0].url)
            pin_embed.add_field(name="Message attachment", value = "[" + pin_fetch_msg.attachments[0].filename + "](" + pin_fetch_msg.attachments[0].url + ")")
            # lines above entirely are used for setting up the embed formatting, and inserting message content into
            # the embed. it also checks if there was an attachment in the message, and shows it where applicable.

        if pin_db.find_one({"pin_message_id": str(pin_msg_id)}) is None:
            pin_id = pin_db.insert_one(pin_db_log).inserted_id
            await pin_channel.send(embed=pin_embed)
        # this is used for checking if the message has been pinned before. if not, pin it and add the log info
        # to the collection.
        else:
            return
        # if it has been pinned, do nothing.

@bot.command()
async def quit(ctx):
    await bot.close()
    # used for closing the bot if you plan to make changes. this can either be entirely removed, or modified so
    # only the bot owner (presumably yourself) can use it. as it stands, any user can use the command and
    # turn off the bot.

bot.run(token)
