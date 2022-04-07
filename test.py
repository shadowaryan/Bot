import requests
headers = {'X-API-Key': 'xha1n5zJ86je4uT9ryM751OMv24JPr08xpsGKachXQ8GyazgRI3SRwkfs35Tzo7h','accept': 'application/json'}
total_transaction = requests.get(f'https://deep-index.moralis.io/api/v2/nft/0x8a90cab2b38dba80c64b7734e58ee1db38b8992e/trades?chain=eth&from_date=2022-03-15&marketplace=opensea&offset=692',headers=headers).json()['result']
for x in total_transaction:
    print(x)
    print("hello")