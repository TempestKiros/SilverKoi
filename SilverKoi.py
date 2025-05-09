import discord
from discord.ext import commands, tasks
import os
import asyncio
import random

from cogs.economy.koins import get_balance, add_koins, ensure_user

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="sk/", intents=intents)

# Cargar cogs (módulos)
for folder in ["cogs/drops", "cogs/economy"]:
    for filename in os.listdir(folder):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{folder.split("/")[-1]}.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f"✅ Silver Koi está conectado como {bot.user}")
    for command in bot.commands:
        print(f"Comando cargado: {command.name}")
    
    try:
        await bot.load_extension('cogs.drops')
        print("Cog 'drops' cargado con éxito.")
    except Exception as e:
        print(f"Error al cargar el cog 'drops': {e}")

# Comando balance
@bot.command()
async def balance(ctx):
    """Muestra el balance actual del usuario."""
    ensure_user(str(ctx.author.id))
    balance = get_balance(str(ctx.author.id))
    await ctx.send(f"💰 {ctx.author.display_name}, tienes {balance} koins.")

# Comando add (solo pruebas)
@bot.command()
async def add(ctx, amount: int):
    """(Solo pruebas) Agrega koins al usuario."""
    ensure_user(str(ctx.author.id))
    add_koins(str(ctx.author.id), amount)
    await ctx.send(f"✅ Se te agregaron {amount} koins.")

# Aquí va el comando de drops (lo que creamos en el cog 'drops')

if __name__ == "__main__":
    from config import TOKEN
    bot.run(TOKEN)
