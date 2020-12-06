from config import Token
import telebot
from db_reqests import *
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(Token)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "/room  По комнате узнать кто там живёт\n"
                                      "/surname По фамилии узнать где он живёт\n"
                                      "/help Узнать описание команд")


# первое взаимодействие с ботом
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, это бот для жителей Дома Студента!\n'
                                      'Здесь вы можете узнать много полезной информции и удобно общаться с соседями!'
                                      'Используйте /help чтобы узнать команды')

    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAJc8V-2w6lq33eMxp9tbsA2ZtBHpH8gAAJ0AAM7YCQUs8te1W3kR_QeBA')


@bot.message_handler(commands=['room'])
def get_room(message):
    next_message = bot.send_message(message.chat.id, 'В какой комнате вы хотите узнать кто живёт?')
    bot.register_next_step_handler(next_message, give_name)


def give_name(message):
    room = message.text
    if not room.isdigit():
        next_message = bot.send_message(message.chat.id, 'Вы ввели не число, напишите число')
        bot.register_next_step_handler(next_message, give_name)
        return

    room = int(room)

    exists, students = who_lives_in_room(room)

    if 100 <= room < 800:  # условие есть ли комната в базе данных
        # names = room_names[room]    # взять все фио кто живёт в данной комнате (0 1 2)

        if exists:
            bot.send_message(message.chat.id, 'В комнате ' + str(room) + ' живут:')
            for (surname, name, chat_id) in students:
                bot.send_message(message.chat.id, surname + ' ' + name)
        else:
            bot.send_message(message.chat.id, 'Мы не знаем кто-там живёт 😖')

    else:
        bot.send_message(message.chat.id, 'Такой комнаты не существует 🙄')


@bot.message_handler(commands=['surname'])
def get_surname(message):
    next_message = bot.send_message(message.chat.id, 'Чьё местопроживание вас интересует?\n Фамилия Имя\n'
                                                     'Поиск по одной Фамилия/Имя:\nsurname=Фамилия/Имени')
    bot.register_next_step_handler(next_message, give_room)


def give_room(message):
    owner_room = message.text
    # print(owner_room)
    owner_room = owner_room.split(' ')
    if len(owner_room) > 2:
        next_message = bot.send_message(message.chat.id,
                                        'Пожалуйста введите корректно данные\n Фамилия Имя\n Поиск по одной Фамилия/Имя:\n'
                                        'surname=Фамилия/Имени')
        bot.register_next_step_handler(next_message, give_room)
        return
    surname, name = None, None


    if len(owner_room) == 1:  # кучу косяков проверка на верный ввод
        flag_nick = owner_room[0]
        if 'surname=' in flag_nick:
            surname = flag_nick.replace('surname=', '').strip()
        elif 'name=' in flag_nick:
            name = flag_nick.replace('name=', '').strip()
        else:
            next_message = bot.send_message(message.chat.id,
                                            'Пожалуйста введите корректно данные\n Фамилия Имя\n Поиск по одной Фамилии/Имени:\n'
                                            'surname=Фамилия/Имени')
            bot.register_next_step_handler(next_message, give_room)
            return
    else:
        surname = owner_room[0]
        name = owner_room[1]

    exist, info_of_person = where_lives_person(surname=surname, name=name)

    if exist:  # проверка наличие человека в базе данных
        for room_, surname_, name_, chat_id in info_of_person:
            bot.send_message(message.chat.id, surname_ + ' ' + name_ + ' : ' + str(room_))   # достать номер комнаты жильцов
    else:
        bot.send_message(message.chat.id, 'Этот человек не живёт в общежитии 🙄')


@bot.message_handler(commands=['registration'])
def registration(message):
    exist, profile = get_profile(message.chat.id)
    if exist:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы\n Если вы хотите изменить данные зайдите в профиль")
        return

    next_message = bot.send_message(message.chat.id, """
    Введите пожалуйста на новых строчках
    Фамилия 
    Имя
    Номер комнаты
    """)
    bot.register_next_step_handler(next_message, registration_add_in_bd)


def exception_registration_add_in_bd(message):
    # print('Пожалуйста, введите корректно данные')
    next_message = bot.send_message(message.chat.id, """
        Введите пожалуйста корректные данные
        Фамилия 
        Имя
        Номер комнаты
        """)
    bot.register_next_step_handler(next_message, registration_add_in_bd)
    return


def registration_add_in_bd(message):
    # print(message.text)
    list_name_room = message.text.split('\n')
    if not (len(list_name_room) == 3):
        exception_registration_add_in_bd(message)
        return

    surname = list_name_room[0]
    name = list_name_room[1]  # неправильный ввод может быть
    if not(list_name_room[2].isdigit()):
        exception_registration_add_in_bd(message)
        return

    room = int(list_name_room[2])
    chat_id = message.chat.id
    add_students(surname=surname, name=name, room=room, chat_id=chat_id)

    bot.send_message(message.chat.id, 'Пользователь успешно добавлен в систему')


@bot.message_handler(commands=['profile'])
def show_profile(message):
    chat_id = message.chat.id
    exist, profile = get_profile(chat_id)
    profile = profile[0]
    if exist:
        room = profile[0]
        surname = profile[1]
        name = profile[2]
        chat_id = profile[3]
        bot.send_message(message.chat.id, f""" Surname: {surname}\nName: {name}\nRoom: {room}""")

    else:
        next_message = bot.send_message(message.chat.id, """Вы не зарегистрированны""")
        bot.register_next_step_handler(next_message, registration)
    return



if __name__ == '__main__':
    bot.polling(none_stop=True)
