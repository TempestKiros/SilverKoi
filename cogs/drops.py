# cogs/drops.py
import discord
from discord.ext import commands, tasks
import random
import asyncio
from database.mongo import add_card_to_user

EMOJI_NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

class Drops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.drop_cooldowns = {}
        self.active_drops = {}
        self.character_pool = self.load_character_pool()

    def load_character_pool(self):
        # Implementa tu generador de personajes o carga desde JSON
        return [
            {"name": "Goku", "series": "Dragon Ball", "image": "https://example.com/goku.jpg", "rarity": "R"},
            {"name": "Naruto", "series": "Naruto", "image": "https://example.com/naruto.jpg", "rarity": "SR"}
        ]

    async def get_random_character(self):
        weights = {
            "R": 70,
            "SR": 25,
            "SSR": 5
        }
        character = random.choice(self.character_pool)
        character["rarity"] = random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
        return character

    @commands.command(name="drop", aliases=["d"])
    async def drop_command(self, ctx):
        user_id = str(ctx.author.id)
        
        # Verificar cooldown
        if user_id in self.drop_cooldowns:
            remaining = self.drop_cooldowns[user_id] - ctx.message.created_at.timestamp()
            if remaining > 0:
                await ctx.send(f"⏳ Espera {int(remaining)} segundos antes de usar otro drop.")
                return
        
        # Determinar cantidad de cartas
        cantidad = random.choices([1, 3, 4], weights=[65, 34, 1])[0]
        cartas = [await self.get_random_character() for _ in range(cantidad)]
        
        # Mostrar cartas
        messages = []
        for i, carta in enumerate(cartas):
            embed = self.create_card_embed(carta, i+1)
            msg = await ctx.send(embed=embed)
            await msg.add_reaction(EMOJI_NUMBERS[i])
            messages.append((msg, carta))
        
        self.active_drops[user_id] = messages
        self.drop_cooldowns[user_id] = ctx.message.created_at.timestamp() + 3600  # 1 hora cooldown

    def create_card_embed(self, card, index):
        embed = discord.Embed(
            title=f"{card['name']} ({card['rarity']})",
            description=f"De: {card['series']}",
            color=self.get_rarity_color(card['rarity'])
        )
        embed.set_image(url=card['image'])
        embed.set_footer(text=f"Reacciona con {EMOJI_NUMBERS[index-1]} para reclamar")
        return embed

    def get_rarity_color(self, rarity):
        colors = {
            "R": 0x00FF00,    # Verde
            "SR": 0x0000FF,   # Azul
            "SSR": 0xFF00FF   # Morado
        }
        return colors.get(rarity, 0xFFFFFF)

    @commands.command(name="claim", aliases=["reclamar"])
    async def claim_command(self, ctx):
        user_id = str(ctx.author.id)
        
        if user_id not in self.active_drops:
            await ctx.send("❌ No tienes drops activos para reclamar.")
            return
            
        messages = self.active_drops[user_id]
        await ctx.send("✋ Reacciona a la carta que deseas reclamar (tienes 30 segundos):")

        def check(reaction, user):
            return (
                user == ctx.author and
                str(reaction.emoji) in EMOJI_NUMBERS and
                any(reaction.message.id == msg.id for msg, _ in messages)
            )

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            index = EMOJI_NUMBERS.index(str(reaction.emoji))
            selected_card = messages[index][1]
            
            # Guardar en MongoDB
            add_card_to_user(user_id, selected_card)
            
            # Eliminar mensajes
            for msg, _ in messages:
                await msg.delete()
                
            del self.active_drops[user_id]
            
            embed = discord.Embed(
                title=f"🎉 ¡Has reclamado a {selected_card['name']}!",
                description=f"Ahora forma parte de tu colección.",
                color=self.get_rarity_color(selected_card['rarity'])
            )
            await ctx.send(embed=embed)
            
        except asyncio.TimeoutError:
            await ctx.send("⏰ Tiempo agotado. No se reclamó ninguna carta.")

async def setup(bot):
    await bot.add_cog(Drops(bot))