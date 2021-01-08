import telebot
import logging
import sqlite3
import os
import time
import threading
from telebot import types
from array import array

get_queue_name_flag = False
choosing_position_flag = False
other_position_flag = False
user_id_flag = False
enter_name_of_queue_flag = False
enter_position_flag = False
name_of_queue = ""
conn = ""
qcounter = 0

def main():
    aqueue = [' ']
    pnum = ' '
    qcounter = 0
    token = '1302515511:AAEWAVbAAwB4TqPAqpX99IisxtWScceDBKw'
    bot = telebot.TeleBot(token)
    user = bot.get_me()
    updates = bot.get_updates()
    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)
    nqueue = 0
    queue_str = "QBot"
    qname = ['']
    evt = threading.Event()
    result = None

    @bot.message_handler(content_types=['text'])
    def smth_wrong(message):
        global get_queue_name_flag
        global choosing_position_flag
        global enter_name_of_queue_flag
        global other_position_flag
        global enter_position_flag
        global user_id_flag
        global name_of_queue
        global qcounter
        global conn

        if enter_position_flag:
            enter_position_flag = False
            pos_s = message.text
            conn.execute("insert into " + name_of_queue + " (position) values (?)", (pos_s,))

        if enter_name_of_queue_flag:
            enter_name_of_queue_flag = False
            name_of_queue = message.text
            conn.execute("insert into " + name_of_queue + " (name) values (?)", (user.id,))
            bot.send_message(message.from_user.id, "Enter your position")
            enter_position_flag = True

        if user_id_flag:
            choose_position_other(message, message.text)
        if choosing_position_flag:
            position_chooser(message, nqueue, qname)
        if get_queue_name_flag:
            create_queue(message, nqueue, qname)
        if message.text.lower() == "delete queue":
            bot.send_message(message.from_user.id, "Enter name of queue for deleting")
            delete_db(message, cursor=sqlite3)
        if message.text.lower() == "choose position":
            choose_position(message, cursor=sqlite3)
        if message.text.lower() == "help":
            bot.send_message(message.from_user.id,
                             "Commands:\nCreate Queue\nQueue list\nDelete queue\nButtons\nInfo\nChoose position"
                             )
        if message.text.lower() == "buttons":
            buttons_init(message)
        if message.text.lower() == "/start":
            bot.send_message(message.from_user.id, "Hello, it's QueueBot")
            buttons_init(message)
        if message.text.lower() == "info":
            bot.send_message(message.from_user.id, "Шо ты хочешь от меня")
        if message.text.lower() == "queue list":
            queue_list(message, cursor=sqlite3)
        if message.text.lower() == "create queue":
            bot.send_message(message.from_user.id, "Enter name of queue: ")
            get_queue_name_flag = True

    def buttons_init(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Create Queue")
        button2 = types.KeyboardButton("Queue list")
        button3 = types.KeyboardButton("Help")
        markup.add(button1, button2, button3)
        bot.send_message(message.from_user.id, "ok", reply_markup=markup)

    def create_queue(message, nqueue, qname):
        global get_queue_name_flag
        global choosing_position_flag
        global other_position_flag
        global user_id_flag

        nqueue += 1
        get_queue_name_flag = False
        choosing_position_flag = True
        # temp_str = message.text.lower()
        qname = message.text.lower()
        # bot.register_next_step_handler(qname, create_queue(message, nqueue, qname))
        bot.send_message(message.from_user.id, qname)
        qcounter = create_db(message, qname)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("yes")
        button2 = types.KeyboardButton("no")
        markup.add(button1, button2)
        bot.send_message(message.from_user.id, "Would you like to choose position now?",
                         reply_markup=markup)
        pass

    def position_chooser(message, nqueue, qname):
        global get_queue_name_flag
        global choosing_position_flag
        global other_position_flag
        global user_id_flag

        choosing_position_flag = False
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("yes")
        button2 = types.KeyboardButton("no")
        markup.add(button1, button2)
        if message.text == "yes":
            choose_position(message, cursor=sqlite3)
        elif message.text == "no":
            bot.send_message(message.chat.id, "Would you like to choose position for another person?",
                             reply_markup=markup)
            if message.text == "yes":
                bot.send_message(message.chat.id, "Enter user id of person: ")
                user_id_flag = True
            elif message.text == "no":
                pass
        pass

    def queue_list(message, cursor):
        table = cursor.fetchall()
        bot.send_message(message.from_user.id, table)

    def choose_position_other(message, cursor):
        bot.send_message(message.from_user.id, "Enter name of queue")
        tqnmae = message.text
        bot.send_message(message.from_user.id, "Enter user id of person")
        operson = message.text
        bot.send_message(message.from_user.id, "Enter your position")
        pos_s = message.text
        cursor.execute("insert into " + tqnmae + " (position) values (?)", (pos_s,))
        cursor.execute("insert into " + tqnmae + " (name) values (?)", (operson,))

    def choose_position(message, cursor):
        global enter_name_of_queue_flag
        global enter_position_flag
        global name_of_queue

        bot.send_message(message.from_user.id, "Enter name of queue")
        enter_name_of_queue_flag = True
        pass

    def create_db(message, qname):
        global conn
        qcounter = + 1
        # queue_name = str(qcounter)
        conn = sqlite3.connect(qname + "data.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE "
                       + qname +
                       "(queue_name TEXT, position TEXT, name TEXT, queue_number INTEGER)"
                       )
        cursor.execute("insert into " + qname + "(queue_name) values (?)", (qname,))
        cursor.execute("insert into " + qname + "(queue_number) values (?)", (qcounter,))
        bot.send_message(message.from_user.id, "Queue added")
        conn.commit()
        return qcounter

    def delete_db(message, cursor):
        queuename = message.text
        conn.execute("DELETE FROM" + queuename)
        os.remove(queuename + "data.db")
        bot.send_message(message.from_user.id, "Queue deleted")

    bot.polling()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
