import os
import discord
import asyncio
from discord.ext import commands
from config import TOKEN
from mysql_functions import create_connection, user_exists, insert_user


# Définissez votre token dans le config.py
TOKEN = TOKEN

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True

class CryptoBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.conn, self.cursor = create_connection()
        self.economy_loaded = False  # Variable pour suivre si l'extension 'Economy' est chargée

    async def setup_hook(self):
        # Chargez l'extension 'Economy' uniquement si elle n'est pas déjà chargée
        if not self.economy_loaded:
            from economy import Economy
            await self.add_cog(Economy(self))
            self.economy_loaded = True

bot = CryptoBot()

@bot.event
async def on_message(message):
    # Assurez-vous que le message n'est pas envoyé par le bot lui-même
    if message.author.bot:
        return

    # Vérifiez si le message commence par le préfixe de commande
    if message.content.startswith("!"):
        # Vérifiez si l'utilisateur existe dans la base de données
        user_id = message.author.id
        if not user_exists(bot.conn, bot.cursor, user_id):
            # Si l'utilisateur n'existe pas, demandez-lui de créer un compte avec la commande !start
            print(f"User {user_id} does not exist in the database. Prompting to create an account.")
            await message.channel.send(f"{message.author.mention}, you need to create an account first. Use `!start` to begin.")
            return
    
    # Si l'utilisateur existe dans la base de données ou a créé un compte, continuez à traiter la commande
    await bot.process_commands(message)

@bot.command(name="start")
async def start(ctx):
    user_id = ctx.author.id
    conn, cursor = create_connection()
    if not user_exists(conn, cursor, user_id):
        print(f"User {user_id} is starting the account creation process.")
        await ctx.send(f"Welcome, {ctx.author.mention}! Please choose your language:")
        embed = discord.Embed(
            title="Choose Your Language",
            description="React with 🇫🇷 for French\nReact with 🇬🇧 for English\nReact with 🇪🇸 for Spanish",
            color=discord.Color.blue()
        )
        start_message = await ctx.send(embed=embed)
        await start_message.add_reaction("🇫🇷")
        await start_message.add_reaction("🇬🇧")
        await start_message.add_reaction("🇪🇸")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["🇫🇷", "🇬🇧", "🇪🇸"]

        try:
            reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            language = None
            if reaction.emoji == "🇫🇷":
                language = "fr"
            elif reaction.emoji == "🇬🇧":
                language = "en"
            elif reaction.emoji == "🇪🇸":
                language = "es"
            
            if language:
                # Ajoutez l'utilisateur à la base de données avec la langue choisie en utilisant la fonction insert_user
                insert_user(conn, cursor, user_id, 0.0, language)  # Balance initialisée à 0.0
                print(f"User {user_id} has created an account with language {language}.")
                await ctx.send(f"You have selected {language} as your language.")
            else:
                print(f"User {user_id} made an invalid selection.")
                await ctx.send("Invalid selection. Please use the `!start` command again.")
        except asyncio.TimeoutError:
            print(f"User {user_id} did not make a selection in time.")
            await ctx.send("You didn't make a selection. Please use the `!start` command again.")
        
        conn.close()

@bot.event
async def on_ready():
    print(f"Connected as {bot.user.name}")
    await bot.setup_hook()

if __name__ == "__main__":
    bot.run(TOKEN)
