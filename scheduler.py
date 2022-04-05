from email import message
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select
import requests
from telegram import Bot

import discord
from discord.ext import commands
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


bot = Bot(token='5221341356:AAF5D4OKX3rEHv5M3KvyY6Sg9caipj0ej-k')

def track_stats():
    print('Tracking stats.........')
    collections = session.query(Collection).all()
    for collection in collections:
        resp = requests.get(f'https://api.opensea.io/collection/{collection.slug}/stats').json()['stats']
        latest_record = session.query(History).filter_by(collection_id=collection.id).order_by(History.id.desc()).first()
        if round(float(latest_record.floor_price),2) != round(resp['floor_price'],2):
            print(f'{collection.slug} price changed from {round(float(latest_record.floor_price),2)} to {round(resp["floor_price"],2)}')
            history = History(**resp, collection_id=collection.id)
            session.add(history)
            print("Adding to history")
            session.commit()
            session.refresh(history)

            users = collection.users
            for user in users:
                message = f"Floor price of {collection.slug[0].upper()+collection.slug[1:]} has changed from {round(float(latest_record.floor_price),2)} to {resp['floor_price']}"
                print(f"Sending message to {user.username}")
                bot.send_message(chat_id=user.chat_id, text=message)
        else:
            print(f'{collection.slug} price not changed from {round(float(latest_record.floor_price),2)} to {round(resp["floor_price"],2)}')

    
    session.expire_all()

async def track_transaction():
    print("sending transaaction......")
    contracts = session.query(Contract).all()
    for contract in contracts:
        headers = {'X-API-Key': 'xha1n5zJ86je4uT9ryM751OMv24JPr08xpsGKachXQ8GyazgRI3SRwkfs35Tzo7h','accept': 'application/json'}
        total_transaction = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{contract.contract_address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea',headers=headers).json()['total']
        print(f"no of total trans - {total_transaction}")
        if total_transaction != contract.total_transaction:
            total = total_transaction-(contract.total_transaction)
            for x in total:
                print(f"going for transaction number - {x}")
                offset_value = x
                transaction_response = requests.get(f'https://deep-index.moralis.io/api/v2/nft/{contract.contract_address}/trades?chain=eth&from_date=2022-03-15&marketplace=opensea&offset={offset_value}',headers=headers).json()['result'][0]
                transaction_hash = transaction_response['transaction_hash']
                contract = Contract(user_id=contract.user_id,collection_id=contract.collection_id,channel_id=channel_id,contract_address=contract.contract_address,contract_type=contract.contract_type,latest_transaction_hash=transaction_hash,total_transaction=str(offset_value))
                session.add(contract)
                session.commit()

                slug_name = session.execute(select(Collection.slug).where(Collection.id==contract.collection_id).order_by(Collection.id)).first()[0]

                icon = requests.get(f'https://api.opensea.io/collection/{slug_name}').json()['collection']['image_url']
                channel_id = contract.channel_id
                message_channel_name = client.get_channel(channel_id)                    
                embed = discord.Embed(
                    title = f"NFT = {slug_name}",
                    description = "NFT Transaction",
                    color = discord.Color.dark_gold()
                )
                embed.set_thumbnail(url=icon)

                for key ,value in transaction_response.items():
                    embed.add_field(name=key, value=value ,inline=True)
                
                    await message_channel_name.send(embed=embed)
    

    session.expire_all()
        




scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler.add_job(track_stats, 'interval', minutes=2)
scheduler.add_job(track_transaction, 'interval', minutes=2)
scheduler.start()