from ..db import Database

db = Database.getDatabase()

def get_race_list():
    result = []
    cursor = db.cursor()
    query = ("SELECT DISTINCT REPLACE(LOWER(name), ' grand prix', '') FROM races ORDER BY raceId;")

    cursor.execute(query)
    for race in cursor:
        result.append(race[0])
    return result
