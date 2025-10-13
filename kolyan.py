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
    DBPath   = config['DEFAULT']['DBPath'  ]
    gifID    = config['DEFAULT']['gifID'   ]
    return botToken, float(shitRate), int(kolyanId), DBPath, gifID

botToken, shitRate, kolyanId, DBPath, gifID = init_config(defaultConfigPath)

db_connection = sqlite3.connect(DBPath, check_same_thread=False, isolation_level=None)
lock = threading.Lock()

cursor = db_connection.cursor()

kolyabot = telebot.TeleBot(botToken)

########################################    INIT

def init_db():
    with lock:
        cursor.execute('CREATE TABLE IF NOT EXISTS reply_messages(submitted_by bigint NOT NULL, message_text text NOT NULL UNIQUE)')
        cursor.execute('CREATE TABLE IF NOT EXISTS admins(id bigint NOT NULL UNIQUE)')

########################################    COMMON
        
def check_admin(id : int):
    with lock:
        cursor.execute('SELECT id FROM admins WHERE id = ?', [id])
        if cursor and list(cursor):
            return True
    return False

def check_reply(message : telebot.types.Message):
    user_id = message.from_user.id
    if user_id == kolyanId:
        return True
    elif kolyanId == -1337:
        return True
    if message.text.startswith('/test') and check_admin(user_id):
        return True
    return False

def random_msg(message : telebot.types.Message):
    with lock:
         cursor.execute("SELECT message_text FROM reply_messages ORDER BY RANDOM() LIMIT 1")
         rep_list = list(cursor)
         if len(rep_list) == 0:
             randomReply = 'ЭУЪ'
         else:
             randomReply = rep_list[0]
    kolyabot.reply_to(message, text=randomReply)

########################################    HANDLERS

@kolyabot.message_handler(func=check_reply, content_types=['audio', 'photo', 'voice', 'video', 'document',
                                                            'text', 'location', 'contact', 'sticker', 'animation'])
def reply_message(message : telebot.types.Message):
    if message.text:
        ltext = message.text.lower()
    elif message.caption:
        ltext = message.caption.lower()
    else:
        ltext = ''
    if not ltext:
        return
    ########## GIF
    if 'трейд' in ltext:
        kolyabot.send_animation(message.chat.id, gifID,reply_to_message_id=message.message_id)
    ########## BAZA
    elif 'каля' in ltext:
        random_msg(message)
    ########## REPLAY-TO-REPLAY-TO-BOT
    elif message.reply_to_message is not None and message.reply_to_message.from_user.id == kolyabot.get_me().id:
        random_msg(message)
    ########## TEST
    elif ltext.startswith('/test'):
        random_msg(message)
    ########## ADD
    elif ltext.startswith('/add'):
        if check_admin(message.from_user.id):
            user_id = message.from_user.id
            text = message.text[4:].strip()
            try:
                with lock:
                    cursor.execute('INSERT INTO reply_messages(submitted_by, message_text) VALUES (?, ?)', [user_id, text])
            except sqlite3.IntegrityError as e:
                kolyabot.reply_to(message, 'Не добавил ебать ты че')
            else:
                kolyabot.reply_to(message, 'Базар жок')
    ########## GRANT
    elif ltext.startswith('/grant'):
        print('request for admin:',message.from_user.full_name)
        user_id = message.from_user.id
        if 'POTNOFMOB' in message.text:
            print('granted ',user_id)
            try:
                with lock:
                    cursor.execute('INSERT INTO admins(id) VALUES (?)', [user_id])
            except sqlite3.IntegrityError as e:
                print('already added ',user_id)
            kolyabot.reply_to(message, text='ДОБАВИЛ ЖОК')
        else:
            print('refused ',user_id)
            kolyabot.reply_to(message, text='ТЫ КТО ВООБЩЕ ЭУ')

def main():
    init_db()
    #while True:
    if True:
        #try:
            kolyabot.infinity_polling(timeout=60, long_polling_timeout=60, none_stop=True)
        #except Exception as e:
        #    print(f"TeleBot: Infinity polling exception: {e}")
        #    time.sleep(1000)

if __name__ == '__main__':
    main()
