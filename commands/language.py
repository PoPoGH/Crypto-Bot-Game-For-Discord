import discord
import asyncio
from discord.ext import commands
from mysql_functions import create_connection, get_user_language, update_language
from language_manager import get_translator

class Language(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded!")  # Chargement du module Language

    def unload_cog(self):
        self.give_money.cancel()
        self.conn.close()
        print(f"{self.__class__.__name__} unloaded!")  # Déchargement du module Language

    @commands.command(name='language')  # Commande pour changer la langue
    async def change_language(self, ctx):
        user_id = ctx.author.id

        # Ouvrir et fermer la connexion à la base de données pour chaque opération
        conn, cursor = create_connection()
        user_language = get_user_language(conn, cursor, user_id)

        # Fermer la connexion après utilisation
        cursor.close()
        conn.close()

        # Obtenir l'objet de traduction
        translation = get_translator(user_language)

        # Créer un message demandant la nouvelle langue
        embed = discord.Embed(
            title=translation.gettext("Change Language"),  # Titre du message
            description=translation.gettext("Current Language:\n**{}**\n\nChoose a New Language:").format(user_language),  # Description affichée à l'utilisateur
            color=discord.Color.gold()  # Couleur de l'encart (or ici)
        )
        
        message = await ctx.send(embed=embed)
        await message.add_reaction('🇫🇷')
        await message.add_reaction('🇬🇧')
        await message.add_reaction('🇪🇸')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['🇫🇷', '🇬🇧', '🇪🇸'] and reaction.message.id == message.id

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            new_language = 'en'  # Anglais par défaut en cas de problème
            if reaction.emoji == '🇫🇷':
                new_language = 'fr'
            elif reaction.emoji == '🇬🇧':
                new_language = 'en'
            elif reaction.emoji == '🇪🇸':
                new_language = 'es'

            # Ouvrir une nouvelle connexion à la base de données pour mettre à jour la langue
            conn, cursor = create_connection()
            update_language(conn, cursor, user_id, new_language)  # Ajouter l'appel de fonction manquant
            cursor.close()
            conn.commit()  # S'assurer de valider la transaction
            conn.close()

            # Confirmer le changement de langue à l'utilisateur
            confirm_translation = get_translator(new_language)
            confirm_message = confirm_translation.gettext("Language changed to {}. Please restart any commands.").format(new_language)
            await ctx.send(confirm_message)
        except asyncio.TimeoutError:
            timeout_message = translation.gettext("You did not make a selection in time.")
            await ctx.send(timeout_message)
        
def setup(bot):
    bot.add_cog(Language(bot))
