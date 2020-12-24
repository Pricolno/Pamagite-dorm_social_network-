from threading import Thread

from config import Token
import telebot
from db_reqests import *
import os
import sys
import vk_api
import configparser
from time import sleep

# from aiogram.types import ReplyKeyboardRemove, \
#     ReplyKeyboardMarkup, KeyboardButton, \
#     InlineKeyboardMarkup, InlineKeyboardButton


bot = telebot.TeleBot(Token)

config_path = os.path.join(sys.path[0], 'settings.ini')
config = configparser.ConfigParser()
config.read(config_path)
ACCESS_TOKEN_VK = config.get('VK', 'ACCESS_TOKEN_VK')
DOMAIN_TEST = config.get('VK', 'DOMAIN_TEST')
DOMAIN_MAIN = config.get('VK', 'DOMAIN_MAIN')
COUNT_TEST = config.get('VK', 'COUNT_TEST')
COUNT_MAIN = config.get('VK', 'COUNT_MAIN')
PREVIEW_LINK = config.get('Settings', 'PREVIEW_LINK')

message_breakers = [':', ' ', '\n']
max_message_length = 4091


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "/room 🏠 По комнате узнать кто там живёт\n"
                                      "/surname 🧑‍🎓 По фамилии узнать где он живёт\n"
                                      "/registration 🛂  Зарегистрироваться в систему (ФИ, комната)\n"
                                      "/profile 👦 Профиль пользователя\n"
                                      "/send_message_to_room 📩 Отправить письмо комнате\n"
                                      "/info VK - узнать свежую полезную информацию\n"
                                      "/help 🆘 Узнать описание команд\n"
                                      "/start 🔙 Повторить приветствие\n"
                                      "/vk_management Подписка, отписка от групп вк\n"
                                      "/my_groups Список подписок")


def create_main_markup():
    markup = telebot.types.ReplyKeyboardMarkup(True, True)
    button_room = telebot.types.KeyboardButton('🏠')  # 🏠 /room
    button_surname = telebot.types.KeyboardButton('🧑‍🎓')  # 🧑‍🎓 /surname
    button_registration = telebot.types.KeyboardButton('🛂')  # 🛂 /registration
    button_profile = telebot.types.KeyboardButton('👦')  # 👦 /profile
    button_send_message_to_room = telebot.types.KeyboardButton('📩')  # 👦 /profile
    button_start = telebot.types.KeyboardButton('🔙')  # 🔙 /send_message_to_room
    button_vk = telebot.types.KeyboardButton('VK')  # vk /info
    button_help = telebot.types.KeyboardButton('🆘')  # 🆘 /help
    markup.row(button_room, button_surname, button_registration)
    markup.row(button_profile, button_send_message_to_room, button_start)
    markup.row(button_vk, button_help)
    return markup


# первое взаимодействие с ботом
@bot.message_handler(commands=['start'])
def start(message):
    markup = create_main_markup()
    bot.send_message(message.chat.id, 'Привет, это бот для жителей Дома Студента!\n'
                                      'Здесь вы можете узнать много полезной информции и удобно общаться с соседями!\n'
                                      'Используйте /help чтобы узнать команды', reply_markup=markup)

    # main_keyboard(message)

    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAJc8V-2w6lq33eMxp9tbsA2ZtBHpH8gAAJ0AAM7YCQUs8te1W3kR_QeBA')
    # bot.register_next_step_handler(next_message, main_keyboard)
    # main_keyboard(message)


def main_keyboard(message):
    markup = create_main_markup()
    # next_message = bot.send_message(message.chat.id, ' gg', reply_markup=markup)
    bot.send_message(message.chat.id, 'asdasdad')
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAKJIF_eek6G_jdz5w8l_XqpXB85SQ74AAIeAAPANk8ToWBbLasAAd4EHgQ',
                     reply_markup=markup)
    # bot.register_next_step_handler(next_message, change_profile)


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
                                        'Пожалуйста введите корректно данные\n Фамилия Имя\n Поиск по одной Фамилия'
                                        '/Имя:\nsurname=Фамилия/Имени')
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
            bot.send_message(message.chat.id,
                             surname_ + ' ' + name_ + ' : ' + str(room_))  # достать номер комнаты жильцов
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
    if not (list_name_room[2].isdigit()):
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
    if exist:
        profile = profile[0]
        room = profile[0]
        surname = profile[1]
        name = profile[2]
        chat_id = profile[3]

        markup = telebot.types.ReplyKeyboardMarkup(True, True)
        button_surname = telebot.types.KeyboardButton('surname')
        button_name = telebot.types.KeyboardButton('name')
        button_room = telebot.types.KeyboardButton('room')
        button_exit = telebot.types.KeyboardButton('exit')
        markup.row(button_surname, button_name, button_room, button_exit)

        next_message = bot.send_message(message.chat.id,
                                        f""" Surname: {surname}\nName: {name}\nRoom: {room}\n\nВы можете изменить данные""",
                                        reply_markup=markup)
        bot.register_next_step_handler(next_message, change_profile)

    else:
        next_message = bot.send_message(message.chat.id, """Вы не зарегистрированны""")
        bot.register_next_step_handler(next_message, registration)


data_type = ''


def change_profile(message):
    if message.text in ['surname', 'name', 'room']:
        next_message = bot.send_message(message.chat.id, 'Введите желаемые изменения')
        global data_type
        data_type = message.text
        bot.register_next_step_handler(next_message, change_data_in_profile_bot)
        return
    if 'exit' in message.text:
        main_keyboard(message)
        return


def change_data_in_profile_bot(message):
    global data_type
    print(data_type)
    print(message.text)
    print('MAIN_KEYBOARD_3')
    print(data_type)
    if 'exit' in data_type:
        print('MAIN_KEYBOARD_0')
        main_keyboard(message)
        print('MAIN_KEYBOARD_0')
        return

    change_data_in_profile(message.chat.id, data_type, message.text)

    markup = telebot.types.ReplyKeyboardMarkup(True, True)
    button_surname = telebot.types.KeyboardButton('surname')
    button_name = telebot.types.KeyboardButton('name')
    button_room = telebot.types.KeyboardButton('room')
    button_exit = telebot.types.KeyboardButton('exit')
    markup.row(button_surname, button_name, button_room, button_exit)

    next_message = bot.send_message(message.chat.id, "Что вы хотите изменить?", reply_markup=markup)
    bot.register_next_step_handler(next_message, change_profile)


@bot.message_handler(commands=['send_message_to_room'])
def send_message_across_the_room_request(message):
    next_message = bot.send_message(message.chat.id, 'Какой комнате вы хотите отправить сообщение?')
    bot.register_next_step_handler(next_message, send_message_across_the_room)


request_room = -1


def send_message_across_the_room(message):
    global request_room
    print(message.text)
    if message.text.isdigit():
        request_room = int(message.text)
        next_message = bot.send_message(message.chat.id, f'Напишите послание комнате: {request_room}')
        bot.register_next_step_handler(next_message, send_message_across_the_room_final)
    else:
        bot.send_message(message.chat.id, 'Введено не число')


def send_message_across_the_room_final(message):
    global request_room
    letter = message.text
    exist, persons = who_lives_in_room(request_room)
    if exist:
        bot.send_message(message.chat.id, 'Отправили сообщение:')
        for person in persons:
            bot.send_message(person[2], letter)
            bot.send_message(message.chat.id, person[0] + ' ' + person[1])
    else:
        bot.send_message(message.chat.id, 'Мы не знаем кто там живёт :(')


def start_vk_session():
    vk_session = vk_api.VkApi(token=ACCESS_TOKEN_VK)
    vk = vk_session.get_api()
    return vk


def get_data(domain_vk, count_vk):
    vk = start_vk_session()
    response = vk.wall.get(domain=domain_vk, count=count_vk)
    return response


def check_posts_vk(message_chat_id=None):
    if message_chat_id:
        posts = get_data(DOMAIN_MAIN, COUNT_MAIN)
        posts = reversed(posts['items'])
        for post in posts:
            text = post['text']
            send_posts_text(text, message_chat_id)
            send_attachments(message_chat_id, post)
    else:
        posts = get_data(DOMAIN_TEST, COUNT_TEST)
        posts = reversed(posts['items'])
        flag = False
        for post in posts:
            id = config.get('Settings', 'LAST_ID')
            if int(post['id']) <= int(id):
                continue

            if not flag:
                # message_chat_ids = get_all_chat_ids()
                message_chat_ids = [387731337, 343196823]
                # message_chat_ids = [572525878]
                flag = True

            for chat_id in message_chat_ids:
                text = post['text']
                send_posts_text(text, chat_id)
                send_attachments(chat_id, post)
            config.set('Settings', 'LAST_ID', str(post['id']))
            with open(config_path, "w") as config_file:
                config.write(config_file)


def send_posts_text(text, message_chat_id):
    if text == '':
        print('no text')
    else:
        global bot
        # Если слишком много символов, разделяем сообщение
        for message in split(text):
            try:
                next_message = bot.send_message(message_chat_id, message, disable_web_page_preview=not PREVIEW_LINK)
                print('Не кидок: ', next_message)
            except telebot.apihelper.ApiException as e:
                print(e)
                left_person(message_chat_id)
                break

            print('отправил')


def left_person(chat_id):
    print('Кидок: ', chat_id)
    pass
    # можно что-то сделать с пользователем который заблокировал бота


def split(text):
    if len(text) >= max_message_length:
        last_index = max(
            map(lambda separator: text.rfind(separator, 0, max_message_length), message_breakers))
        good_part = text[:last_index]
        bad_part = text[last_index + 1:]
        return [good_part] + split(bad_part)
    else:
        return [text]


def send_attachments(message_chat_id, post):
    images = []
    if 'attachments' in post:
        attachment = post['attachments']
        for add in attachment:
            if add['type'] == 'photo':
                image = add['photo']
                images.append(image)
    if len(images) > 0:
        image_urls = list(map(lambda image: max(
            image["sizes"], key=lambda size: size["type"])["url"], images))
        try:
            bot.send_media_group(message_chat_id, map(
                lambda url: telebot.types.InputMediaPhoto(url), image_urls))
        except telebot.apihelper.ApiException as e:
            print(e)
            left_person(message_chat_id)


@bot.message_handler(commands=['vk_management'])
def get_operation(message):
    next_message = bot.send_message(message.chat.id, 'Что вы хотите сделать?\nДобавить группу:\nadd ID группы\n'
                                                     'Удалить группу:\ndelete Id группы/Название группы')
    bot.register_next_step_handler(next_message, vk_setting)


def vk_setting(message):
    vk_operation = message.text
    vk_operation = vk_operation.split(" ")
    exist_in_bd, profile = get_profile(message.chat.id)
    if not exist_in_bd:
        bot.send_message(message.chat.id,
                         'Чтобы иметь возможность подписываться на группы вк, пожалуйста зарегистрируйтесь!')
        return
    # print(owner_room)
    if not ('delete' == vk_operation[0] or 'add' == vk_operation[0]):
        next_message = bot.send_message(message.chat.id,
                                        'Пожалуйста введите корректно команду\nДобавить группу:\nadd ID группы\n'
                                        'Удалить группу:\ndelete Id группы/Название группы')
        bot.register_next_step_handler(next_message, vk_setting)
        return
    if len(vk_operation) == 1:
        next_message = bot.send_message(message.chat.id,
                                        'Пожалуйста введите корректно команду\nДобавить группу:\nadd ID группы\n'
                                        'Удалить группу:\ndelete Id группы/Название группы')
        bot.register_next_step_handler(next_message, vk_setting)
        return
    if vk_operation[0] == 'add' and len(vk_operation) != 2:
        next_message = bot.send_message(message.chat.id,
                                        'Пожалуйста введите корректно команду\nДобавить группу:\nadd ID группы\n'
                                        'Удалить группу:\ndelete Id группы/Название группы')
        bot.register_next_step_handler(next_message, vk_setting)
        return
    if vk_operation[0] == 'add':
        vk = start_vk_session()
        name_of_group = ''
        id_of_group = -1
        try:
            name_of_group = vk.groups.getById(group_id=vk_operation[1])[0]['name']
            id_of_group = int(vk.groups.getById(group_id=vk_operation[1])[0]['id'])
        except vk_api.ApiError:
            print('Неправильное короткое название')
        if name_of_group == '':
            next_message = bot.send_message(message.chat.id,
                                            'Пожалуйста, введите правильный идентификатор группы!')
            bot.register_next_step_handler(next_message, vk_setting)
            return
        exist, group_name = is_persons_group(message.chat.id, group_id=id_of_group)
        if exist:
            bot.send_message(message.chat.id,
                             f'Вы уже подписаны на группу {group_name}!')
        else:
            add_group(message.chat.id, id_of_group, name_of_group)
            bot.send_message(message.chat.id, f'Вы успешно подписались на группу {name_of_group}')
    if vk_operation[0] == 'delete' and len(vk_operation) == 2 and vk_operation[1].isdigit():
        exist, group_name = is_persons_group(message.chat.id, group_id=int(vk_operation[1]))
        if not exist:
            next_message = bot.send_message(message.chat.id,
                                            'К сожалению вы не подписаны на эту группу')
            bot.register_next_step_handler(next_message, vk_setting)
            return
        else:
            delete_group(message.chat.id, group_id=vk_operation[1])
            bot.send_message(message.chat.id,
                             f'Вы успешно отписались от группы {group_name}')
    elif vk_operation[0] == 'delete':
        group_name = message.text.replace('delete ', '')
        exist, group_name = is_persons_group(message.chat.id, group_name=group_name)
        print(exist, group_name)
        if not exist:
            next_message = bot.send_message(message.chat.id,
                                            'К сожалению вы не подписаны на эту группу')
            bot.register_next_step_handler(next_message, vk_setting)
            return
        else:
            delete_group(message.chat.id, group_name=group_name)
            bot.send_message(message.chat.id,
                             f'Вы успешно отписались от группы {group_name}')


@bot.message_handler(commands=['my_groups'])
def persons_groups(message):
    list_of_groups = get_persons_groups(message.chat.id)
    text_of_message = ''
    for name_of_group in list_of_groups:
        text_of_message = text_of_message + name_of_group + '\n'
    if text_of_message == '':
        bot.send_message(message.chat.id, 'К сожалению, вы не подписаны ни на что')
    else:
        bot.send_message(message.chat.id, text_of_message)


@bot.message_handler(commands=['info'])
def get_info(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Лупа и Пупа', callback_data='lypa_group'))
    bot.send_message(message.chat.id, text='Выберите источник информации', reply_markup=markup)


# Inline keyboard
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'lypa_group':
        check_posts_vk(call.message.chat.id)


def bot_telegram_polling():
    while True:
        try:
            global bot
            bot.polling(none_stop=True)
        except Exception as exception:
            print(exception)


def vk_post():
    while True:
        check_posts_vk()
        sleep(10)


@bot.message_handler(content_types=['text'])
def allocation_commands(message):
    if message.text == '🏠':
        get_room(message)
    elif message.text == '🧑‍🎓':
        get_surname(message)
    elif message.text == '🛂':
        registration(message)
    elif message.text == '👦':
        show_profile(message)
    elif message.text == '📩':
        send_message_across_the_room_request(message)
    elif message.text == '🔙':
        start(message)
    elif message.text == 'VK':
        get_info(message)
    elif message.text == '🆘':
        help(message)
    else:
        print('mdaaa')


if __name__ == '__main__':
    Thread(target=bot_telegram_polling).start()
    Thread(target=vk_post).start()
