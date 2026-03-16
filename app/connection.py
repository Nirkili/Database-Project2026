from config import Config
import mysql.connector

class connection:
    def __init__(self):
        self.conn = mysql.connector.connect(
        host = Config.DB_HOST, 
        user = Config.DB_USER, 
        password = Config.DB_PASSWORD, 
        database = Config.DB_NAME)
        
        self.cursor = self.conn.cursor()