import discord
from discord import app_commands
import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
import requests


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

cooldowns = {}


async def get_id(name):
  try:
      async with aiohttp.ClientSession() as session:
          response = await session.post('https://users.roblox.com/v1/usernames/users', json={
              'usernames': [name],
              'excludeBannedUsers': True
          })
          data = await response.json()
          if 'data' in data:
              return data['data'][0]['id']
  except Exception as err:
      print(err)
      return None

async def get_rolimons_data(user_id):
  try:
      async with aiohttp.ClientSession() as session:
          response = await session.get(f'https://www.rolimons.com/playerapi/player/{user_id}')
          data = await response.json()
          return data
  except Exception as err:
      print(err)
      return None

async def get_roblox_user_data(user_id):
  try:
      async with aiohttp.ClientSession() as session:
          response = await session.get(f'https://users.roblox.com/v1/users/{user_id}')
          data = await response.json()
          return data
  except Exception as err:
      print(err)
      return None

@client.event
async def on_ready():
  await tree.sync()
  print("Ready!")

@tree.command(name="test", description="Alt Generation Command")
async def alt_command(interaction):
  
  user_id = str(interaction.user.id)
  if user_id in cooldowns and datetime.utcnow() < cooldowns[user_id]:
      retry_after = (cooldowns[user_id] - datetime.utcnow()).seconds
      return await interaction.response.send_message(f"This command is on cooldown. Try again in {retry_after} seconds.")

  # Set cooldown change it to anything you want
  cooldowns[user_id] = datetime.utcnow() + timedelta(seconds=20)

  
  file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stock', 'test.txt')

  
  try:
      with open(file_path, "r") as file:
          lines = file.readlines()
  except FileNotFoundError:
      return await interaction.response.send_message(f"Error: '{file_path}' not found.")

  if not lines:
      
      embed_out_of_stock = discord.Embed(title="Out of stock",
                                         description="Sorry, we are out of stock. Please be patient and let us restock :(",
                                         colour=0xa2161d)
      return await interaction.response.send_message(embed=embed_out_of_stock)

  
  line = lines[0].strip()
  pro, noob = line.split(":")

  
  user_id_response = await get_id(pro)

  if not user_id_response:
      return await interaction.response.send_message("Error getting user ID from Roblox API.")

  
  rol_data = await get_rolimons_data(user_id_response)

  if not rol_data:
      return await interaction.response.send_message("Error getting data from Rolimons API.")

  
  roblox_data = await get_roblox_user_data(user_id_response)

  if not roblox_data:
      return await interaction.response.send_message("Error getting user data from Roblox API.")

  
  try:
      embed_dm = discord.Embed(title="Profile link",
                               url=f"https://www.roblox.com/users/{user_id_response}/profile",
                               colour=0x17fda5)

      embed_dm.add_field(name="Username", value=f"```{pro}```", inline=True)
      embed_dm.add_field(name="Password", value=f"```{noob}```", inline=True)
      embed_dm.add_field(name="Combo", value=f"```{line}```", inline=False)
      

      await interaction.user.send(embed=embed_dm)
  except discord.errors.Forbidden:
      return await interaction.response.send_message("Error: Could not send a DM to the user. Please ensure DMs are enabled.")

  
  embed_channel = discord.Embed(title="<:tick:1201594747173740654> Account sent in dms!",
                                description="Generated successfully",
                                colour=0x00b0f4,
                                timestamp=datetime.now())

  await interaction.response.send_message(embed=embed_channel)


  
  with open(file_path, "w") as file:
      file.writelines(lines[1:])


client.run(Token here)
