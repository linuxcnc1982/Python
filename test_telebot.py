import telebot
import sqlite3,requests
import os
from dotenv import load_dotenv
from typing import Final
import logging
import asyncio
from telebot.async_telebot import AsyncTeleBot

TOKEN='6889510436:AAFdV8cnLmxl8R67Rr2iihlXy4VwcHtcz-E'
bot = AsyncTeleBot(TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

CHAT_ID :Final ='-1002068836030'
DB_FILE = 'test_sqlite.db'


def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
    "chat_id": CHAT_ID,
    "text": text
    }
    response = requests.post(url, json=params)
    if response.status_code == 200:
        print("Сообщение успешно отправлено")
    else:
        print("Ошибка при отправке сообщения")
def get_exp(SN:str)->list:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    #cursor.execute(f'SELECT Devices."ExpDate", DeviceType."DeviceType" FROM Devices INNER JOIN Devices ON (Devices."DeviceType"=DeviceType."Key") WHERE SerNumber={SN}')
    cursor.execute("SELECT ExpDate,Сertificate,DeviceType FROM Devices WHERE SerNumber = ?", (SN,))
    exp,cert,dev = cursor.fetchone()
    #try:
        #cert=exp[0]
        #dev=exp[1]
        #print (cert)
        #print(dev)
    #except BaseException:
    #    print('Error')
    #for exp in cursor:
    #    print(exp) 
    #cursor.execute(f'SELECT Device,Key FROM DeviceType WHERE Key={dev}')
    #dev_= cursor.fetchall()
    #print (exp)

    print(f'{exp} {cert} {dev}')
    # Выводим результаты
   
    # Закрываем соединение
    connection.close()
    return exp,cert,dev

def get_device(SN:str)->str:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT DeviceType FROM Devices WHERE SerNumber = ?", (SN,))
    dev = cursor.fetchone()
    print(dev)
    cursor.execute("SELECT Device FROM DeviceType WHERE Key=?",dev)
    device=cursor.fetchone()
    print(device)
    # Выводим результаты
    for device in device:
        print(device)
    
    # Закрываем соединение
    connection.close()
    return device

def get_mydev(id:str)->list:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    # Выбираем всех пользователей
    cursor.execute("SELECT * FROM Devices WHERE Owner = ?", (id,))
    mydev=cursor.fetchall()
    return mydev



def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
       load_dotenv(dotenv_path)
    TOKEN=os.getenv('TOKEN')
    print(TOKEN)
    print('Starting bot...')

    asyncio.run(bot.polling())

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)

if __name__ =='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass