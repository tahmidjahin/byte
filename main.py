import discord
from discord.ext import commands
from discord import Intents, app_commands
import os
import requests
import json
import asyncio
import random
from keep_alive import keep_alive

import google.generativeai as genai
import pathlib
import textwrap

from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


conversation_history = {}

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

#ai-ends

intents = discord.Intents().all()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
client = discord.AutoShardedClient(intents=intents, shard_count=1)
tree = app_commands.CommandTree(client)


@client.event 
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='tahmidjahin!'))
  
  print('-----------------------------')
  print('Connected to Discord.gateway!')
  print('Logged in as {0.user}'.format(client))
  print('Connected to Gemini API!')
  print('-----------------------------')


  try:
    synced = await tree.sync()
    print(f'Synced {len(synced)} commands successfully!')
  except Exception as e:
    print(e)
    print('-----------------------------')
  
#slash-commands

@tree.command(name="greet", description="Greets you!")
async def greet(interaction: discord.Interaction):
  await interaction.response.send_message(f'👋🏻 Hey **{interaction.user.mention}**! How are you doing?')

@tree.command(name="ping", description="Returns latency of the client!")
async def ping(interaction: discord.Interaction):
  await interaction.response.send_message(f'🏓 Pong! **{round(client.latency *1000)}**ms.')

dice = ["1", "2", "3", "4", "5", "6"]

@tree.command(name="roll-dice", description="Rolls the dice!")
async def rolldice(interaction: discord.Interaction):
  await interaction.response.send_message(f'🎲 Dice rolled! You got **{random.choice(dice)}**!')

coin = ["heads", "tails"]

@tree.command(name="flip-a-coin", description="Flips a coin!")
async def flipacoin(interaction: discord.Interaction):
  await interaction.response.send_message(f'🪙 Coin flipped! You got **{random.choice(coin)}**!')

@tree.command(name="shards", description="Mentions the number of shards the bot is running!")
async def shards(interaction: discord.Interaction):
  await interaction.response.send_message(f"> 🟢 Discord.gateway is connected to **{client.shard_count}** Shard ID(s)!")

@tree.command(name="ask", description="Ask Byte a question!")
async def ask(interaction: discord.Interaction, question: str):
  response = genai.generate_text(
    model='models/text-bison-001',
    prompt=question,
    temperature=0.7,
    max_output_tokens=256,
    min_output_tokens=1,
  )
  await interaction.response.send_message(response.result)

@tree.command(name="echo", description="Echoes back the message!")
async def echo(interaction: discord.Interaction, message: str, password: int):
  if password != 11932:
    await interaction.response.send_message(f"**Wrong password!** Message not sent!", ephemeral=True)
    return
  await interaction.response.send_message(f"**Password matched!** Your message is sent by `Byte`!", ephemeral=True)
  await interaction.channel.send(message)

@tree.command(name="help", description="List all Slash Commands!")
async def help(interaction: discord.Interaction):
  await interaction.response.send_message(f"This `/command` is still under **development**!", ephemeral=True)

@tree.command(name="about", description="Information about Byte!")
async def about(interaction: discord.Interaction):
  await interaction.response.send_message(f"This `/command` is still under **development**!", ephemeral=True)


@tree.command(name="history", description="Conversation history all users have made with Byte so far!")
async def history(interaction: discord.Interaction, password: int):
  if password != 11932:
    await interaction.response.send_message(f"**Wrong password!** You are not _tahmidjahin_! Only **he** can see the history. Dialing **911**...", ephemeral=True)
    return
  await interaction.response.send_message(f"**Password matched!** Sending overall `conversation_history` with all `users`. <@895284024807923713>, you are requested to check your DM!", ephemeral=False)
  await interaction.user.send(conversation_history)
  
#slash-command ends

#Gemini
@client.event
async def on_message(message): 
  if message.author == client.user:
    return

  if '<@1045726218437263371>' not in message.content:
    return

  messages = message.content.replace('<@1045726218437263371>', '')

  if messages == '':
    await message.reply(f'Hey there {message.author.mention}! How can I help you today?')
    return


  msg = await message.reply(f'_Typing_')
  await asyncio.sleep(0.75)
  await msg.edit(content='_Typing._')
  await asyncio.sleep(0.75)
  await msg.edit(content='_Typing.._')
  await asyncio.sleep(0.75)
  await msg.edit(content='_Typing..._')

  
  user_id = str(message.author.id)
  if user_id not in conversation_history:
    conversation_history[user_id] = []

  conversation_history[user_id].append({"content": messages})

  # Get the messages for the current conversation
  messages = conversation_history[user_id]

  # Call the API to generate a response
  response = genai.chat(messages=messages, temperature=1, context='You are a discord bot named Byte. You are coded by Tahmid Jahin! Consider Tahmid Jahin as your papa/ father. If anyone asks who you are (or anything like this), you going to say "I am Byte, a discord bot! I am a large language model, also known as a conversational AI trained to be informative and comprehensive. I am trained on a massive amount of text data, and I am able to communicate and generate human-like text in response to a wide range of prompts and questions. I also support Slash Commands.".(nothing else. you got it? NOTHING ELSE EXCEPT THIS) If anyone asks you "who created you"(or anything like this), you going to say "I am developed by Tahmid Jahin".(nothing else. you can be creative a say this in different styles). If anyone asks about your mother, you are going to say that, "As my father is still unmarried, I have no mother. But I think soon I will have one." If anyone asks how you were born without a mother you are going to say, "That is the mystery!". Remember that you support SLash Commands.')

  
  # Get the last model response from the API
  model_response = response.last

  # Append the model's response to the conversation history
  conversation_history[user_id].append({"content": model_response})

  await msg.edit(content=model_response)
  
#Gemini-ends


my_secret = os.environ['TOKEN']
keep_alive()
client.run(os.getenv('TOKEN')) 



