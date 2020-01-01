import discord
from datetime import date, time
from discord.ext import commands
from pymongo import MongoClient

mClient = MongoClient()
db = mClient['pinbot']

bot = discord.Client()
bot = commands.Bot(command_prefix='s?')

@bot.event
async def on_raw_reaction_add(payload):
    message_channel = bot.get_channel(payload.channel_id)
    pin_user_id = await bot.fetch_user(payload.user_id)
    pin_msg_id = payload.message_id
    pin_fetch_msg = await message_channel.fetch_message(pin_msg_id)
    pin_channel = discord.utils.get(message_channel.guild.text_channels, name='pinbot')

    pin_db = db[str(message_channel.guild.id)]
    if payload.emoji.name == "📌":
        pin_db_log = {
                    "pin_message_id": str(pin_msg_id),
                    "pin_user_name": str(pin_user_id.name),
                    "pinned_from_channel": str(message_channel)
                  }

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

        if pin_db.find_one({"pin_message_id": str(pin_msg_id)}) is None:
            pin_id = pin_db.insert_one(pin_db_log).inserted_id
            await pin_channel.send(embed=pin_embed)
        else:
            return

@bot.command()
async def quit(ctx):
    await bot.close()

bot.run(token)
