from telegram import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from uuid import uuid4
import sys
from sqlalchemy.orm import Session, sessionmaker
import requests
from sqlalchemy import create_engine
from sqlalchemy.sql import exists
import json


sys.path.append(".")
from models import *

from Telegram_bot.utils import get_collection_id


#engine = create_engine('postgresql://spqqojmysvclhl:35e13032f8326f8b7908e52a75e65215a62437d5c0c618aaee8a14392405e188@ec2-52-204-14-80.compute-1.amazonaws.com:5432/d7jch8clhgaktb', echo=False)

engine = create_engine('postgresql+psycopg2://postgres:aoGY0J9U9o@hypemail-db-staging.c44vnyfhjrjn.us-east-1.rds.amazonaws.com:5432/nft-bot', echo=False)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()



TOKEN = '5181629296:AAEO1swHrmsBotFGmItdz6JvKDSRbsWxMwY'


#bot start command    
def start(update, context):

    update.message.reply_text("""Hello,\n Welcome to NFT Collection Bot \nFor more - /help""")

    user_chat_id = str(update.effective_user.id)
    user_chat_type = update.effective_chat.type
    platform = User(user_id=user_chat_id,platform='Telegram')
    user = Telegram_User(username=update.effective_user.username,chat_id=user_chat_id,chat_type=user_chat_type)

    if not session.query(session.query(User).filter_by(user_id=user_chat_id).exists()).scalar():

        session.add(platform)
        session.commit()
        print('User added')
        if not session.query(session.query(Telegram_User).filter_by(chat_id=user_chat_id).exists()).scalar():
            session.add(user)
            session.commit()
            print('User_ added')
        

    
    
   


#bot help command
def help (update, context):
    update.message.reply_text("""
    Commands:
    /help - to view commands
    /add_collection <YOUR_NFT_COLLECTION_NAME_LINK> - to add NFT collection 
    """)


        
#bot command to get collection data 
def add_collection(update, context):
    url = update.message.text.partition(' ')[2]
    slug = url.split('/')[-1]
    if url != '':
        update.message.reply_text(f"NFT Collection Name - {slug}")
    
        user = session.query(User).filter_by(user_id=update.effective_user.id).first()
        collection_id = get_collection_id(slug)
        
        resp = requests.get(f'https://api.opensea.io/collection/{slug}/stats').json()['stats']

        # if not session.query(session.query(Collection, Telegram_User).filter(User_Collection.collection_id==collection_id, User_Collection.user_id==user.id).exists()).scalar():
        if session.query(User_Collection).filter(User_Collection.collection_id==collection_id, User_Collection.user_id==user.id).count() == 0:
            user.collections.append(session.query(Collection).filter_by(id=collection_id).first())
            print('Collection added')
            update.message.reply_text(f"NFT Collection Name - {slug}\nIs added to our Database")
            
        else:
            update.message.reply_text("Error - Invaild Text or collection is already there, please use /start and then /help to know commands")
        
        session.commit()
    
    else:
        update.message.reply_text("Error - Invaild Text, Use /help to know more")


#message handling command
def handle_message(update,context):
    message = update.message.text
    print(update.effective_user.id)
    print(update.effective_user.username)
    if message in ("Hi","Hii","hii","hello","Hello"):
        update.message.reply_text(f"{message}, there")
    else:
        update.message.reply_text("Error - Invalid Text , use /help ")


if __name__ == '__main__':
    updater = Updater('5181629296:AAEO1swHrmsBotFGmItdz6JvKDSRbsWxMwY', use_context=True)
    dp = updater.dispatcher
    print("started")
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add_collection", add_collection))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    

    updater.start_polling()
    updater.idle()


