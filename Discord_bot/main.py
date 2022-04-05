from turtle import title
import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure
import os
from dotenv import load_dotenv
import requests
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import true ,create_engine,select
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
    user = User(user_id=str(author.id),platform='Discord')

    if session.query(User).filter_by(user_id=str(author.id)).all() == []:
        print('ADDING USER')
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



#transaction
@client.command()
async def set_nft(message,*,slug_name):
    author = message.message.author
    
    if session.query(exists().where(User.user_id == str(author.id))).scalar() == True:
        #checking and setting collection data

        user = session.query(User).filter_by(user_id=str(author.id)).first()
        collection_id = get_collection_id(slug_name)

        if session.query(User_Collection).filter(User_Collection.collection_id==collection_id, User_Collection.user_id==user.id).count() == 0:
            user.collections.append(session.query(Collection).filter_by(id=collection_id).first())
            print('User_Collection added. sending transaction ......')          
        else:
            print('user_collection exists')
            await message.send("Collection is already in our Database. sending transaction...")
        
        session.commit()
            
            
        #checking channel
        if session.query(exists().where(Discord_User.set_nft_channel_id == str(message.channel.id))).scalar() == True:
            channel_id = message.channel.id
            message_channel_name = client.get_channel(channel_id)
            print('channel check')
        

            response = requests.get(f'https://api.opensea.io/collection/{slug_name}').json()['collection']['primary_asset_contracts']
            # print(len(response))
            for x in response:
                if session.query(Contract).filter(Contract.contract_type == str(x['address']),Contract.contract_type == str(x['asset_contract_type'])).count() == 0:
                    
                    address = x['address']
                    print('nft address -'+address)
                    
                    if address != None:
                        print('here')
                        headers = {'X-API-Key': 'xha1n5zJ86je4uT9ryM751OMv24JPr08xpsGKachXQ8GyazgRI3SRwkfs35Tzo7h','accept': 'application/json'}
                        print('here')
                        transaction_resp = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea',headers=headers).json()['total']
                        print('here')
                        total = str(transaction_resp-1)
                        
                        print(total)
                        
                        
                        
        
                        
                                                
                        if session.query(session.query(Contract).filter_by(contract_address=address).exists()).scalar():
                            # if not session.query(session.query(Contract).filter_by(total_transaction=total).exists()).scalar():
                            #     old_total = session.query(Contract).filter_by(contract_address=address).first()
                            #     print('started collecting all transaction')
                                
                            #     print(type(old_total.total_transaction))                              
                            
                            #     print('collecting all transaction')

                            #     new_total = str(int(total)-int(old_total.total_transaction))

                            #     for i in new_total:
                            #         offset_value = int(old_total.total_transaction)+int(i)
                            #         print(offset_value)
                            #         transaction_response = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea&offset={offset_value}',headers=headers).json()['result'][0]
                            #         print(transaction_response)
                            #         transaction_hash = transaction_response['transaction_hash']
                            #         print(transaction_hash)
                            #         print(type(offset_value))
                            #         print(type(x['address']))

                            #         # token_ids = transaction_response['token_ids']
                                    
                            #         # print(token_ids)
                            #         collection = session.query(Collection).filter_by(slug=slug_name).first()
                            #         contract = Contract(user_id=user.id,collection_id=collection.id,contract_address=x['address'],contract_type=x['asset_contract_type'],latest_transaction_hash=transaction_hash,total_transaction=str(offset_value))
                            #         session.add(contract)
                            #         session.commit()

                            #         icon = requests.get(f'https://api.opensea.io/collection/{slug_name}').json()['collection']['image_url']
                                    
                            #         embed = discord.Embed(
                            #             title = f"NFT = {slug_name}",
                            #             description = "NFT Transaction",
                            #             color = discord.Color.dark_gold()
                            #         )
                            #         embed.set_thumbnail(url=icon)

                            #         for key ,value in transaction_response.items():
                            #             embed.add_field(name=key, value=value ,inline=True)
                                    
                            #         await message_channel_name.send(embed=embed)
                            # else:
                            icon = str(message.guild.icon_url)
                            embed = discord.Embed(title="Update",description = "No transaction held")
                            embed.set_thumbnail(url=icon)
                            await message_channel_name.send(embed=embed)  
                        else:    
                            
                            print(total)
                            transaction_response = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea&offset={total}',headers=headers).json()['result'][0]
                            print(transaction_response)
                            transaction_hash = transaction_response['transaction_hash']
                            
                            print(transaction_hash)


                            # token_ids = transaction_response['token_ids']
                            
                            # print(token_ids)
                            collection = session.query(Collection).filter_by(slug=slug_name).first()
                            contract = Contract(user_id=user.id,collection_id=collection.id,channel_id=channel_id,contract_address=str(x['address']),contract_type=str(x["asset_contract_type"]),latest_transaction_hash=str(transaction_hash),total_transaction=total)
                            session.add(contract)
                            session.commit()

                            icon = requests.get(f'https://api.opensea.io/collection/{slug_name}').json()['collection']['image_url']
                            
                            embed = discord.Embed(
                                title = f"NFT = {slug_name}",
                                description = "NFT Transaction",
                                color = discord.Color.dark_gold()
                            )
                            embed.set_thumbnail(url=icon)

                            for key ,value in transaction_response.items():
                                embed.add_field(name=key, value=value ,inline=True)
                            
                            await message_channel_name.send(embed=embed)
                else:
                    print('error')        
        else:
            await message.send("channel not exists")                
    else:
        await message.send("User not exists. Use $set_channel command to set user and then set the nft")
        



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
            user = User(user_id=str(author.id),platform='Discord')
            print('ok')
            if session.query(exists().where(User.user_id == str(author.id))).scalar() == False:
                print('ADDING USER')
                
                print('1')
                session.add(user)
                print('2')
                session.commit()
                print('User added')
            else:
                print('user exists')

            await data(server_id,channel_id,channel_name,author)

            await message_channel_name.send(f"Hello Admin , Verification is completed now to set nft alerts to channel - {channel_name}\nType :- $set_nft \"nft name\"")
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
