import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure
import os
from dotenv import load_dotenv
import requests
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import true ,create_engine
from sqlalchemy.sql import exists
import sys

client = commands.Bot(command_prefix = '$')
sys.path.append(".")
from models import *

engine = create_engine('postgresql+psycopg2://postgres:aoGY0J9U9o@hypemail-db-staging.c44vnyfhjrjn.us-east-1.rds.amazonaws.com:5432/nft-bot', echo=False)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()



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

    author = message.message.author
    id = str(author.id)
    platform = User(user_id=id,platform='Discord')
    if not session.query(session.query(User).filter_by(user_id=id).exists()).scalar():
        session.add(platform)
        session.commit()
        print('User added')


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

    author = message.message.author
    #await message.send('Your ID is: ' + str(author.id))
    # user_id(str(author.id))
    # id = 940835714524909609
    # await message.send(client.fetch_user(str(id)))
    # print(client.fetch_user(id))


    platform = User(user_id=str(author.id),platform='Discord')
    if not session.query(session.query(User).filter_by(user_id=str(author.id)).exists()).scalar():
        session.add(platform)
        session.commit()
        print('User added')



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

#thisone  
def data(message,server_id,channel_id,channel_name):
    author = message.message.author
    
    data = Discord_User(set_nft_channel_name=channel_name,set_nft_channel_id=channel_id,user_id=str(author.id),server_id=server_id)
    if not session.query(session.query(Discord_User).filter_by(user_id=str(author.id)).exists()).scalar():
        session.add(data)
        session.commit()
        print('User data added')



#set channel for nft command   
@client.command()
@commands.has_permissions(administrator=True)
async def set_channel(message,*,channel_name):

    server_id = str(message.guild.id)
    author = message.message.author
    user = User(user_id=str(author.id),platform='Discord')
    if not session.query(session.query(User).filter_by(user_id=str(author.id)).exists()).scalar():
        session.add(user)
        session.commit()
        print('User added')
        

    for channel in message.guild.channels:
        if str(channel) == channel_name:
            channel_id = channel.id

    
    
    try:
        if channel_name != client.get_channel(channel_id):
            message_channel_name = client.get_channel(channel_id)
            print(message_channel_name)
            print(channel_id)
            print(channel_name)
            print(message)
            print("message send")
            data(message,server_id,channel_id,channel_name)
            await message_channel_name.send("Hii")
            #here
           
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
