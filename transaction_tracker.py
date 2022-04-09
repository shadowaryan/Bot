from sqlalchemy.orm import Session
from sqlalchemy import select
import requests

import os
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks
client = commands.Bot(command_prefix = '$')

from Telegram_bot.main import engine
from models import *

session = Session(bind=engine)

@tasks.loop(seconds=10)
async def track_transaction():
    print("sending transaaction......")
    contract = session.query(Contract).order_by(Contract.total_transaction.desc()).first()
    
    headers = {'X-API-Key': 'xha1n5zJ86je4uT9ryM751OMv24JPr08xpsGKachXQ8GyazgRI3SRwkfs35Tzo7h','accept': 'application/json'}
    total_transaction = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{contract.contract_address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea',headers=headers).json()['total']
    print(f"no of total trans - {total_transaction}")
    if (total_transaction) != int(contract.total_transaction) and total_transaction > int(contract.total_transaction):
        print("here")
        print(type(contract.total_transaction))
        total = total_transaction-int(contract.total_transaction)
        print(contract.total_transaction)
        old = contract.total_transaction
        print(f"going for {contract.total_transaction}")
        channel_id = contract.channel_id
        
        transaction_response = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{contract.contract_address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea&offset=0',headers=headers).json()['result']

        k=0
        print(type(total))
        for x in reversed(range(int(total))):
            print("range -"+ str(x))

            # print(f"going for transaction number - {k+1}")
            offset_value = k+1+int(old)
            print(offset_value)
            
            transaction_hash = transaction_response[x]['transaction_hash']
            print(transaction_hash)
            
            print(channel_id)
            contract = Contract(user_id=contract.user_id,collection_id=contract.collection_id,channel_id=channel_id,contract_address=contract.contract_address,contract_type=contract.contract_type,latest_transaction_hash=transaction_hash,total_transaction=str(offset_value))
            session.add(contract)
            

            slug_name = session.execute(select(Collection.slug).where(Collection.id==contract.collection_id).order_by(Collection.id)).first()[0]

            icon = requests.get(f'https://api.opensea.io/collection/{slug_name}').json()['collection']['image_url']
            print(type(channel_id))
            message_channel_name = client.get_channel(int(channel_id))                    
            embed = discord.Embed(
                title = f"NFT = {slug_name}",
                description = "NFT Transaction",
                color = discord.Color.dark_gold()
            )
            embed.set_thumbnail(url=icon)
            print(message_channel_name)
            
            for key ,value in transaction_response[x].items():
                embed.add_field(name=key, value=value ,inline=True)
                            
            await message_channel_name.send(embed=embed)
            
            session.commit()
            k = k+1
    else:
        print("no latest update")

    session.expire_all()

@track_transaction.before_loop
async def before():
    await client.wait_until_ready()
    print("Started")


load_dotenv()
track_transaction.start()
client.run(os.getenv('TOKEN'))