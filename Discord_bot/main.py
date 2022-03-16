import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure
import os
from dotenv import load_dotenv
import requests
from sqlalchemy import true
import sys

client = commands.Bot(command_prefix = '$')
sys.path.append(".")
from models import *


#login event
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#join event
@client.event
async def on_member_join(member):
    print(f'{member} joined the server')

#remove event
@client.event
async def on_member_remove(member):
    print(f'{member} left the server')

#server stats command
@client.command()
async def stats(message):
    # if message.author == client.user:
    #     return

    # id = client.get_guild(950674739133808690)
    name = str(message.guild.name)
    owner_name = str(message.guild.owner)
    server_id = str(message.guild.id)
    #no_of_channels = str(message.guild.channels)
    member_count = str(message.guild.member_count)

    icon = str(message.guild.icon_url)

    embed = discord.Embed(
        title = "Server Stats",
        color = discord.Color.dark_red()
    )
    embed.set_thumbnail(url=icon)

    embed.add_field(name="Server Name", value=name ,inline=True)
    embed.add_field(name="Owner name", value=owner_name ,inline=True)
    embed.add_field(name="Server id", value=server_id ,inline=True)
    # embed.add_field(name="no of channel", value=no_of_channels ,inline=True)
    embed.add_field(name="Member Count", value=member_count ,inline=True)

    await message.send(embed=embed)
    # if message.content.startswith('$hello'):
    #     slug = message.content.partition('')[2]
    #     print(slug)
    #     await message.channel.send('Hello!')

    # if message.content.startswith('$server_stats'):
    # await message.send(f' Server Stats:-\n no of member: {id.member_count}')

#nft stats command 
@client.command()
async def nft(message,*,slug):
    response = requests.get(f'https://api.opensea.io/collection/{slug}/stats').json()['stats']
    
    icon = requests.get(f'https://api.opensea.io/collection/{slug}').json()['collection']['primary_asset_contracts'][0]['image_url']
    
    embed = discord.Embed(
        title = f"NFT = {slug}",
        description = "NFT Stats",
        color = discord.Color.dark_red()
    )
    embed.set_thumbnail(url=icon)

    for key ,value in response.items():
        embed.add_field(name=key, value=value ,inline=True)
    
    await message.send(embed=embed)


#set channel for nft command   
@client.command()
@commands.has_permissions(administrator=True)
async def set_channel(message,*,channel_name):

    for channel in message.guild.channels:
        if str(channel) == channel_name:
            channel_id = channel.id


    try:
        if channel_name != client.get_channel(channel_id):
            message_channel_name = client.get_channel(channel_id)
            print("message send")
            await message_channel_name.send("Hii")
        else:
            print("Got Error")
    except UnboundLocalError:
        await message.send(f"Channel Name - {channel_name}\nNot in a Server")


#user validation
@set_channel.error
async def set_channel_error(ctx, error):
    if isinstance(error, CheckFailure):
        msg = "You're not an administrator {}".format(ctx.message.author.mention)  
        await ctx.send(msg)

    #to get channel id
    # channel = discord.utils.get(message.guild.channels, name=channel_name)
    # if channel.id == channel.id:
    #     print("ok")
    



    # condition = True
    # for channel in message.guild.channels:
    #     if str(channel) == channel_name:
    #         await message.send(f"hello, your requested channel={channel_name}")
    #         return condition
            
    #     # else:
    #     #     await message.send("in")
    # if condition == True:
    #     print("hello")

load_dotenv()
client.run(os.getenv('TOKEN'))
