import decimal
import discord
from discord.ext import commands, tasks
from mysql_functions import create_connection, create_users_table, get_all_users, update_balance, get_balance

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn, self.cursor = create_connection()
        create_users_table(self.conn, self.cursor)
        self.give_money.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded!")

    def unload_cog(self):  # Renommez cette méthode
        self.give_money.cancel()
        self.conn.close()
        print(f"{self.__class__.__name__} unloaded!")

    @tasks.loop(seconds=1.5)
    async def give_money(self):
        all_users = get_all_users(self.conn, self.cursor)
        for user in all_users:
            user_id, balance, _ = user
            new_balance = balance + decimal.Decimal('0.00001')  # Convertir 0.00001 en decimal.Decimal
            print(f"Updating balance for user {user_id}...")
            print(f"Old balance: {balance:.6f}, New balance: {new_balance:.6f}")  # Ajoutez cette ligne pour vérifier les valeurs
            update_balance(self.conn, self.cursor, user_id, new_balance)
            print(f"Updated balance for user {user_id}. New balance: {new_balance:.6f}")
    

    @commands.command(name="balance", aliases=['b'])
    async def balance(self, ctx):
        user_id = ctx.author.id
        user_balance = get_balance(self.conn, self.cursor, user_id)
        await ctx.send(f"Your balance is {user_balance:.6f} BitCoin.")

def setup(bot):
    bot.add_cog(Economy(bot))
