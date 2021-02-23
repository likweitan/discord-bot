from keep_alive import keep_alive

import discord
import os

import requests

from discord.ext import commands,tasks
from dotenv import load_dotenv

from itertools import cycle

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix=".")

text_channel_list = []
for server in bot.guilds:
    print(server)
    for channel in server.channels:
        print(channel)
        if channel.type == 'Text':
            text_channel_list.append(channel)

def get_cases(country):
    res = requests.get("https://coronavirus-19-api.herokuapp.com/countries/" + country)

    print(res.status_code)

    json = res.json()
    print(json)
    x = (json['todayCases'])
    print('Total number of cases: ' + str(x))
    return x

@bot.event
async def on_ready():
  change_status.start()
  #send_message.start(bot.guilds)
  print('Bot is ready')
  print(bot.guilds)

@bot.command(
  help="Uses come crazy logic to determine if pong is actually the correct value or not.",
	brief="Prints pong back to the channel."
  )
async def ping(ctx):
	await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


@bot.command()
async def tracking(ctx, *args):
	response = ""

	for arg in args:
		response = response + " " + arg

	await ctx.channel.send(response)

@bot.event
async def on_message(message):
	if message.content.startswith('http'):
		await message.channel.send("noob")

	await bot.process_commands(message)

@bot.command()
async def corona(ctx, arg):
  total_new_cases = get_cases(arg)
  embed=discord.Embed(title="sd")
  embed.add_field(name="undefined", value="Total new cases today: " + str(total_new_cases), inline=False)
  await ctx.send(embed=embed)

@bot.command()
async def minecraft(ctx, arg):
  params = dict(ip=arg)
  res = requests.get('https://mcapi.us/server/status',params=params)
  json_data = res.json()

  description = str(json_data['motd'])
  online = str(json_data['online'])
  player_count = str(json_data['players']['now'])

  embed = discord.Embed(
    title = arg + " Server Info",
    description = "Description: " + description + "\nOnline: " + online + "\nPlayers: " + player_count,
    colour = 0x542a93
  )
  embed.set_thumbnail(url='https://eu.mc-api.net/v3/server/favicon/'+arg)
  await ctx.send(embed=embed)


@tasks.loop(seconds=60)
async def change_status():
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers"))
"""
@tasks.loop(seconds=60)
async def send_message(guild):
  await guild.text_channels[0].send("I have joined the server")
"""




keep_alive()
bot.run(TOKEN)