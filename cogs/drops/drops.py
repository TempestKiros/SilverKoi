import discord
from discord.ext import commands, tasks
import random
import asyncio
from economy.koins import get_balance, add_koins, ensure_user

class DropCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generate_drop.start()  # Iniciar generación de drops automáticos

        # Diccionario para controlar el cooldown de usuarios
        self.cooldowns = {}

    def cog_unload(self):
        self.generate_drop.cancel()

    drop_pool = []  # Pool de cartas generadas automáticamente

    @tasks.loop(hours=2.5)
    async def generate_drop(self):
        """Genera un set de 4 cartas cada 2h30min automáticamente."""
        self.drop_pool = [f"Carta {i}" for i in range(1, 5)]  # Simulamos con nombres genéricos
        print("🃏 Se generó un nuevo set de cartas para el drop.")

    @commands.command(name="drop", aliases=["d"])
    async def manual_drop(self, ctx):
        """Permite al usuario generar su propio drop cada 1h."""
        now = asyncio.get_event_loop().time()

        # Checkeo del cooldown
        user_id = str(ctx.author.id)
        last_drop_time = self.cooldowns.get(user_id, 0)
        if now - last_drop_time < 3600:  # 1 hora en segundos
            await ctx.send(f"⏳ {ctx.author.display_name}, debes esperar antes de dropear una carta.")
            return

        # Establecer tiempo del último drop
        self.cooldowns[user_id] = now

        cantidad = random.choices([1, 3, 4], weights=[65, 34, 1])[0]
        cartas = [f"Carta {random.randint(1, 100)}" for _ in range(cantidad)]
        await ctx.send(f"🎴 {ctx.author.display_name}, has dropeado: {', '.join(cartas)}")

    @commands.command(name="reclamar", aliases=["claim"])
    async def reclamar(self, ctx):
        """Permite reclamar una carta cada 30 minutos."""
        now = asyncio.get_event_loop().time()

        # Checkeo del cooldown de reclamación
        user_id = str(ctx.author.id)
        last_claim_time = self.cooldowns.get(f"claim_{user_id}", 0)
        if now - last_claim_time < 1800:  # 30 minutos en segundos
            await ctx.send(f"⏳ {ctx.author.display_name}, debes esperar antes de reclamar una carta.")
            return

        # Establecer el cooldown de reclamación
        self.cooldowns[f"claim_{user_id}"] = now
        carta = random.choice(self.drop_pool)  # Elegimos una carta aleatoria del pool generado
        await ctx.send(f"🎁 {ctx.author.display_name}, has reclamado: {carta}")

# Función setup fuera de la clase
async def setup(bot):
    await bot.add_cog(DropCog(bot))
