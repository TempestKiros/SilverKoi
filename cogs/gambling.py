# cogs/gambling.py
import discord
from discord.ext import commands
import random
from database.mongo import get_user_balance, add_user_koins, remove_user_koins

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.slot_symbols = ["💎", "🍒", "🍋", "🍇", "🔔", "7️⃣"]
        self.user_games = {}  # {user_id: {"plays": 3, "last_play": timestamp}}

    @commands.command(name="gamble", aliases=["g", "tragaperras"])
    async def gamble_command(self, ctx):
        user_id = str(ctx.author.id)
        balance = get_user_balance(user_id)
        
        if balance < 10:
            await ctx.send("❌ Necesitas al menos 10 koins para jugar.")
            return
            
        # Verificar juegos disponibles
        if user_id not in self.user_games:
            self.user_games[user_id] = {"plays": 3, "last_play": 0}
            
        if self.user_games[user_id]["plays"] <= 0:
            await ctx.send("❌ No tienes más juegos disponibles hoy. Usa `sk/more` para recargar.")
            return
            
        # Generar resultado
        slots = [random.choice(self.slot_symbols) for _ in range(9)]
        result = self.check_slot_result(slots)
        
        # Actualizar balance
        if result["win"]:
            prize = 10 * (2 ** result["lines"])  # 20, 40, 80, etc.
            add_user_koins(user_id, prize)
            message = f"🎉 ¡Ganaste {prize} koins! ({result['lines']} líneas)"
        else:
            remove_user_koins(user_id, 10)
            message = "💸 Perdiste 10 koins. ¡Sigue intentando!"
            
        # Actualizar juegos restantes
        self.user_games[user_id]["plays"] -= 1
        self.user_games[user_id]["last_play"] = ctx.message.created_at.timestamp()
        
        # Mostrar resultado
        embed = discord.Embed(
            title="🎰 Tragaperras de SilverKoi",
            description=self.format_slot_board(slots),
            color=0xFFD700 if result["win"] else 0xFF0000
        )
        embed.add_field(name="Resultado", value=message)
        embed.add_field(name="Juegos restantes", value=str(self.user_games[user_id]["plays"]))
        embed.set_footer(text="Balance actual: {} koins".format(balance + (prize if result["win"] else -10)))
        
        await ctx.send(embed=embed)

    def check_slot_result(self, slots):
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontales
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Verticales
            [0, 4, 8], [2, 4, 6]              # Diagonales
        ]
        
        winning_lines = 0
        for line in lines:
            if slots[line[0]] == slots[line[1]] == slots[line[2]]:
                winning_lines += 1
                
        return {"win": winning_lines > 0, "lines": winning_lines}

    def format_slot_board(self, slots):
        return (
            f"╔═══╦═══╦═══╗\n"
            f"║ {slots[0]} ║ {slots[1]} ║ {slots[2]} ║\n"
            f"╠═══╬═══╬═══╣\n"
            f"║ {slots[3]} ║ {slots[4]} ║ {slots[5]} ║\n"
            f"╠═══╬═══╬═══╣\n"
            f"║ {slots[6]} ║ {slots[7]} ║ {slots[8]} ║\n"
            f"╚═══╩═══╩═══╝"
        )

    @commands.command(name="more", aliases=["recargar"])
    async def more_command(self, ctx):
        user_id = str(ctx.author.id)
        
        if user_id not in self.user_games:
            self.user_games[user_id] = {"plays": 3, "last_play": 0}
            
        last_play = self.user_games[user_id]["last_play"]
        current_time = ctx.message.created_at.timestamp()
        
        if (current_time - last_play) < 43200:  # 12 horas
            await ctx.send("⏳ Todavía no puedes recargar juegos. Espera 12 horas desde tu última jugada.")
            return
            
        self.user_games[user_id]["plays"] = 3
        await ctx.send("✅ Has recargado tus 3 juegos diarios.")

async def setup(bot):
    await bot.add_cog(Gambling(bot))