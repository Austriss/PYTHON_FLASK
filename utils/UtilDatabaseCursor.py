import sqlite3

class UtilDatabaseCursor:
    def __init__(self):
        super().__init__()
        self.connection = sqlite3.connect("./blog.sqlite")
        self.cursor = None

    def __enter__(self): #with instance as something
        self.connection.__enter__()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.__exit__(exc_type, exc_val, exc_tb)
