import discord
from discord.ext import commands
import random
import asyncio
from cogs.economy.koins import get_balance, add_koins, ensure_user

class GamblingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.plays = {}

    @commands.command(name="g", aliases=["gambling"])
    async def gambling(self, ctx):
        user_id = str(ctx.author.id)
        ensure_user(user_id)
        balance = get_balance(user_id)
        if balance < 10:
            await ctx.send("❌ No tienes suficientes koins para jugar.")
            return
        symbols = ['🗿', '💲']
        grid = [[random.choice(symbols) for _ in range(4)] for _ in range(4)]
        lines = grid + list(map(list, zip(*grid)))  # filas y columnas
        diagonals = [[grid[i][i] for i in range(4)], [grid[i][3 - i] for i in range(4)]]
        lines += diagonals
        points = sum(1 for line in lines if line.count(line[0]) == 4 and line[0] == '💲')
        reward = points * 5
        add_koins(user_id, reward - 10)  # costo de jugar es 10
        grid_display = '\n'.join([''.join(row) for row in grid])
        await ctx.send(f"🎰 Resultado:\n{grid_display}\nPuntos: {points}\nGanancia: {reward - 10} koins")

    @commands.command(name="mo", aliases=["more"])
    async def more(self, ctx):
        # Implementar recarga de jugadas
        await ctx.send("🔄 Función de recarga aún no implementada.")

    @commands.command(name="r", aliases=["ranking"])
    async def ranking(self, ctx):
        # Implementar ranking
        await ctx.send("📊 Función de ranking aún no implementada.")

async def setup(bot):
    await bot.add_cog(GamblingCog(bot))
