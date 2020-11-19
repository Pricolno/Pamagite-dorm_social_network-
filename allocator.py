from config import Token
import telebot


bot = telebot.TeleBot(Token)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "/ + room  По комнате узнать кто-то живёт\n"
                                      "/ + surname По фамилии узнать где он живёт"
                                      "/ + help узнать описание команд")


@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(message.chat.id, 'Привет, это бот для жителей Дома Студента!\n'
                                      'Здесь вы можете узнать много полезной информции и удобно общаться с соседями! ')

    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAJc8V-2w6lq33eMxp9tbsA2ZtBHpH8gAAJ0AAM7YCQUs8te1W3kR_QeBA')


@bot.message_handler(content_types=['text'])
def eho(message):
    bot.send_message(message.chat.id, message.text * 2)


if __name__ == '__main__':
    bot.polling(none_stop=True)
