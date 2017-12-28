import sqlite3

class GameLibrary:

    def __init__(self, name='game.db'):
        self.name = name
        self.saved = True
        self.con = sqlite3.connect(name)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS library (
                                id              INTEGER PRIMARY KEY,
                                platform        VARCHAR(255),
                                platformid      INTEGER,
                                title           VARCHAR(255),
                                titleid         INTEGER,
                                cover           VARCHAR(255),
                                coverid         INTEGER,
                                release_date    VARCHAR(255),
                                genres          VARCHAR(255)
                            )""")

    def add(self, platform, title, platformid='', titleid='', cover='', coverid='', release_date='', genres=''):
        'Adds a game to the list'
        self.cur.execute("""INSERT INTO library (platform, title, platformid, titleid, cover, coverid, release_date, genres)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (platform, title, platformid, titleid, cover, coverid, release_date, genres))
        
        self.saved = False

    def remove(self, platform, title):
        'Removes a game from the list'
        self.cur.execute("""DELETE FROM library
                            WHERE platform=? AND
                                  title=?""", (platform, title))
        self.saved = False

    def update(self, uid, platform=None, platformid=None, title=None, titleid=None, cover=None, coverid=None, release_date=None, genres=None):
        'Updates a game in the list'
        
        game = self.getGamesById(uid)

        # If any of the values are None, set them to the current value
        if platform == None:        platform = game[1]
        if platformid == None:      platformid = game[2]
        if title == None:           title = game[3]
        if titleid == None:         titleid = game[4]
        if cover == None:           cover = game[5]
        if coverid == None:         coverid = game[6]
        if release_date == None:    release_date = game[7]
        if genres == None:          genres = game[8]
        
        self.cur.execute("""UPDATE library
                            SET platform=?, platformid=?, title=?, titleid=?, cover=?, coverid=?, release_date=?, genres=?
                            WHERE id=?""", (platform, platformid, title, titleid, cover, coverid, release_date, genres, uid))

        self.saved = False
        
    def getGames(self):
        'Retrieves all games'
        self.cur.execute("""SELECT * FROM library
                            ORDER BY platform ASC, title ASC""")
        
        return self.cur.fetchall()

    def getGamesById(self, uid):
        'Retrieves a game by its id'
        self.cur.execute("""SELECT * FROM library
                            WHERE id=?""", (uid,))

        return self.cur.fetchone()

    def getGamesByQuery(self, query='', platform=''):
        'Retrieves games with any field that matchs a query'

        query = '%{}%'.format(query)

        # If platform is not blank, include it in the query
        if platform != '':
            self.cur.execute("""SELECT * FROM library
                                WHERE platform = ? AND
                                    ( platformid LIKE ? OR
                                      title LIKE ? OR
                                      titleid LIKE ? OR
                                      cover LIKE ? OR
                                      coverid LIKE ? OR
                                      release_date LIKE ? OR
                                      genres LIKE ? )
                                ORDER BY platform ASC, title ASC""",
                             (platform, query, query, query, query, query, query, query))

        else:
            self.cur.execute("""SELECT * FROM library
                                WHERE platformid LIKE ? OR
                                      title LIKE ? OR
                                      titleid LIKE ? OR
                                      cover LIKE ? OR
                                      coverid LIKE ? OR
                                      release_date LIKE ? OR
                                      genres LIKE ?
                                ORDER BY platform ASC, title ASC""",
                             (query, query, query, query, query, query, query))

        return self.cur.fetchall()

    def getGamesBySearch(self, query='', platform='', platformid='', title='', titleid='', cover='', coverid='', release_date='', genres=''):
        'Retrieves games that match search terms'

        # Platform should match exactly, so don't wrap in wildcards
        platformid =    '%{}%'.format(platformid)
        title =         '%{}%'.format(title)
        titleid =       '%{}%'.format(titleid)
        cover =         '%{}%'.format(cover)
        coverid =       '%{}%'.format(coverid)
        release_date =  '%{}%'.format(release_date)
        genres =        '%{}%'.format(genres)

        # If platform is not blank, include it in the query
        if platform != '':
            self.cur.execute("""SELECT * FROM library
                                WHERE platform = ? AND
                                      platformid LIKE ? AND
                                      title LIKE ? AND
                                      titleid LIKE ? AND
                                      cover LIKE ? AND
                                      coverid LIKE ? AND
                                      release_date LIKE ? AND
                                      genres LIKE ?
                                ORDER BY platform ASC, title ASC""",
                             (platform, platformid, title, titleid, cover, coverid, release_date, genres))

        else:
            self.cur.execute("""SELECT * FROM library
                                WHERE platformid LIKE ? AND
                                      title LIKE ? AND
                                      titleid LIKE ? AND
                                      cover LIKE ? AND
                                      coverid LIKE ? AND
                                      release_date LIKE ? AND
                                      genres LIKE ?
                                ORDER BY platform ASC, title ASC""",
                             (platformid, title, titleid, cover, coverid, release_date, genres))

        return self.cur.fetchall()        

    def getGamesByPlatform(self, platform):
        'Retrieves games by platform'
        
        self.cur.execute("""SELECT * FROM library
                            WHERE platform=?
                            ORDER BY platform ASC, title ASC""", (platform,))

        return self.cur.fetchall()

    def getPlatforms(self):
        'Retrieves all platforms'
        self.cur.execute("""SELECT DISTINCT platform FROM library
                            ORDER BY platform ASC""")

        return [item[0] for item in self.cur]

    def save(self):
        'Saves changes made to the list'
        self.con.commit()
        self.saved = True

    def close(self):
        'Closes list'
        self.con.close()

    def import_(self, filepath):
        'Imports from a .csv file'
        if not filepath.endswith('.csv'):
            filepath += '.csv'
        
        infile = open(filepath)

        for line in infile:
            ln = line.rstrip().split(',')
            self.add(ln[0], ln[2], ln[1], ln[3], ln[4], ln[5], ln[6], ln[7])

        infile.close()

    def export(self, filepath):
        'Exports to a .csv file'
        if not filepath.endswith('.csv'):
            filepath += '.csv'
        
        outfile = open(filepath, 'w')
        
        for record in self.getGames():
            outfile.write('{},{},{},{},{},{},{},{},\n'.format(record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8]))

        outfile.close()

    def __del__(self):
        self.close()
