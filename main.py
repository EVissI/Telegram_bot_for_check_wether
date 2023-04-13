import telebot
from telebot import types
import requests
import json
import sqlite3

bot = telebot.TeleBot('6054469955:AAHEO3G3W4EaBWZZgWHuP81Q1efcfV4ZyFE')
API = '3d343d1df7aa7afa6246dae7744467a8'


@bot.message_handler(commands=['start', 'lang'])
def start(message):

    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users(id int primary key,lang varchar(15))')  # create table
    cur.execute('SELECT id FROM users')      # take all user_id from table
    users = cur.fetchall()                   # that func return info from table like [(123,142,412)]
    if not(message.from_user.id in users[0]):
        cur.execute('INSERT INTO users (id,lang) VALUES ("%s","en") ' % message.from_user.id)
    conn.commit()
    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup()               # creating buttons for change language bot
    btn1 = types.KeyboardButton('Русский')
    btn2 = types.KeyboardButton('English')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Hello, good to see you! Choose the language', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    a = telebot.types.ReplyKeyboardRemove()      # func for remove button after use

    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()

    if message.text == 'Русский':
        bot.send_message(message.from_user.id, 'Язык бота изменен на Русский ', reply_markup=a)
        cur.execute('UPDATE users SET lang = "ru" WHERE id = ("%s")' % message.from_user.id)
        conn.commit()
        cur.close()
        conn.close()
    elif message.text == 'English':
        bot.send_message(message.from_user.id, 'Bot language changed to English ', reply_markup=a)
        cur.execute('UPDATE users SET lang = "en" WHERE id = ("%s")' % message.from_user.id)
        conn.commit()
        cur.close()
        conn.close()
    else:
        bot.send_message(message.from_user.id, 'just push on button')
        bot.register_next_step_handler(message, on_click)


@bot.message_handler(commands=['data'])  # just command to check data
def data(call):
    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    info = ''
    print(users)
    for el in users:
        info += f'id: {el[0]}, язык {el[-1]}' # idk why but el[1] return None. Check all, but dont know why this work like this
    cur.close()
    conn.close()

    bot.send_message(call.chat.id, info)


@bot.message_handler(content_types=['text'])
def get_weather(message):
    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    lang = ''
    for el in users:
        if el[0] == message.from_user.id:
            lang = el[-1]
    cur.close()
    conn.close()

    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric&lang={lang}')
    data = json.loads(res.text)  # this use for take readable info from json request
    try:
        weather = data["weather"][0]['main']
        if weather == 'Clouds':
            img = 'free-icon-cloudy-day-9073957.png'
        elif weather == 'Rain':
            img = 'free-icon-heavy-rain-9073919 (1).png'
        elif weather == 'Snow':
            img = 'snowing.png'
        else:
            img = 'free-icon-cloudy-day-9073957.png'
        file = open('./' + img, 'rb')

        temp = data["main"]["temp"]
        weather_dis = data["weather"][0]['description']
        if lang == 'ru':
            bot.reply_to(message, f'Температура: {temp}° \nПогода : {weather_dis.capitalize()}')
        elif lang == 'en':
            bot.reply_to(message, f'Temperature: {temp}° \nWeather : {weather_dis.capitalize()}')
        bot.send_photo(message.chat.id, file)
    except KeyError:
        if lang == 'ru':
            bot.reply_to(message, 'Я не могу обработать этот запрос, неверно набран город')
        elif lang == 'en':
            bot.reply_to(message, 'I cant process this request, wrong city')


bot.polling(none_stop=True)
