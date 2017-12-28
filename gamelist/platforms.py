import sqlite3


class Platforms:

    def __init__(self, filename='platforms.db'):
        self.filename = filename
        self.con = sqlite3.connect(filename)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS platforms (
                                                id              INTEGER PRIMARY KEY,
                                                name            VARCHAR(255)
                                            )""")

    def add(self, uid, name):
        'Adds a platform'
        self.cur.execute("""INSERT INTO platforms (id, name)
                            VALUES (?, ?)""",
                         (uid, name))

        self.con.commit()

    def remove(self, name):
        'Removes a platform'
        self.cur.execute("""DELETE FROM platforms
                            WHERE name=?""", (name,))
        self.con.commit()

    def removeAll(self):
        'Removes all platforms'
        self.cur.execute("""DELETE FROM platforms""")
        self.con.commit()

    def getPlatforms(self):
        'Retrieves all platforms'
        self.cur.execute("""SELECT * FROM platforms
                            ORDER BY id ASC""")

        return self.cur.fetchall()

    def getPlatformName(self, uid):
        'Retrieves a platform name'
        self.cur.execute("""SELECT name FROM platforms
                            WHERE id=?""", (uid,))

        result = self.cur.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    def getPlatformId(self, name):
        'Retrieves a platform id'
        self.cur.execute("""SELECT id FROM platforms
                            WHERE name=?""", (name,))

        result = self.cur.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    def close(self):
        'Closes list'
        self.con.close()

    def __del__(self):
        self.close()
