import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import aiohttp  # Changed from requests to aiohttp for async support
import asyncio
import asyncio

# ----------------- SWEAR WORD FILTER -----------------
list1 = ['shit', 'fuck', 'cum', 'dick', 'ass', 'cock', 'bitch']
secret_role = "Regal Daddy"

# ----------------- LOAD TOKENS -----------------
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
replicate_token = os.getenv('REPLICATE_API_TOKEN')

# ----------------- LOGGING -----------------
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# ----------------- DISCORD INTENTS -----------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ----------------- DISCORD EVENTS -----------------
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    try:
        await member.send(f"Welcome to the server {member.name}")
    except discord.Forbidden:
        pass
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"{member.mention} Welcome to the group!")

@bot.event
async def on_member_remove(member):
    try:
        await member.send(f"You left the server {member.name}")
    except discord.Forbidden:
        pass
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"{member.mention} left the group!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    for word in list1:
        if word in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention}, never say that - it is derogatory")
            return
    await bot.process_commands(message)

# ----------------- BOT COMMANDS -----------------
@bot.command()
async def hi(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def bye(ctx):
    await ctx.send(f"Screw off {ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned {secret_role}")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} is now removed {secret_role}")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send(f"Welcome {ctx.author.mention}")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have permission.")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said: {msg}")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
async def reply(ctx, *, msg):
    if msg.lower() == 'sigma':
        await ctx.reply("boy, sigma boy")
    else:
        await ctx.reply("This is a reply")

# ----------------- CLAUDE COMMAND -----------------
@bot.command()
async def claude(ctx, *, prompt):
    """Send a prompt to Claude and return the result."""
    thinking_msg = await ctx.send("Thinking... ⏳")
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "http://localhost:6700/chat",
                json={"query": prompt},  # Fixed: use 'prompt' instead of undefined 'user_input'
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    reply = await response.text()  # <--- instead of .json()
                else:
                    reply = f"API error: Status {response.status}"
                    
        # Delete the "thinking" message and send the actual response
        await thinking_msg.delete()
        
        # Discord messages have a 2000 character limit
        if len(reply) > 2000:
            # Split long responses
            for i in range(0, len(reply), 2000):
                await ctx.send(reply[i:i+2000])
        else:
            await ctx.send(reply)
            
    except asyncio.TimeoutError:
        await thinking_msg.edit(content="Claude took too long to respond (timeout).")
    except aiohttp.ClientError as e:
        await thinking_msg.edit(content=f"Connection error: {str(e)}")
    except Exception as e:
        await thinking_msg.edit(content=f"An error occurred: {str(e)}")

# ----------------- RUN BOT -----------------
bot.run(token, log_handler=handler, log_level=logging.DEBUG)