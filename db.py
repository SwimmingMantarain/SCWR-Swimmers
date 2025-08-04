import sqlite3

class DB:
    def __init__(self, db_name="scwr.sql"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def init_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS scwr_swimmers (
            id INTEGER PRIMARY KEY,
            sw_id INTEGER,
            birth_year INTEGER,
            first_name TEXT,
            last_name TEXT,
            gender INTEGER
        )
        """

        self.cursor.execute(query)

        query = """
        PRAGMA foreign_keys = ON;
        """
        self.cursor.execute(query);

        query = """
        CREATE TABLE IF NOT EXISTS swimmer_pbs (
            id INTEGER PRIMARY KEY,
            course INTEGER,
            distance INTEGER,
            stroke TEXT,

            swimmer_sql_id INTEGER NOT NULL,
            FOREIGN KEY(swimmer_sql_id) REFERENCES swimmers(id)
        )
        """
        self.cursor.execute(query)

    def commit(self):
        self.conn.commit()
    
    def insert_into(self, table: str, cols: str | None = None, values: str | None = None):
        if not cols:
            raise ValueError(
                f'\033[31m\033[34m[INTERNAL DB ERROR]\033[0m: `You need to know where you are adding stuff!`'
            )
        elif not values:
            raise ValueError(
                f'\033[31m\033[34m[INTERNAL DB ERROR]\033[0m: `You need to know what stuff you are adding!`'
            )

        query = f"INSERT INTO {table}({cols}) VALUES({values});"

        try:
            self.cursor.execute(query)

        except sqlite3.OperationalError as e:
            print(f'\033[31m\033[34m[SQLITE ERROR]\033[0m: `{e}`')
            return None


    def exists_in(self, table: str, sql_filter: str | None = None):
        if not sql_filter:
            raise ValueError(
                f'\033[31m\033[34m[INTERNAL DB ERROR]\033[0m: `You need to know what you are looking for!`'
            )

        query = f"SELECT * FROM {table} WHERE {sql_filter};"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        if result:
            return 1
        return 0

    def get_all_from(self, table: str, col: str = '*', sql_filter: str | None = None):
        if sql_filter:
            query = f"SELECT {col} FROM {table} WHERE {sql_filter};"
        else:
            query = f"SELECT {col} FROM {table};"

        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if result:
                return result
            return None
        
        except sqlite3.OperationalError as e:
            print(f'\033[31m\033[34m[SQLITE ERROR]\033[0m: `{e}`')
            return None

    def get_one_from(self, table: str, col: str = '*', sql_filter: str | None = None):
        result = self.get_all_from(table, col, sql_filter)[0]
        if result:
            return result
        return None
    
    def delete_from(self, table: str, sql_filter: str | None = None):
        if not sql_filter:
            raise ValueError(
                f'\033[31m\033[34m[INTERNAL DB ERROR]\033[0m: `A filter set to NONE will rm -rf your db out of existence!`'
            )

        query = f"DELETE FROM {table} WHERE {sql_filter};"

        try:
            self.cursor.execute(query)

        except sqlite3.OperationalError as e:
            print(f'\033[31m\033[34m[SQLITE ERROR]\033[0m: `{e}`')
            return None
