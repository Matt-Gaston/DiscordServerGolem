import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import yaml
import subprocess



# Load environment variables and config from .env file
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
APP_ID = os.getenv('APP_ID')
PUB_KEY = os.getenv('PUB_KEY')
PREFIX = os.getenv('PREFIX', '/')
AUTHORIZED_ROLE = os.getenv('AUTHORIZED_ROLE')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
tree = bot.tree
server_group = discord.app_commands.Group(name="server", description="Server management commands")


#helper functions

def has_role(member, role_name):
    return any(role.name==role_name for role in member.roles)

def get_services():
    with open('docker-compose.yml', 'r') as f:
        compose = yaml.safe_load(f)
    return list(compose.get('services', {}).keys())


# Commands

@server_group.command(name="ls", description="List all available servers to start/stop")
async def ls(interaction: discord.Interaction):
    if not has_role(interaction.user, AUTHORIZED_ROLE):
        return await interaction.response.send_message("❌ You do not have permission to run this command.")
    
    services = get_services()
    print(services)
    await interaction.response.send_message("Available servers:\n" + f"```\n{"\n".join(services)}\n```")

@server_group.command(name="status", description="Check the status of all servers")
async def status(interaction: discord.Interaction):
    if not has_role(interaction.user, AUTHORIZED_ROLE):
        return await interaction.response.send_message("❌ You do not have permission to run this command.")
    
    result = subprocess.run(['docker-compose', 'ps', '--format', '{{.Name}}\t{{.Status}}\t{{.Ports}}"'], capture_output=True, text=True)
    if result.returncode != 0:
        return await interaction.response.send_message(f"Error retrieving status:\n{result.stderr}")
    
    await interaction.response.send_message(f"Server status:\n```NAME                  STATUS                     PORTS\n{result.stdout}\n```")

@server_group.command(name="start", description="Start a specified server")
async def start(interaction: discord.Interaction, service: str):
    if not has_role(interaction.user, AUTHORIZED_ROLE):
        return await interaction.response.send_message("❌ You do not have permission to run this command.")
    
    services = get_services()
    if service not in services:
        return await interaction.response.send_message(f"❌ Server not found. Use /server ls to see available services.")
    
    await interaction.response.send_message(f"⏳ Starting server '{service}'...")
    
    result = subprocess.run(['docker-compose', 'up', '-d', service], capture_output=True, text=True)
    if result.returncode != 0:
        return await interaction.followup.edit_message(f"Error starting server")
    
    await interaction.followup(f"✅ Server '{service}' started successfully.")

@server_group.command(name="stop", description="Stop a specified server")
async def stop(interaction: discord.Interaction, service: str):
    if not has_role(interaction.user, AUTHORIZED_ROLE):
        return await interaction.response.send_message("❌ You do not have permission to run this command.")
    
    services = get_services()
    if service not in services:
        return await interaction.response.send_message(f"❌ Server not found. Use /server ls to see available services.")
    
    await interaction.response.send_message(f"⏳ Stopping server '{service}'...")
    
    result = subprocess.run(['docker-compose', 'down', service], capture_output=True, text=True)
    if result.returncode != 0:
        return await interaction.followup.send_message(f"Error stopping server")
    
    await interaction.followup.edit_message(f"✅ Server '{service}' stopped successfully.")



@bot.event
async def on_ready():
    tree.add_command(server_group)
    await tree.sync(guild=discord.Object(293528955854651392))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')



if __name__ == '__main__':
    bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)