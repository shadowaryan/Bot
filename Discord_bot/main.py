from turtle import title
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests

client = commands.Bot(command_prefix = '$')
#ok


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

@client.command()
async def stats(message):
    # if message.author == client.user:
    #     return

    # id = client.get_guild(950674739133808690)
    name = str(message.guild.name)
    owner_name = str(message.guild.owner)
    server_id = str(message.guild.id)
    no_of_channels = str(message.guild.channels)
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
  
@client.command()
async def nft(message,*,slug):
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
    



load_dotenv()
client.run(os.getenv('TOKEN'))
