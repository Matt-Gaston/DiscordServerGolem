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
AUTHORIZED_ROLE = os.getenv('AUTHORIZED_ROLE', 'Butthouse')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    # await bot.tree.sync()


#helper functions

def has_role(member, role_name):
    return any(role.name==role_name for role in member.roles)

def get_services():
    with open('docker-compose.yml', 'r') as f:
        compose = yaml.safe_load(f)
    return list(compose.get('services', {}).keys())




# Commands

@bot.group()
async def server(ctx):
    if not has_role(ctx.author, AUTHORIZED_ROLE):
        return await ctx.send("❌ You do not have permission to run this command.")
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid command. Use /server help for available commands.')

@server.command()
async def ls(ctx):
    if not has_role(ctx.author, AUTHORIZED_ROLE):
        return await ctx.send("❌ You do not have permission to run this command.")
    
    services = get_services()
    print(services)
    await ctx.send("Available servers:\n" + f"```\n{"\n".join(services)}\n```")

@server.command()
async def status(ctx):
    if not has_role(ctx.author, AUTHORIZED_ROLE):
        return await ctx.send("❌ You do not have permission to run this command.")
    
    result = subprocess.run(['docker-compose', 'ps', '--format', '{{.Name}}\t{{.Status}}\t{{.Ports}}"'], capture_output=True, text=True)
    if result.returncode != 0:
        return await ctx.send(f"Error retrieving status:\n{result.stderr}")
    
    await ctx.send(f"Server status:\n```NAME                  STATUS                     PORTS\n{result.stdout}\n```")

@server.command()
async def start(ctx, service: str):
    if not has_role(ctx.author, AUTHORIZED_ROLE):
        return await ctx.send("❌ You do not have permission to run this command.")
    
    services = get_services()
    if service not in services:
        return await ctx.send(f"❌ Server not found. Use /server ls to see available services.")
    
    await ctx.send(f"⏳ Starting server '{service}'...")
    
    result = subprocess.run(['docker-compose', 'up', '-d', service], capture_output=True, text=True)
    if result.returncode != 0:
        return await ctx.send(f"Error starting server")
    
    await ctx.send(f"✅ Server '{service}' started successfully.")

@server.command()
async def stop(ctx, service: str):
    if not has_role(ctx.author, AUTHORIZED_ROLE):
        return await ctx.send("❌ You do not have permission to run this command.")
    
    services = get_services()
    if service not in services:
        return await ctx.send(f"❌ Server not found. Use /server ls to see available services.")
    
    await ctx.send(f"⏳ Stopping server '{service}'...")
    
    result = subprocess.run(['docker-compose', 'down', service], capture_output=True, text=True)
    if result.returncode != 0:
        return await ctx.send(f"Error stopping server")
    
    await ctx.send(f"✅ Server '{service}' stopped successfully.")


if __name__ == '__main__':
    bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)