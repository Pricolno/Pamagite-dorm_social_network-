from config import Token
import telebot
from data_base import room_names, names_room


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
    if room in room_names:  # условие есть ли комната в базе данных
        names = room_names[room]    # взять все фио кто живёт в данной комнате (0 1 2)

        if len(names) > 0:
            for name in names:
                bot.send_message(message.chat.id, name)
        else:
            bot.send_message(message.chat.id, 'Мы не знаем кто-там живёт 😖')

    else:
        bot.send_message(message.chat.id, 'Такой комнаты не существует 🙄')


@bot.message_handler(commands=['surname'])
def get_surname(message):
    next_message = bot.send_message(message.chat.id, 'Чьё местопроживание вас интересует?\n Фамилия Имя')
    bot.register_next_step_handler(next_message, give_room)


def give_room(message):
    owner_room = message.text
    #print(owner_room)
    if owner_room.lower() in names_room:  # проверка наличие человека в базе данных
        bot.send_message(message.chat.id, names_room[owner_room.lower()]) # достать номер комнаты жильцов
    else:
        bot.send_message(message.chat.id, 'Этот человек не живёт в общежитии 🙄')


@bot.message_handler(commands=['registration'])
def registration(message):
    next_message = bot.send_message(message.chat.id, """
    Введите пожалуйста на новых строчках
    Фамилия Имя
    Номер комнаты
    """)
    bot.register_next_step_handler(next_message, registration_add_in_bd)


def registration_add_in_bd(message):
    #print(message.text)
    list_name_room = message.text.split('\n')
    if not (len(list_name_room) == 2):
        #print('Пожалуйста, введите корректно данные')
        next_message = bot.send_message(message.chat.id, 'Пожалуйста, введите корректно данные')
        bot.register_next_step_handler(next_message, registration_add_in_bd)

    surname_name = list_name_room[0]
    room = list_name_room[1]

    if room in room_names:
        room_names[room].append(surname_name)
    else:
        room_names[room] = surname_name

    if not(surname_name in names_room):
        names_room[surname_name] = room


if __name__ == '__main__':
    bot.polling(none_stop=True)
