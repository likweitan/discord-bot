import discord
from discord.ext import commands,tasks

import os
import requests
import re
import logging # For logging
import platform # For stats

import wikipedia
from better_profanity import profanity

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
VIRUSTOTALKEY = os.getenv('VIRUSTOTALKEY')



bot = commands.Bot(command_prefix='.', case_insensitive=True)#, owner_id=271612318947868673)
logging.basicConfig(level=logging.INFO)
bot.version = '1'

text_channel_list = []

for server in bot.guilds:
    print(server)
    for channel in server.channels:
        print(channel)
        if channel.type == 'Text':
            text_channel_list.append(channel)

def find_url(string): 
  
    # findall() has been used  
    # with valid conditions for urls in string 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url] 

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
  print("-----\nLogged in as: {} : {}\n-----\nMy current prefix is: .\n-----".format(bot.user.name, bot.user.id))
  print(bot.guilds)

@bot.command(
  help="Uses come crazy logic to determine if pong is actually the correct value or not.",
	brief="Prints pong back to the channel."
  )
async def ping(ctx):
	await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))

@bot.command()
async def stats(ctx):
    """
    A usefull command that displays bot statistics.
    """
    pythonVersion = platform.python_version()
    dpyVersion = discord.__version__
    serverCount = len(bot.guilds)
    memberCount = len(set(bot.get_all_members()))

    embed = discord.Embed(title=f'{bot.user.name} Stats', description='\uFEFF', colour=ctx.author.colour, timestamp=ctx.message.created_at)

    embed.add_field(name='Bot Version:', value=bot.version)
    embed.add_field(name='Python Version:', value=pythonVersion)
    embed.add_field(name='Discord.Py Version', value=dpyVersion)
    embed.add_field(name='Total Guilds:', value=serverCount)
    embed.add_field(name='Total Users:', value=memberCount)
    embed.add_field(name='Bot Developer:', value="https://github.com/likweitan/discord-bot")

    embed.set_footer(text=f"Requested By | {bot.user.name}")
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
    embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/11171910')
    await ctx.send(embed=embed)

@bot.command()
async def tracking(ctx, *args):
	response = ""

	for arg in args:
		response = response + " " + arg

	await ctx.channel.send(response)

@bot.event
async def on_message(message):
  #if message.content.startswith('http'):
  #  await message.channel.send("noob")

  # Convert All String to Lowercase
  message = message.lower()
  
  if profanity.contains_profanity(message.content):
    await message.channel.send("No bad words please")

  if "codes" in message.content:
    print('codes detected')

  if "http" in message.content:
    url = 'https://www.virustotal.com/vtapi/v2/url/report'

    resource = find_url(message.content)

    params = {'apikey': VIRUSTOTALKEY, 'resource': resource}

    response = requests.get(url, params=params)

    print(response.json())

    print(response.json()['positives'])

    if not response.json()['positives'] == 0:
        await message.add_reaction("👎")
    else:
        await message.add_reaction("👍")
    

  await bot.process_commands(message)

@bot.command()
async def corona(ctx, arg):
  total_new_cases = get_cases(arg)
  embed=discord.Embed(title="sd")
  embed.add_field(name="undefined", value="Total new cases today: " + str(total_new_cases), inline=False)
  await ctx.send(embed=embed)

@bot.command()
async def wiki(ctx, arg):
  wikipedia.set_lang("en")
  try:
    answer = wikipedia.summary(arg, sentences=3)
  except wikipedia.exceptions.DisambiguationError as e:
    answer = '"' + str(arg) + '" does not match any pages. Try another query!'
  embed=discord.Embed(title="Wikipedia")
  embed.add_field(name=arg, value=answer, inline=False)
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

bot.run(TOKEN)