import mysql.connector
import datetime
from mysql.connector import Error
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

DEBUG_MODE = False  # Activez ou désactivez le mode de débogage

# Fonction pour établir une connexion à la base de données MySQL login dans le config.py
def create_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if conn.is_connected():
            if DEBUG_MODE:
                print("Connection to MySQL database established.")
            cursor = conn.cursor()
            return conn, cursor
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return None, None

# Fonction pour créer la table des utilisateurs (à exécuter une seule fois)
def create_users_table(conn, cursor):
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            discord_id BIGINT,
            balance DECIMAL(10, 2) DEFAULT 0.0
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        if DEBUG_MODE:
            print("Users table created successfully.")
    except Error as e:
        print(f"Error creating users table: {e}")

# Fonction pour insérer un nouvel utilisateur dans la table avec des informations supplémentaires
import datetime  # Importez le module datetime

# Fonction pour insérer un nouvel utilisateur dans la table
def insert_user(conn, cursor, discord_id, balance, language):
    try:
        # Obtenez la date actuelle au format YYYY-MM-DD HH:MM:SS
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Modifiez la requête SQL pour insérer toutes les informations
        insert_query = "INSERT INTO users (discord_id, balance, created_at, language) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (discord_id, balance, current_date, language))
        conn.commit()
        if DEBUG_MODE:
            print(f"User {discord_id} successfully inserted with a balance of {balance} and a language of {language}.")
    except Error as e:
        print(f"Error inserting user {discord_id}: {e}")


# Fonction pour obtenir le solde d'un utilisateur
def get_balance(conn, cursor, discord_id):
    try:
        select_query = "SELECT balance FROM users WHERE discord_id = %s"
        cursor.execute(select_query, (discord_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except Error as e:
        print(f"Error retrieving balance for user {discord_id}: {e}")
    return 0.0

# Fonction pour mettre à jour le solde d'un utilisateur
def update_balance(conn, cursor, discord_id, new_balance):
    try:
        update_query = "UPDATE users SET balance = %s WHERE discord_id = %s"
        cursor.execute(update_query, (new_balance, discord_id))
        conn.commit()
        if DEBUG_MODE:
            print(f"Balance of user {discord_id} updated successfully.")
    except Error as e:
        print(f"Error updating balance of user {discord_id}: {e}")

def user_exists(conn, cursor, discord_id):
    select_query = "SELECT * FROM users WHERE discord_id = %s"
    cursor.execute(select_query, (discord_id,))
    result = cursor.fetchone()
    return result is not None

def get_all_users(conn, cursor):
    select_query = "SELECT discord_id, balance, language FROM users"
    cursor.execute(select_query)
    result = cursor.fetchall()
    return result

def update_language(conn, cursor, discord_id, new_language):
    try:
        update_query = "UPDATE users SET language = %s WHERE discord_id = %s"
        cursor.execute(update_query, (new_language, discord_id))
        conn.commit()
        if DEBUG_MODE:
            print(f"Language of user {discord_id} updated to {new_language} successfully.")
    except Error as e:
        print(f"Error updating language of user {discord_id}: {e}")
        
def get_user_language(conn, cursor, discord_id):
    try:
        select_query = "SELECT language FROM users WHERE discord_id = %s"
        cursor.execute(select_query, (discord_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 'en'  # Retourne 'en' par défaut si aucune langue n'est définie
    except Error as e:
        print(f"Error retrieving user {discord_id}'s language: {e}")
        return 'en'  # Retourne 'en' par défaut en cas d'erreur
    
def get_user_language_no_fall(conn, cursor, discord_id):
    try:
        select_query = "SELECT language FROM users WHERE discord_id = %s"
        cursor.execute(select_query, (discord_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("{discord_id} none")
            return 'none'  # Retourne 'en' par défaut si aucune langue n'est définie
    except Error as e:
        print(f"Error retrieving user {discord_id}'s language: {e}")
        return 'none'  # Retourne 'en' par défaut en cas d'erreur
