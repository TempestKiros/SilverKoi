import discord
from discord.ext import commands
import os
import asyncio
from cogs.economy.koins import get_balance, add_koins, ensure_user

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("sk/", "&"), intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Silver Koi está conectado como {bot.user}")

@bot.command()
async def balance(ctx):
    ensure_user(str(ctx.author.id))
    balance = get_balance(str(ctx.author.id))
    await ctx.send(f"💰 {ctx.author.display_name}, tienes {balance} koins.")

@bot.command()
async def add(ctx, amount: int):
    ensure_user(str(ctx.author.id))
    add_koins(str(ctx.author.id), amount)
    await ctx.send(f"✅ Se te agregaron {amount} koins.")

async def load_cogs():
    for folder in ["drops", "economy", "gambling"]:
        for filename in os.listdir(f'./{folder}'):
            if filename.endswith('.py'):
                await bot.load_extension(f'{folder}.{filename[:-3]}')

async def main():
    async with bot:
        await load_cogs()
        from config import TOKEN
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
