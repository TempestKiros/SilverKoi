import discord
from discord.ext import commands, tasks
import random
import asyncio
from characters.generator import get_random_character

class DropCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generate_drop.start()
        self.cooldowns = {}
        self.drop_pool = []

    def cog_unload(self):
        self.generate_drop.cancel()

    @tasks.loop(hours=2.5)
    async def generate_drop(self):
        self.drop_pool = [await get_random_character() for _ in range(4)]
        print("🃏 Nuevo set de cartas generado.")

    @commands.command(name="drop", aliases=["d"])
    async def manual_drop(self, ctx):
        now = asyncio.get_event_loop().time()
        user_id = str(ctx.author.id)
        last_drop_time = self.cooldowns.get(user_id, 0)
        if now - last_drop_time < 3600:
            await ctx.send(f"⏳ {ctx.author.display_name}, debes esperar antes de dropear una carta.")
            return
        self.cooldowns[user_id] = now
        cantidad = random.choices([1, 3, 4], weights=[65, 34, 1])[0]
        cartas = [await get_random_character() for _ in range(cantidad)]
        for carta in cartas:
            embed = discord.Embed(title=carta['name'], description=carta['series'])
            embed.set_image(url=carta['image'])
            await ctx.send(embed=embed)

    @commands.command(name="reclamar", aliases=["claim"])
    async def reclamar(self, ctx):
        now = asyncio.get_event_loop().time()
        user_id = str(ctx.author.id)
        last_claim_time = self.cooldowns.get(f"claim_{user_id}", 0)
        if now - last_claim_time < 1800:
            await ctx.send(f"⏳ {ctx.author.display_name}, debes esperar antes de reclamar una carta.")
            return
        self.cooldowns[f"claim_{user_id}"] = now
        if not self.drop_pool:
            await ctx.send("❌ No hay cartas disponibles para reclamar.")
            return
        carta = random.choice(self.drop_pool)
        embed = discord.Embed(title=carta['name'], description=carta['series'])
        embed.set_image(url=carta['image'])
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DropCog(bot))
