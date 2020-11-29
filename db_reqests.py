import sqlite3

path_to_db = 'data_base/hostel.db'

__connection = None


def get_connection():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect(path_to_db)

    return __connection


def init_bd_hostel(force: bool = False):

    db = get_connection()
    cursor = db.cursor()

    if force:
        cursor.execute('DROP TABLE IF EXISTS hostel')

    query = """ CREATE TABLE IF NOT EXISTS hostel( 
    surname TEXT,
    name TEXT,
    room INTEGER,
    chat_id INTEGER
    )"""

    cursor.execute(query)
    db.commit()


def add_students(*, surname: str = None, name: str = None, room: int = None, chat_id: int = None):
    not_have = []
    if surname is None:
        not_have.append('surname')
    if name is None:
        not_have.append('name')
    if room is None:
        not_have.append('room')
    if chat_id is None:
        not_have.append('chat_id')

    for not_given in not_have:
        if not(not_given == 'chat_id'):
            return False, not_have

    db = get_connection()
    cursor = db.cursor()

    if not(chat_id is None):
        db.execute(""" INSERT INTO hostel(surname, name, room, chat_id) 
                    VALUES(?, ?, ?, ?)""", (surname, name, room, chat_id))
    else:
        db.execute(""" INSERT INTO hostel(surname, name, room, chat_id) 
                            VALUES(?, ?, ?, ?)""", (surname, name, room, None))

    db.commit()
    return True, []


def who_lives_in_room(room: int):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
    SELECT surname, name FROM hostel WHERE room = ?
    """, (room, ))
    res = cursor.fetchall()
    db.commit()
    # возращает [(Surname, Name], .. ]
    return res


def where_lives_person(surname: str = None, name: str = None):

    db = get_connection()
    cursor = db.cursor()

    if (surname is None) and (name is None):
        return
    elif (surname is None) and not(name is None):
        cursor.execute("""
                        SELECT surname, name FROM hostel WHERE name=?
                        """, (name,))
    elif not(surname is None) and (name is None):
        cursor.execute("""
                SELECT surname, name FROM hostel WHERE surname=?
                """, (surname,))
    else:
        cursor.execute("""
                SELECT surname, name FROM hostel WHERE surname=? AND name=?
                """, (surname, name))

    students = cursor.fetchall()
    db.commit()
    return students



if __name__ == '__main__':
    init_bd_hostel()
    #add_students(surname='Naumtsev', name='Aleksandr', room=620)
    #add_students(surname='Pety', name='Skovorodnikov', room=230)
    #add_students(surname='Pety', name='Skovorodnikov', room=230)
    #res = who_lives_in_room(620)
    #print(res)
    res = where_lives_person(name='Skovorodnikov')
    print(res)



