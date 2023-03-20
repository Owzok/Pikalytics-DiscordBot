from random import random
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.headless = True
chrome_options.add_argument("--window-size=1920.1200")

def p2f(x):
    return float(x.strip('%'))

def pkmn_types(soup):
    res = ""
    i = 3
    types = soup.find('div', {'class': 'header-div-padding'})
    for x in types.find_all('span', {'class': 'inline-block pokedex-header-types'}):
        type1 = x.contents[0].text.capitalize()
        if len(x.contents) > 1:
            type2 = x.contents[1].text.capitalize()
            return type1+' - '+type2
        else:
            return type1

def pkmn_moves(soup):
    res = ""
    moves = soup.find('div', {'id': 'moves_wrapper'})
    for x in moves.find_all('div', {'class': 'pokedex-move-entry-new'}):
        movement = x.contents[1].text.rstrip()
        usg = x.contents[5].text
        if p2f(usg) > 5.0:
            if len(movement) < 7:
                res+= movement + '\t\t\t' + usg + '\n'
            else:
                res+= movement + '\t\t' + usg + '\n'
    return res

def pkmn_stats(soup):
    res = ""
    i = 1
    stats = soup.find('div', {'id': 'bstats_wrapper'})
    for x in stats.find_all('div', {'style': ['display:inline-block;width:30px;text-align: left;', 'display:inline-block;vertical-align: middle;margin-left: 20px;']}):
        if i % 2 != 0:
            res += x.contents[0] + ' - '
            i+=1
        else:
            res += x.contents[0] + '\n'
            i+=1
    return res

def pkmn_items(soup):
    res = ""
    try:
        items = soup.find('div', {'id': 'items_wrapper'})
        empty = True
        for y in items.find_all('div', {'class': 'pokedex-move-entry-new'}):
            empty = False
            pkmn = y.contents[3].text.replace('\n', '')
            usg = y.contents[5].text
            if p2f(usg) > 5.0:
                if len(pkmn) < 7:
                    res += pkmn + '\t\t\t' + usg + '\n'
                else:
                    res += pkmn + '\t\t' + usg + '\n'
        
        if empty == True:
            return 'This format doesn\'t support item registers yet.'
    except:
        return 'This format doesn\'t have items yet.'
    return res

def pkmn_teammates(soup):
    res = ''
    teammates = soup.find('div', {'id': 'dex_team_wrapper'})
    for y in teammates.find_all('a', {'class': 'teammate_entry pokedex-move-entry-new'}):
        pkmn = y.contents[3].text.replace('\n', '')
        usg = y.contents[7].text
        if p2f(usg) > 10.0:
            if len(pkmn) < 7:
                res += pkmn + '\t\t\t' + usg + '\n'
            elif len(pkmn) > 14:
                res += pkmn + '\t' + usg + '\n'
            else:
                res += pkmn + '\t\t' + usg + '\n'
    return res

def pkmn_abilities(soup):
    res = ''
    try:
        abs = soup.find('div', {'id': 'abilities_wrapper'})
        for y in abs.find_all('div', {'class': 'pokedex-move-entry-new'}):
            empty = False
            pkmn = y.contents[1].text.replace('\n', '')
            usg = y.contents[3].text
            
            if len(pkmn) < 7:
                print(pkmn,'\t\t\t',usg)
                res += pkmn + '\t\t\t' + usg + '\n'
            else:
                res += pkmn + '\t\t' + usg + '\n'
        if empty == True:
            return 'This format doesn\'t support ability registers yet.'
    except:
        return 'This format doesn\'t have abilities yet.'
    return res

def pkmn_tera(soup):
    res = ''
    try:
        teras = soup.find('div', {'id': 'teratypes_wrapper'})
        for x in teras.find_all('div', {'class': 'pokedex-move-entry-new'}):
            type = x.contents[1].text.rstrip().capitalize()
            usg = x.contents[5].text
            if len(type) < 7:
                res += type + '\t\t\t' + usg + '\n'
            else:
                res += type + '\t\t' + usg + '\n'
    except:
        return 'This format doesn\'t have teratypes.'
    return res

def pkmn_evs(soup):
    res = ''
    try:
        ev = soup.find('div', {'id': 'dex_spreads_wrapper'})
        for y in ev.find_all('div', {'class': 'pokedex-move-entry-new'}):
            nat = y.contents[1].text
            usg = y.contents[10].text
            evs = y.contents[3].text + y.contents[4].text + y.contents[5].text + y.contents[6].text + y.contents[7].text + y.contents[8].text
            if p2f(usg) > 10.0:
                if len(nat+evs)+1 < 23:
                    res += nat + ' ' + evs + '\t\t' + usg + '\n'
                else:
                    res += nat + ' ' + evs + '\t' + usg + '\n'
    except:
        return 'This format doesn\'t have ev spreads yet.'
    return res

class pika(commands.Cog):    
    def __init__(self, client):
        self.client = client
        self.vc = None # voice channel

        print('\n\n Pikalyics bot active !! \n\n')

# ============== FUNCTIONS ========================
    @commands.command()
    async def join(self, ctx):
        if self.vc != None:
            return
        if ctx.author.voice is None:
            await ctx.send("Connect to a voice channel")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=

    @commands.command()
    async def leave(self, ctx):
        if self.vc != None:
            await ctx.voice_client.disconnect()

    @commands.command(name='formats')
    async def formats(self, ctx):
        await ctx.send("Supported formats are: gen9ou, gen9doublesou, bdsp, gen8bsd, gen9vgc2023series1.")

# -------- MUSIC ----------
    @commands.command(name='data')
    async def get_pkmn_data(self, ctx, *args):

        self.formats = ['gen9ou', 'gen9doublesou', 'bdsp', 'gen8bsd', 'gen9vgc2023series1']

        if len(args) > 2:
            await ctx.send("Expected [2] arguments, received [3].")
            return

        if args[0] not in self.formats:
            await ctx.send('The following format is not supported: '+args[0]+'.')

        URL = 'https://www.pikalytics.com/pokedex/'+args[0]+'/'+args[1]

        driver = webdriver.Chrome("C:/chromedriver/chromedriver")

        driver.get(URL)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        embed = discord.Embed(title=args[1].capitalize(), url=URL, description=pkmn_types(soup))

        embed.add_field(name='Stats', value=pkmn_stats(soup), inline=True)

        embed.add_field(name='Moves', value=pkmn_moves(soup), inline=True)

        embed.add_field(name='Teammates', value=pkmn_teammates(soup), inline=True)

        embed.add_field(name='Items', value=pkmn_items(soup), inline=True)

        embed.add_field(name='Abilities', value=pkmn_abilities(soup), inline=True)

        embed.add_field(name='Teratypes', value=pkmn_tera(soup), inline=True)

        embed.add_field(name='EVS', value=pkmn_evs(soup), inline=True)

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(pika(client))