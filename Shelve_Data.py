import shelve
import json

class Shelve_Data(object):
    def __init__(self, db_name):
        """Open or create new database file"""
        self.db = shelve.open(db_name)
    
    def push(self, data, key):
        """Push JSON Object into DB"""
        self.db[key] = data

    def pull_all(self):
        """Pulls all objects from the DB"""
        try:
            return self.db.values()
        finally:
            self.db.values()

    def close(self):
        """Close the database file"""
        self.db.close()
