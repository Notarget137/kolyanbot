import random
import telebot
import configparser
import sqlite3
import threading

defaultConfigPath = './bot_config.conf'

def init_config(config_path : str):
    config = configparser.ConfigParser()
    config.read(config_path)
    botToken = config['DEFAULT']['BotToken']
    shitRate = config['DEFAULT']['ShitRate']
    kolyanId = config['DEFAULT']['KolyanId']
    DBPath = config['DEFAULT']['DBPath']
    return botToken, float(shitRate), int(kolyanId), DBPath

botToken, shitRate, kolyanId, DBPath = init_config(defaultConfigPath)

db_connection = sqlite3.connect(DBPath, check_same_thread=False, isolation_level=None)
lock = threading.Lock()

cursor = db_connection.cursor()

def init_db():
    cursor.execute('CREATE TABLE IF NOT EXISTS reply_messages(submitted_by bigint NOT NULL, message_text text NOT NULL UNIQUE)')
    cursor.execute('CREATE TABLE IF NOT EXISTS admins(id bigint NOT NULL UNIQUE)')


def check_admin(id : int):
    cursor.execute('SELECT id FROM admins WHERE id = ?', [id])
    if cursor and list(cursor):
        return True
    return False


kolyabot = telebot.TeleBot(botToken)

def check_reply(message : telebot.types.Message):
    user_id = message.from_user.id
    if user_id == kolyanId:
        return True
    if message.text.startswith('/test') and check_admin(user_id):
        return True
    return False


@kolyabot.message_handler(func=check_reply, content_types=['audio', 'photo', 'voice', 'video', 'document',
                                                                    'text', 'location', 'contact', 'sticker'])
def reply_message(message : telebot.types.Message):
    cursor.execute("SELECT message_text FROM reply_messages ORDER BY RANDOM() LIMIT 1")
    randomReply = list(cursor)[0]
    if random.random() > shitRate:
        kolyabot.reply_to(message, text=randomReply)

@kolyabot.message_handler(commands=['add'])
def add_reply(message : telebot.types.Message):
    if check_admin(message.from_user.id):
        user_id = message.from_user.id
        text = message.text[4:].strip()
        try:
            cursor.execute('INSERT INTO reply_messages(submitted_by, message_text) VALUES (?, ?)', [user_id, text])
        except sqlite3.IntegrityError as e:
            kolyabot.reply_to(message, 'Не добавил ебать ты че')
        else:
            kolyabot.reply_to(message, 'Базар жок')

@kolyabot.message_handler(commands=['grant'])
def add_admin(message : telebot.types.Message):
    print(message.from_user.full_name)
    if 'POTNOFMOB' in message.text:
        print('huj')
        user_id = message.from_user.id
        cursor.execute('INSERT INTO admins(id) VALUES (?)', [user_id])


def main():
    init_db()
    kolyabot.infinity_polling()

if __name__ == '__main__':
    main()
