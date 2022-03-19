from itertools import count
import requests
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import sys

sys.path.append(".")
from models import *

engine = create_engine('postgresql+psycopg2://postgres:aoGY0J9U9o@hypemail-db-staging.c44vnyfhjrjn.us-east-1.rds.amazonaws.com:5432/nft-bot', echo=False)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

def get_collection_id(slug):
    collection = session.query(Collection).filter_by(slug=slug).first()
    if collection:
        return collection.id
    else:
        resp = requests.get(f'https://api.opensea.io/collection/{slug}/stats').json()['stats']
        floor_price = resp['floor_price']
        count = resp['count']
        collection = Collection(slug=slug, floor_price=floor_price,count=count)
        session.add(collection)
        session.commit()
        history =  History(**resp,collection_id=collection.id)
        session.add(history)
        session.commit()
        return collection.id

