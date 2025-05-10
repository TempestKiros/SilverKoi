import discord
from discord.ext import commands
from discord import Embed, Color

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "❓"  # Emoji para el embed

    @commands.command(name="help", aliases=['h'])
    async def help_command(self, ctx, *, command_name: str = None):
        """Muestra todos los comandos disponibles o ayuda sobre un comando específico"""
        if command_name:
            # Ayuda para un comando específico
            await self.show_command_help(ctx, command_name)
        else:
            # Ayuda general
            await self.show_all_help(ctx)

    async def show_all_help(self, ctx):
        """Muestra el menú de ayuda principal"""
        embed = Embed(
            title=f"{self.emoji} SilverKoi - Sistema de Ayuda",
            description="Aquí tienes todos los comandos disponibles. Usa `sk/help [comando]` para más detalles.",
            color=Color.blurple()
        )
        
        # Agrupar comandos por cog
        for cog_name in self.bot.cogs:
            cog = self.bot.get_cog(cog_name)
            commands_list = cog.get_commands()
            
            if commands_list:  # Solo mostrar cogs con comandos
                value = "\n".join(f"`{cmd.name}` - {cmd.short_doc or 'Sin descripción'}" for cmd in commands_list)
                embed.add_field(
                    name=f"**{cog_name.upper()}**",
                    value=value,
                    inline=False
                )

        embed.set_footer(text=f"Pedido por {ctx.author.display_name}")
        await ctx.send(embed=embed)

    async def show_command_help(self, ctx, command_name):
        """Muestra ayuda detallada para un comando específico"""
        command = self.bot.get_command(command_name.lower())
        
        if not command:
            return await ctx.send(f"⚠️ Comando `{command_name}` no encontrado. Usa `sk/help` para ver la lista.")
        
        embed = Embed(
            title=f"ℹ️ Ayuda para `{command.name}`",
            color=Color.gold()
        )
        
        embed.add_field(
            name="Descripción",
            value=command.help or "No hay descripción disponible",
            inline=False
        )
        
        if command.aliases:
            embed.add_field(
                name="Alias",
                value=", ".join(f"`{alias}`" for alias in command.aliases),
                inline=False
            )
        
        if isinstance(command, commands.Group):
            subcommands = "\n".join(f"`{sub.name}` - {sub.short_doc}" for sub in command.commands)
            embed.add_field(
                name="Subcomandos",
                value=subcommands,
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))