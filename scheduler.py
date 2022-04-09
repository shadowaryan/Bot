from email import message
from tkinter import OFF
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests
from telegram import Bot


from Telegram_bot.main import engine
from models import *
from transaction_tracker import track_transaction

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


def transaction_track():
    print("started the bot")
    track_transaction()
    
    



scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler.add_job(track_stats, 'interval', minutes=2)
scheduler.add_job(transaction_track, 'interval', minutes=2)

