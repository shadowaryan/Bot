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
from utils import get_collection_id

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
    if session.query(User).filter_by(user_id=str(author.id)).all() == []:
        print('ADDING USER')
        user = User(user_id=str(author.id),platform='Discord')
        session.add(user)
        session.commit()
        print('User added')
    else:
        print('user exists')

    name = str(message.guild.name)
    owner_name = str(message.guild.owner)
    server_id = str(message.guild.id)
    member_count = str(message.guild.member_count)
    #no_of_channels = str(message.guild.channels)

    icon = str(message.guild.icon_url)

    embed = discord.Embed(
        title = "Server Stats",
        color = discord.Color.dark_red()
    )
    embed.set_thumbnail(url=icon)

    embed.add_field(name="Server Name", value=name ,inline=True)
    embed.add_field(name="Owner name", value=owner_name ,inline=True)
    embed.add_field(name="Server id", value=server_id ,inline=True)
    embed.add_field(name="Member Count", value=member_count ,inline=True)
    # embed.add_field(name="no of channel", value=no_of_channels ,inline=True)

    await message.send(embed=embed)


#nft stats command 
@client.command()
async def nft(message,*,slug_name):

    author = message.message.author

    if session.query(User).filter_by(user_id=str(author.id)).all() == []:
        print('ADDING USER')
        user = User(user_id=str(author.id),platform='Discord')
        session.add(user)
        session.commit()
        print('User added')
    else:
        print('user exists')


    
    slug = slug_name.split('/')[-1]

    if slug != '':
        
        response = requests.get(f'https://api.opensea.io/collection/{slug}/stats').json()['stats']
        
        icon = requests.get(f'https://api.opensea.io/collection/{slug}').json()['collection']['image_url']
        
        embed = discord.Embed(
            title = f"NFT = {slug}",
            description = "NFT Stats",
            color = discord.Color.dark_red()
        )
        embed.set_thumbnail(url=icon)

        for key ,value in response.items():
            embed.add_field(name=key, value=value ,inline=True)
        
        await message.send(embed=embed)


        #adding nft data to database
        await message.send(f"NFT Collection Name - {slug}")
    
        user = session.query(User).filter_by(user_id=str(author.id)).first()
        collection_id = get_collection_id(slug)

        if session.query(User_Collection).filter(User_Collection.collection_id==collection_id, User_Collection.user_id==user.id).count() == 0:
            user.collections.append(session.query(Collection).filter_by(id=collection_id).first())
            print('User_Collection added')          
        else:
            print('user_collection exists')
            await message.send("Collection is already in our Database.")
        
        session.commit()
    else:
        await message.send("invalid input")



#data adding function 
async def data(server_id,channel_id,channel_name,author):
    print('Inside data function')
    
    if session.query(Discord_User).filter_by(set_nft_channel_id=str(channel_id)).all() == []:
        print('Adding user data')
        user = session.query(User).filter_by(user_id=str(author.id)).first()
        discord_user = Discord_User(set_nft_channel_name=channel_name,set_nft_channel_id=channel_id,user_id=user.id,server_id=server_id)
        session.add(discord_user)
        session.commit()
        print('User data added')
    else:
        print('user data exists')


#set channel for nft command   
@client.command()
@commands.has_permissions(administrator=True)
async def set_channel(message,*,channel_name):
    print('SET CHANNEL')
    
    for channel in message.guild.channels:
        if str(channel) == channel_name:
            channel_id = channel.id

    
    try:
        if channel_name != client.get_channel(channel_id):
            message_channel_name = client.get_channel(channel_id)

            server_id = str(message.guild.id)
            author = message.message.author
            
            if session.query(User).filter_by(user_id=str(author.id)).all() == []:
                print('ADDING USER')
                user = User(user_id=str(author.id),platform='Discord')
                session.add(user)
                session.commit()
                print('User added')
            else:
                print('user exists')

            await data(server_id,channel_id,channel_name,author)

            await message_channel_name.send("Hii")
            print("message send")           
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


load_dotenv()
client.run(os.getenv('TOKEN'))
