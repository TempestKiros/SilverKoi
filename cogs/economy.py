import discord
from discord.ext import commands
from discord import Embed, Color
from database.mongo import (
    get_user_balance,
    add_user_koins,
    remove_user_koins,
    get_user_frames,
    add_user_frame,
    add_card_to_user,
    ensure_user
)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.frame_prices = {
            "N0": {"price": 100, "colors": ["#C0C0C0", "#FFFFFF", "#000000"], "name": "Básico"},
            "N1": {"price": 300, "colors": ["#800080", "#00FF00", "#FF0000"], "name": "Mezclado"},
            "N2": {"price": 500, "colors": ["#0037A4", "#FFD700", "#FF4500"], "name": "Radiante"},
            "N3": {"price": 1000, "colors": ["#A40A00", "#9400D3", "#00BFFF"], "name": "Especial"}
        }
        self.upgrade_costs = [50, 100, 200, 350, 500, 700, 1000, 1500, 2000]  # Costos por nivel de mejora

    @commands.command(name="balance", aliases=["bal", "koins"])
    async def balance_command(self, ctx, user: discord.Member = None):
        """Muestra el balance de koins de un usuario"""
        target = user or ctx.author
        balance = get_user_balance(str(target.id))
        
        embed = Embed(
            title=f"💰 Balance de {target.display_name}",
            description=f"**{balance}** koins",
            color=Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command(name="addkoins", aliases=["addk"])
    @commands.has_permissions(administrator=True)
    async def add_koins_command(self, ctx, amount: int, user: discord.Member = None):
        """Añade koins a un usuario (Solo admins)"""
        target = user or ctx.author
        add_user_koins(str(target.id), amount)
        
        embed = Embed(
            title="✅ Koins añadidos",
            description=f"Se añadieron {amount} koins a {target.mention}",
            color=Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="removekoins", aliases=["remk"])
    @commands.has_permissions(administrator=True)
    async def remove_koins_command(self, ctx, amount: int, user: discord.Member = None):
        """Remueve koins de un usuario (Solo admins)"""
        target = user or ctx.author
        current_balance = get_user_balance(str(target.id))
        
        if current_balance < amount:
            return await ctx.send("❌ El usuario no tiene suficientes koins.")
            
        remove_user_koins(str(target.id), amount)
        
        embed = Embed(
            title="✅ Koins removidos",
            description=f"Se removieron {amount} koins de {target.mention}",
            color=Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="buyframe", aliases=["comprar"])
    async def buy_frame_command(self, ctx, frame_type: str = None):
        """Compra marcos para tus cartas"""
        if not frame_type:
            return await self.show_available_frames(ctx)
            
        frame_type = frame_type.upper()
        if frame_type not in self.frame_prices:
            return await ctx.send(f"❌ Marco inválido. Usa `{ctx.prefix}buyframe` para ver opciones.")
            
        user_id = str(ctx.author.id)
        frame_data = self.frame_prices[frame_type]
        balance = get_user_balance(user_id)
        
        if balance < frame_data["price"]:
            return await ctx.send(f"❌ No tienes suficientes koins. Necesitas {frame_data['price']} (tienes {balance}).")
            
        # Verificar si ya tiene el marco
        user_frames = get_user_frames(user_id)
        if frame_type in user_frames:
            return await ctx.send("❌ Ya tienes este marco.")
            
        remove_user_koins(user_id, frame_data["price"])
        add_user_frame(user_id, frame_type)
        
        embed = Embed(
            title="✅ Marco comprado",
            description=f"Ahora tienes el marco **{frame_data['name']}** en tu colección.",
            color=Color.blue()
        )
        embed.add_field(name="Precio", value=f"{frame_data['price']} koins")
        embed.add_field(name="Balance restante", value=f"{balance - frame_data['price']} koins")
        embed.add_field(name="Colores disponibles", value=", ".join(frame_data["colors"]), inline=False)
        
        await ctx.send(embed=embed)

    async def show_available_frames(self, ctx):
        embed = Embed(
            title="🖼️ Marcos Disponibles",
            description=f"Usa `{ctx.prefix}buyframe [tipo]` para comprar\nEjemplo: `{ctx.prefix}buyframe N1`",
            color=Color.blurple()
        )
        
        for frame_type, data in self.frame_prices.items():
            embed.add_field(
                name=f"{frame_type} - {data['name']} ({data['price']} koins)",
                value="Colores: " + ", ".join(data["colors"]),
                inline=False
            )
            
        await ctx.send(embed=embed)

    @commands.command(name="frames", aliases=["marcos"])
    async def frames_command(self, ctx, user: discord.Member = None):
        """Muestra los marcos que has comprado"""
        target = user or ctx.author
        frames = get_user_frames(str(target.id))
        
        if not frames:
            return await ctx.send(f"❌ {target.display_name} no ha comprado ningún marco.")
            
        embed = Embed(
            title=f"🖼️ Marcos de {target.display_name}",
            color=Color.teal()
        )
        
        for frame_type in frames:
            frame_data = self.frame_prices.get(frame_type, {})
            embed.add_field(
                name=f"{frame_type} - {frame_data.get('name', 'Desconocido')}",
                value="Colores: " + ", ".join(frame_data.get("colors", ["#FFFFFF"])),
                inline=False
            )
            
        await ctx.send(embed=embed)

    @commands.command(name="upgrade", aliases=["mejorar"])
    async def upgrade_card_command(self, ctx, card_name: str):
        """Mejora una carta para aumentar sus estadísticas"""
        user_id = str(ctx.author.id)
        ensure_user(user_id)
        
        # Verificar si el usuario tiene la carta
        # (Implementación simplificada - necesitarías tu sistema de cartas)
        user_cards = []  # Aquí deberías obtener las cartas del usuario desde tu DB
        
        if card_name not in user_cards:
            return await ctx.send("❌ No tienes esta carta en tu colección.")
            
        # Obtener nivel actual de la carta
        card_level = 0  # Implementar lógica para obtener el nivel actual
        
        if card_level >= len(self.upgrade_costs):
            return await ctx.send("🎉 ¡Esta carta ya está al máximo nivel!")
            
        cost = self.upgrade_costs[card_level]
        balance = get_user_balance(user_id)
        
        if balance < cost:
            return await ctx.send(f"❌ Necesitas {cost} koins para esta mejora (tienes {balance}).")
            
        # Aplicar mejora
        remove_user_koins(user_id, cost)
        # Aquí iría la lógica para actualizar el nivel de la carta en tu DB
        
        embed = Embed(
            title="🛠️ Carta mejorada",
            description=f"¡{card_name} ha subido al nivel {card_level + 1}!",
            color=Color.green()
        )
        embed.add_field(name="Costo", value=f"{cost} koins")
        embed.add_field(name="Nuevo balance", value=f"{balance - cost} koins")
        embed.add_field(name="Siguiente mejora", value=f"{self.upgrade_costs[card_level + 1] if card_level + 1 < len(self.upgrade_costs) else 'MAX'} koins", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))