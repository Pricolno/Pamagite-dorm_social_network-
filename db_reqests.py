import sqlite3
import time

path_to_db = 'data_base/hostel.db'

__connection = None


def get_connection():
    """Функция устанавливает соединение с базой данных"""
    global __connection
    if __connection is None:
        __connection = sqlite3.connect(path_to_db, check_same_thread=False)

    return __connection


def init_bd_hostel(force: bool = False):
    """Функция создает таблицу hostel в базе данных, если ее еще нет"""
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
    cursor.close()


def init_bd_vk_groups(force: bool = False):
    """Функция создает таблицу groups в базе данных, если ее еще нет"""
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


def init_bd_last_posts(force: bool = False):
    """Функция создает таблицу posts в базе данных, если её еще нет"""
    db = get_connection()
    cursor = db.cursor()

    if force:
        cursor.execute('DROP TABLE IF EXISTS posts')

    query = """ CREATE TABLE IF NOT EXISTS posts( 
           group_id INTEGER,
           post_id INTEGER
           )"""

    cursor.execute(query)
    db.commit()


def add_students(surname: str = None, name: str = None, room: int = None, chat_id: int = None):
    """Функция добавляет новые значения в таблицу hostel"""
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
        if not_given != 'chat_id':
            return False, not_have

    db = get_connection()

    if chat_id:
        db.execute(""" INSERT INTO hostel(surname, name, room, chat_id) 
                    VALUES(?, ?, ?, ?)""", (surname, name, room, chat_id))
    else:
        db.execute(""" INSERT INTO hostel(surname, name, room, chat_id) 
                            VALUES(?, ?, ?, ?)""", (surname, name, room, None))

    db.commit()
    return True, []


def who_lives_in_room(room: int):
    """Функция возвращает фамилию, имя и chat_id студента, который живет в комнате с номером room"""
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
    SELECT surname, name, chat_id FROM hostel WHERE room = ?
    """, (room,))
    res = cursor.fetchall()
    db.commit()
    cursor.close()

    # возращает [(surname, name, chat_id], .. ]
    if len(res) > 0:
        return True, res
    else:
        return False, res


def where_lives_person(surname=None, name=None):
    """Возвращает номер команаты (или список номеров), в которой живет человек"""
    db = get_connection()
    cursor = db.cursor()

    if surname is None and name is None:
        cursor.close()
        return False, []
    elif surname is None and name:
        cursor.execute("""
                        SELECT room, surname, name, chat_id FROM hostel WHERE name=?
                        """, (name,))
    elif surname and name is None:
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
    """, (chat_id,))

    profile = cursor.fetchall()
    db.commit()
    cursor.close()

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


def is_persons_group(person_id, group_id: int = None, group_name: str = None):
    groups = get_persons_groups(person_id)

    if group_name:
        for group_description in groups:
            if group_description[1] == group_name:
                return True, group_description[1]
    elif group_id:
        for group_description in groups:
            if group_description[0] == group_id:
                return True, group_description[1]
    return False, ''


def delete_group(person_id, group_id: int = None, group_name: str = None):
    db = get_connection()

    if group_name:
        db.execute(f""" DELETE FROM groups
                            WHERE person_id = {person_id} AND group_name = {"'" + group_name + "'"}""")
    elif group_id:
        db.execute(f""" DELETE FROM groups
                                    WHERE person_id = {person_id} AND group_id = {group_id}""")

    db.commit()


def get_persons_groups(person_id):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute(f"""
        SELECT group_id, group_name FROM groups
        WHERE person_id = {person_id}
        ORDER BY group_name
        """)
    list_of_group_names = cursor.fetchall()
    cursor.close()
    return list_of_group_names


def is_new_group(group_id):
    last_post_id = get_last_post_id(group_id)

    if last_post_id:
        return False

    return True


def add_new_post(group_id, post_id):
    db = get_connection()

    db.execute(""" INSERT INTO posts(group_id, post_id) 
                            VALUES(?, ?)""", (group_id, post_id))
    db.commit()


def delete_post(group_id):
    db = get_connection()

    db.execute(f""" DELETE FROM posts
                                WHERE group_id = {group_id}""")

    db.commit()


def get_all_groups():
    db = get_connection()
    cursor = db.cursor()

    cursor.execute(f"""
            SELECT group_id, post_id FROM posts
            """)
    list_of_group_names = cursor.fetchall()
    cursor.close()
    return list_of_group_names


def get_last_post_id(group_id):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute(f"""
                SELECT post_id FROM posts
                WHERE group_id = {group_id}
                """)
    last_post_id = cursor.fetchall()
    cursor.close()
    if last_post_id:
        return last_post_id[0][0]
    return last_post_id


def update_last_post_id(group_id, post_id):
    db = get_connection()
    cursor = db.cursor()

    sql = f"""
        UPDATE posts 
        SET post_id = '{post_id}'
        WHERE group_id = '{group_id} ' 
        """

    cursor.execute(sql)
    db.commit()
    cursor.close()


if __name__ == '__main__':
    init_bd_hostel()
    init_bd_vk_groups()
    init_bd_last_posts()
