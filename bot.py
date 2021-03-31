"""
    Rocket League stats Discord bot.
"""

import discord
from discord.ext import commands

import requests
from bs4 import BeautifulSoup as bs
import re
import os


client = commands.Bot(command_prefix='!')
token = os.environ['BOT_TOKEN']
session = requests.Session()

playlists = []
ranks = []
percentiles = []
mmr = []
icons = []
icon_url = ''


@client.event
async def on_ready():
    print('Bot is ready.')


@client.command()
async def clear(ctx, amount=10):
    """ Clears a specified number of messages from the channel. """
    await ctx.channel.purge(limit=amount)


@client.command()
async def rank(ctx, user):
    """ Gets the rocket league ranks of a given user. """
    get_data(user)
    ranks_embed = discord.Embed(title=f'Rocket League ranks for {user}',
                                url=f'https://rocketleague.tracker.network/rocket-league/profile/epic/{user}/overview',
                                color=discord.Color.blue())
    ranks_embed.set_thumbnail(url=icon_url)

    for i in range(len(playlists)):
        ranks_embed.add_field(name=playlists[i], value=f'{ranks[i]}\nMMR: {mmr[i]}')

    ranks_embed.set_footer(text='Data from https://rocketleague.tracker.network/')

    clear_data()
    await ctx.send(embed=ranks_embed)


def clear_data():
    """ Helper method; clears all data lists. """
    playlists.clear()
    ranks.clear()
    percentiles.clear()
    mmr.clear()
    icons.clear()


def get_data(user):
    """ Helper method; gets data through a http request. """
    global icon_url
    url = f'https://rocketleague.tracker.network/rocket-league/profile/epic/{user}/overview'
    response = session.get(url)
    soup = bs(response.content, 'html.parser')

    for link in soup.findAll(class_='playlist'):
        playlists.append(link.text)

    for link in soup.findAll(class_='rank'):
        if '\n' in link.text:
            percentiles.append(re.sub('\n', '', link.text))
        else:
            ranks.append(link.text)

    for link in soup.findAll(class_='mmr'):
        mmr.append(link.text)

    for link in soup.findAll(class_='match__rating--icon'):
        icons.append(link.get('src'))

    icon_url = soup.find(class_='ph-avatar__image').get('src')


client.run(token)
