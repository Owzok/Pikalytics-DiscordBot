import discord
from discord.ext import commands
import pika
import os

cogs = [pika]

client = commands.Bot(command_prefix='>', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

client.run(os.environ.get("Pikalytics_token"))