import discord
from discord.ext import commands
import os
import asyncio

# Configuración de intents
intents = discord.Intents.default()
intents.message_content = True

# Inicialización del bot
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("sk/", "&"),
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"✅ Silver Koi está conectado como {bot.user}")
    await bot.change_presence(activity=discord.Game(name="sk/help"))

async def load_cogs():
    """Carga todos los módulos desde la carpeta cogs"""
    for filename in os.listdir("./cogs"):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Módulo {filename} cargado correctamente")
            except Exception as e:
                print(f"❌ Error al cargar {filename}: {e}")

@bot.command()
async def sync(ctx):
    """Sincroniza los comandos con Discord (solo para admins)"""
    if ctx.author.guild_permissions.administrator:
        await bot.tree.sync()
        await ctx.send("✅ Comandos sincronizados")
    else:
        await ctx.send("❌ No tienes permisos para esto")

async def main():
    async with bot:
        await load_cogs()
        from config import TOKEN
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())