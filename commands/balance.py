import decimal
import discord
from discord.ext import commands
from mysql_functions import create_connection, get_balance, get_user_language
from language_manager import get_translator

class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded!")

    def unload_cog(self):
        self.give_money.cancel()
        self.conn.close()
        print(f"{self.__class__.__name__} unloaded!")

    @commands.command(name="balance", aliases=['b'])
    async def balance(self, ctx):
        user_id = ctx.author.id

        # Assurez-vous d'ouvrir et de fermer la connexion pour chaque opération de base de données
        conn, cursor = create_connection()
        user_balance = get_balance(conn, cursor, user_id)

        # Obtenez la langue de l'utilisateur depuis la base de données
        user_language = get_user_language(conn, cursor, user_id)

        # Fermez la connexion après utilisation
        cursor.close()
        conn.close()

        # Utilisez le gestionnaire de langue pour obtenir l'objet de traduction
        translation = get_translator(user_language)

        # Créez un objet Embed
        embed = discord.Embed(
            title=translation.gettext("Balance"),
            description=translation.gettext("balance_balance").format(decimal.Decimal(user_balance).quantize(decimal.Decimal('0.000001'))),
            color=discord.Color.blue()  # Couleur de l'embed (bleu ici)
        )

        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Balance(bot))
