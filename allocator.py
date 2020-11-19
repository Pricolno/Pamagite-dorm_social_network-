from config import Token
import telebot
from  data_base import room_names, names_room


bot = telebot.TeleBot(Token)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "/ + room  По комнате узнать кто-то живёт\n"
                                      "/ + surname По фамилии узнать где он живёт"
                                      "/ + help узнать описание команд")


# первое взаимодействие с ботом
@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(message.chat.id, 'Привет, это бот для жителей Дома Студента!\n'
                                      'Здесь вы можете узнать много полезной информции и удобно общаться с соседями! ')

    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAJc8V-2w6lq33eMxp9tbsA2ZtBHpH8gAAJ0AAM7YCQUs8te1W3kR_QeBA')


@bot.message_handler(commands=['room'])
def get_room(message):
    next_message = bot.send_message(message.chat.id, 'В какой комнате вы хотети узнать кто живёт?')
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
    next_message = bot.send_message(message.chat.id, '')
    bot.register_next_step_handler(next_message, give_name)


def surname(message):

    pass

# @bot.message_handler(content_types=['text'])
# def eho(message):
#     bot.send_message(message.chat.id, message.text * 2)


if __name__ == '__main__':
    bot.polling(none_stop=True)
