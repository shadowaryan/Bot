import asyncio
from email import message
from tkinter import OFF
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.schedulers.asyncio import asyncio
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select
import requests
from telegram import Bot

import os
from dotenv import load_dotenv


import discord
from discord.ext import commands, tasks
client = commands.Bot(command_prefix = '$')

from Telegram_bot.main import engine
from models import *


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 1,
    'misfire_grace_time': 1
}

session = Session(bind=engine)


# bot = Bot(token='5221341356:AAF5D4OKX3rEHv5M3KvyY6Sg9caipj0ej-k')

# def track_stats():
#     print('Tracking stats.........')
#     collections = session.query(Collection).all()
#     for collection in collections:
#         resp = requests.get(f'https://api.opensea.io/collection/{collection.slug}/stats').json()['stats']
#         latest_record = session.query(History).filter_by(collection_id=collection.id).order_by(History.id.desc()).first()
#         if round(float(latest_record.floor_price),2) != round(resp['floor_price'],2):
#             print(f'{collection.slug} price changed from {round(float(latest_record.floor_price),2)} to {round(resp["floor_price"],2)}')
#             history = History(**resp, collection_id=collection.id)
#             session.add(history)
#             print("Adding to history")
#             session.commit()
#             session.refresh(history)

#             users = collection.users
#             for user in users:
#                 message = f"Floor price of {collection.slug[0].upper()+collection.slug[1:]} has changed from {round(float(latest_record.floor_price),2)} to {resp['floor_price']}"
#                 print(f"Sending message to {user.username}")
#                 bot.send_message(chat_id=user.chat_id, text=message)
#         else:
#             print(f'{collection.slug} price not changed from {round(float(latest_record.floor_price),2)} to {round(resp["floor_price"],2)}')

    
#     session.expire_all()

@tasks.loop(seconds=10)
async def track_transaction():
    print("sending transaaction......")
    contract = session.query(Contract).order_by(Contract.total_transaction.desc()).first()
    
    headers = {'X-API-Key': 'xha1n5zJ86je4uT9ryM751OMv24JPr08xpsGKachXQ8GyazgRI3SRwkfs35Tzo7h','accept': 'application/json'}
    total_transaction = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{contract.contract_address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea',headers=headers).json()['total']
    print(f"no of total trans - {total_transaction}")
    if (total_transaction-1) != int(contract.total_transaction) and total_transaction > int(contract.total_transaction):
        print("here")
        print(type(contract.total_transaction))
        total = total_transaction-int(contract.total_transaction)
        print(contract.total_transaction)
        old = contract.total_transaction
        print(f"going for {int(old)+1}")
        channel_id = contract.channel_id
        
        transaction_response = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{contract.contract_address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea&offset={old}',headers=headers).json()['result']
        k=0
        for x in transaction_response:
            
            print(f"going for transaction number - {k+1}")
            offset_value = k+1+int(old)
            print(offset_value)
            
            transaction_hash = transaction_response[k]['transaction_hash']
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
            
            for key ,value in transaction_response[k].items():
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

        
    



scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
# scheduler.add_job(track_stats, 'interval', minutes=2)
# scheduler.add_job(track_transaction, 'interval', minutes=2)
load_dotenv()
track_transaction.start()
client.run(os.getenv('TOKEN'))
