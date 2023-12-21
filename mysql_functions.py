import mysql.connector
import datetime
from mysql.connector import Error

# Fonction pour établir une connexion à la base de données MySQL
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="host",
            user="user",
            password="pass",
            database="db"
        )
        if conn.is_connected():
            print("Connexion à la base de données MySQL établie.")
            cursor = conn.cursor()
            return conn, cursor
    except Error as e:
        print(f"Erreur lors de la connexion à la base de données MySQL : {e}")
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
        print("Table des utilisateurs créée avec succès.")
    except Error as e:
        print(f"Erreur lors de la création de la table des utilisateurs : {e}")

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
        print(f"Utilisateur {discord_id} inséré avec succès avec une balance de {balance} et une langue de {language}.")
    except Error as e:
        print(f"Erreur lors de l'insertion de l'utilisateur {discord_id} : {e}")


# Fonction pour obtenir le solde d'un utilisateur
def get_balance(conn, cursor, discord_id):
    try:
        select_query = "SELECT balance FROM users WHERE discord_id = %s"
        cursor.execute(select_query, (discord_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except Error as e:
        print(f"Erreur lors de la récupération du solde de l'utilisateur {discord_id} : {e}")
    return 0.0

# Fonction pour mettre à jour le solde d'un utilisateur
def update_balance(conn, cursor, discord_id, new_balance):
    try:
        update_query = "UPDATE users SET balance = %s WHERE discord_id = %s"
        cursor.execute(update_query, (new_balance, discord_id))
        conn.commit()
        print(f"Solde de l'utilisateur {discord_id} mis à jour avec succès.")
    except Error as e:
        print(f"Erreur lors de la mise à jour du solde de l'utilisateur {discord_id} : {e}")

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
