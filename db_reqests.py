import sqlite3
import time
path_to_db = 'data_base/hostel.db'

__connection = None


def get_connection():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect(path_to_db, check_same_thread=False)

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


def init_bd_vk_groups(force: bool = False):

    db = get_connection()
    cursor = db.cursor()

    if force:
        cursor.execute('DROP TABLE IF EXISTS groups')

    query = """ CREATE TABLE IF NOT EXISTS groups( 
       person_id INTEGER,
       group_id INTEGER,
       group_name TEXT
       )"""

    cursor.execute(query)
    db.commit()


def add_students(surname: str = None, name: str = None, room: int = None, chat_id: int = None):
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

    if not chat_id is None:
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
    SELECT surname, name, chat_id FROM hostel WHERE room = ?
    """, (room, ))
    res = cursor.fetchall()
    db.commit()
    cursor.close()

    # возращает [(surname, name, chat_id], .. ]
    if len(res) > 0:
        return True, res
    else:
        return False, res


def where_lives_person(surname=None, name=None):

    db = get_connection()
    cursor = db.cursor()

    if (surname is None) and (name is None):
        cursor.close()
        return False, []
    elif (surname is None) and not(name is None):
        cursor.execute("""
                        SELECT room, surname, name, chat_id FROM hostel WHERE name=?
                        """, (name,))
    elif not(surname is None) and (name is None):
        cursor.execute("""
                SELECT room, surname, name, chat_id FROM hostel WHERE surname=?
                """, (surname,))
    else:
        cursor.execute("""
                SELECT room, surname, name, chat_id FROM hostel WHERE surname=? AND name=?
                """, (surname, name))
    # возращает [(room, surname, name, chat_id)]
    students = cursor.fetchall()
    cursor.close()

    if len(students) > 0:
        return True, students
    else:
        return False, []


def get_profile(chat_id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
    SELECT room, surname, name, chat_id FROM hostel WHERE chat_id=?
    """, (chat_id, ))

    profile = cursor.fetchall()
    db.commit()
    cursor.close()

    print(profile)
    if len(profile) == 0:
        return False, []
    else:
        return True, profile


def change_data_in_profile(chat_id, data_type, replacement):
    db = get_connection()
    cursor = db.cursor()

    sql = f"""
    UPDATE hostel 
    SET {data_type} = '{replacement}'
    WHERE hostel.chat_id = '{chat_id} ' 
    """

    cursor.execute(sql)
    db.commit()
    cursor.close()
    return True


def get_all_chat_ids():
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT chat_id FROM hostel
        """)

    list_chat_ids = [chat_id_empty[0] for chat_id_empty in cursor.fetchall()]
    db.commit()
    cursor.close()

    return list_chat_ids


def add_group(person_id, group_id, group_name):

    db = get_connection()

    db.execute(""" INSERT INTO groups(person_id, group_id, group_name) 
                        VALUES(?, ?, ?)""", (person_id, group_id, group_name))
    db.commit()


def delete_group(person_id, group_id: int = None, group_name: str = None):

    db = get_connection()

    if group_id is None:
        db.execute(f""" DELETE FROM groups
                            WHERE person_id = {person_id}; group_name = {group_name}""")
    elif group_name is None:
        db.execute(f""" DELETE FROM groups
                                    WHERE person_id = {person_id}; group_id = {group_id}""")

    db.commit()


def get_persons_groups(person_id):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute(f"""
        SELECT group_name FROM groups
        WHERE person_id = {person_id}
        ORDER BY group_name
        """)
    list_of_group_names = cursor.fetchall()
    cursor.close()
    return list_of_group_names

if __name__ == '__main__':
    init_bd_hostel()
    init_bd_vk_groups()
    # add_group(1234, 567891, "Информатика")
    # add_group(1234, 567895, "Английский язык?")
    # print(get_persons_groups(1234))
    #delete_group(1234, group_name="Математика")
    # add_students(surname='Naumtsev', name='Aleksandr', room=620)
    # add_students(surname='Pety', name='Skovorodnikov', room=230)
    # add_students(surname='Pety', name='Skovorodnikov', room=230)
    # res = who_lives_in_room(620)
    # print(res)
    # res = where_lives_person(name='Skovorodnikov')
    # print(res)
    # print(who_lives_in_room(350))

    # print('  gg gg   '.split())
    # print(get_profile('387731337'))

    print(time.time())
    for i in range(1000000):
        i+=1
    print(time.time())