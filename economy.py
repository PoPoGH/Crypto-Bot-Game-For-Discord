import decimal
import discord
import asyncio
from discord.ext import commands, tasks
from mysql_functions import create_connection, create_users_table, get_all_users, update_balance, get_user_language, update_language
from language_manager import get_translator

DEBUG_MODE = False  # Activez ou désactivez le mode de débogage

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn, self.cursor = create_connection()
        create_users_table(self.conn, self.cursor)
        self.give_money.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} loaded!")

    def unload_cog(self):
        self.give_money.cancel()
        self.conn.close()
        print(f"{self.__class__.__name__} unloaded!")

    @tasks.loop(seconds=1.5)
    async def give_money(self):
        try:
            all_users = get_all_users(self.conn, self.cursor)
            for user in all_users:
                user_id, balance, _ = user
                new_balance = balance + decimal.Decimal('0.00001')
                if DEBUG_MODE:
                    print(f"Updating balance for user {user_id}...")
                    print(f"Old balance: {balance:.6f}, New balance: {new_balance:.6f}")
                update_balance(self.conn, self.cursor, user_id, new_balance)
                if DEBUG_MODE:
                    print(f"Updated balance for user {user_id}. New balance: {new_balance:.6f}")
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
    
def setup(bot):
    bot.add_cog(Economy(bot))
