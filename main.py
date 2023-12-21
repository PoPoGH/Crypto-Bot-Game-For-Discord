import os
import discord
import asyncio
from discord.ext import commands
from config import TOKEN, PREFIX
from mysql_functions import create_connection, user_exists, insert_user, update_language, get_user_language
from language_manager import get_translator

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True

class CryptoBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=self.get_custom_prefix, intents=intents)
        self.economy_loaded = False  # Variable pour suivre si l'extension 'Economy' est chargée
        
    async def get_custom_prefix(self, bot, message):
        # Utilise la variable de préfixe de ton fichier de configuration
        return PREFIX
    
    async def setup_hook(self):
        # Charge l'extension 'Economy' seulement si elle n'est pas déjà chargée
        if not self.economy_loaded:
            from economy import Economy
            await self.add_cog(Economy(self))
            from commands.balance import Balance
            await self.add_cog(Balance(self))
            from commands.language import Language
            await self.add_cog(Language(self))
            self.economy_loaded = True
    
    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        custom_prefix = await self.get_custom_prefix(self, message)
        if not message.content.startswith(custom_prefix):
            return

        conn, cursor = create_connection()
        user_id = str(message.author.id)

        if not user_exists(conn, cursor, user_id):
            # Si l'utilisateur n'est pas dans la base de données, demande-lui de choisir une langue.
            welcome_message = await ctx.send("Welcome! Please choose your language:")
            lang_message = await ctx.send("React with 🇫🇷 for French\nReact with 🇬🇧 for English\nReact with 🇪🇸 for Spanish")
            await lang_message.add_reaction('🇫🇷')
            await lang_message.add_reaction('🇬🇧')
            await lang_message.add_reaction('🇪🇸')

            def check(reaction, user):
                return user == message.author and str(reaction.emoji) in ['🇫🇷', '🇬🇧', '🇪🇸'] and reaction.message.id == lang_message.id

            try:
                reaction, user = await self.wait_for('reaction_add', timeout=60.0, check=check)

                language = 'en'  # Définit une langue par défaut au cas où quelque chose se passe mal.
                if reaction.emoji == '🇫🇷':
                    language = 'fr'
                elif reaction.emoji == '🇬🇧':
                    language = 'en'
                elif reaction.emoji == '🇪🇸':
                    language = 'es'

                insert_user(conn, cursor, user_id, 0.0, language)
                await ctx.send(f"Your language is set to {language}.")  # Votre langue est définie sur {language}.
            except asyncio.TimeoutError:
                await ctx.send("You did not respond in time.")  # Vous n'avez pas répondu à temps.

            conn.close()
        else:
            # Si l'utilisateur est dans la base de données, exécute la commande normalement.
            await self.process_commands(message)
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandError) and "User not registered" in str(error):
            # L'utilisateur n'est pas enregistré, envoie-lui un message et bloque la commande
            await ctx.send("Please choose your language and register using !start.")  # Veuillez choisir votre langue et vous enregistrer en utilisant !start.

bot = CryptoBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté à Discord !")  # {bot.user.name} est connecté à Discord !

if __name__ == "__main__":
    bot.run(TOKEN)
