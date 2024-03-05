import sqlite3
from typing import Final
from telegram import InlineKeyboardButton,KeyboardButton, ReplyKeyboardMarkup, WebAppInfo,ReplyKeyboardRemove, InlineKeyboardMarkup,Update, InputTextMessageContent,InlineQueryResultArticle,InlineQueryResultsButton
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes, InlineQueryHandler,ChosenInlineResultHandler
from paho.mqtt import client as mqtt_client
import random
import time
from threading import Thread
import requests
import logging
from html import escape
from uuid import uuid4
from telegram.constants import ParseMode
import os
from dotenv import load_dotenv
import json

CHAT_ID :Final ='-1002068836030'
DB_FILE = 'ronktd'
TOKEN=''

def try_get_tgID(str:FIO):
    return None

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

def get_FIO(FN:str)->list:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()   
    req=(f"SELECT DISTINCT FIO FROM AllUsers WHERE FIO LIKE '{FN}%'")
    print(req)
    try:
        cursor.execute(req)
        ret = cursor.fetchmany(10)
    except:
        err=('None')
        return err
    print(ret)
    connection.close()
    return  ret

def get_cert_naks(FN:str)->list:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()   
    print(FN)
    req=(f"SELECT Stamp,ExpDate,NumCert FROM Certificates_NAKS WHERE FIO LIKE '{FN}%'")
    print(req)
    try:
        cursor.execute(req)
        #fio,exp,cert,method = cursor.fetchone()
        ret  = cursor.fetchall()
    except:
        err=('None','None','None','None')
        return err
    #print(f'{fio} {exp} {cert} {method}')
    #print(ret)
    connection.close()
    return  ret#fio,exp,cert,method

def get_cert(FN:str)->list:
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()   
    print(FN)
    req=(f"SELECT Method,ExpDate,NumCert FROM Certificates WHERE FIO LIKE '{FN}%'")
    print(req)
    try:
        cursor.execute(req)
        #fio,exp,cert,method = cursor.fetchone()
        ret  = cursor.fetchall()
    except:
        err=('None','None','None','None')
        return err
    #print(f'{fio} {exp} {cert} {method}')
    #print(ret)
    connection.close()
    return  ret#fio,exp,cert,method

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

# Define a `/start` command handler.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Поиск приборов",
                web_app=WebAppInfo(url="https://gazpromcert-1be08.web.app"),
            )
        ),
    )
    # """Sends a message with three inline buttons attached."""
    # keyboard = [
    #     [
    #         InlineKeyboardButton("Option 1", callback_data="1"),
    #         InlineKeyboardButton("Option 2", callback_data="2"),
    #     ],
    #     [InlineKeyboardButton("Status", callback_data="3")],
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # await update.message.reply_text("Please choose:", reply_markup=reply_markup)    
    # await update.message.reply_text('Hello! Thanks for chatting with me!', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print('Button data is....')
    print(FIOsearch)
    if query.data=='ronktd':
        print('ronktd')
        list=get_cert(FIOsearch)
        
    if query.data=='naks':
        print('naks')
        list=get_cert_naks(FIOsearch)    
        
    list=str(list).replace('[','\n')
    list=str(list).replace('(','✔️ ')
    list=str(list).replace(')','\n')
    list=str(list).replace("'",'')
    list=str(list).replace(',','')
    list=str(list).replace(']','')
    print(list)
     # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    #await query.answer()
    #await query.edit_message_text(text=f"Selected option: {query.data}")
    await query.edit_message_text(text=f"👷 {FIOsearch} {list}")
async def help_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    await update._bot.send_document(172287348,'2024-02-12_results.xls')
    await update.message.reply_text('I can help you!')

async def custom_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    s=get_mydev(update.message.from_user.id)
    if not s:    
        await update.message.reply_text('Приборов не записано')
    else:
        await update.message.reply_text(f'{s}')

def handle_response(text:str) -> str:
    processed: str=text.lower()
    if ("hello") in processed:
        return 'Hey there!'

    if ('how are you') in processed:
        return 'Im good!'
    #return 'I do not undestand you'

async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE):
    global FIOsearch
    FIOsearch=update.message.text 
    message_type:str=update.message.chat.type
    text:str=update.message.text
    print(f'User({update.message.chat.id})in {message_type}:"{text}"')
    print(update.message.from_user.name)
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME,'').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    print('Bot',response)
    await update.message.reply_text(response)

async def error (update:Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} cause error {context.error}')

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    
    if not query:  # empty query should not be handled
        return
    s=get_FIO(query.strip())     

    print(len(s))
    if len(s)==0:
        print('Not found')
        results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f'Нет данных',
            input_message_content=InputTextMessageContent(f'Нет данных'),
            hide_url=True
            ),
        ]    
    else:
         #   return
        #d=get_device(query.strip())
        #print(f'SSSS{s[0]}')
        keyboard = [
        [
            InlineKeyboardButton("РОНКТД", callback_data="ronktd"),
            InlineKeyboardButton("НАКС", callback_data="naks"),
        ],
        [InlineKeyboardButton("Промбезопасность", callback_data="prombez")],
        ]
        reply_markup1 = InlineKeyboardMarkup(keyboard)
        i=0
        results=list()
        while i < (len(s)):
            if len(s[i])>0:
                s[i]=str(s[i]).replace('(','')
                s[i]=str(s[i]).replace(')','')
                s[i]=str(s[i]).replace("'",'')
                s[i]=str(s[i]).replace(',','')
                results.append(InlineQueryResultArticle(
                        id=str(uuid4()),
                        title=f'{s[i]}',
                        input_message_content=InputTextMessageContent(f'{s[i]}'),
                        hide_url=True,
                        reply_markup=reply_markup1
                    ))
            i=i+1
        print(results)
        #     InlineQueryResultArticle(
        #         id=str(uuid4()),
        #         #title="Caps",
        #         title=f'Its expired {s[1]}',
        #         input_message_content=InputTextMessageContent(f'Its expired {s[1]}'),
        #         hide_url=True
        #     ),
        #     InlineQueryResultArticle(
        #         id=str(uuid4()),
        #         title=f'Cert {s[2]}',
        #         input_message_content=InputTextMessageContent(f'Cert {s[2]}'),
        #         hide_url=True
        #     ),
        #     InlineQueryResultArticle(
        #         id=str(uuid4()),
        #         title=f'Method {s[3]}',
        #         input_message_content=InputTextMessageContent(f'Method {s[3]}'),
        #         hide_url=True
        #     ),
        # ]    

    #btns=InlineQueryResultsButton('Take',start_parameter='1')#,
    #InlineQueryResultsButton('More',start_parameter='2'),]
    await update.inline_query.answer(results)
    #send_message(TOKEN,CHAT_ID,f'Its expired {s}')
def btn_take(update:Update, context:ContextTypes.DEFAULT_TYPE)->None:
    query = update.callback_query
    print('Query data is....')
    print(query.data.text)
    #await query.edit_message_text(text=f"Selected option: {query.data}")

    # Handle incoming WebAppData
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print the received data and remove the button."""
    # Here we use `json.loads`, since the WebApp sends the data JSON serialized string
    # (see webappbot.html)
    print("We are here...")
    print(update.effective_message.web_app_data.data)
    # await update.message.reply_html(
    #     text=(
    #         f"You selected the color with the HEX value <code>{data['hex']}</code>. The "
    #         f"corresponding RGB value is <code>{tuple(data['rgb'].values())}</code>."
    #     ),
    #     reply_markup=ReplyKeyboardRemove(),
    # )

def main():
    print('Starting bot...')
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
       load_dotenv(dotenv_path)
    TOKEN=os.getenv('TOKEN')
    print(TOKEN)
    app=Application.builder().token(TOKEN).build()
    #app.add_handler(CommandHandler('start',start_command))
    app.add_handler(CommandHandler('help',help_command))
    app.add_handler(CommandHandler('start',start))
    app.add_handler(CommandHandler('mydev',custom_command))
    app.add_handler(MessageHandler(filters.TEXT,handle_message))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(ChosenInlineResultHandler(btn_take))
    #app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    app.add_error_handler(error)
    print('Polling...')
    #app.run_polling(allowed_updates=Update.ALL_TYPES,poll_interval=3)
  
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ =='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass


# naks_bot, [01.03.2024 15:52]
# ✅ МР-26АЦ-I-25156 от 07.12.2023
# ПРОВЕРИТЬ ПО ССЫЛКЕ:
# http://u.naks.ru/nCw6sli2pajc0mUdxdmaS5hXyJDggs5k

# naks_bot, [01.03.2024 15:52]
# ❌ МР-26АЦ-I-16978 от 01.12.2021
# ПРОВЕРИТЬ ПО ССЫЛКЕ:
# http://u.naks.ru/ODNuIC9EqXDIlZl+rEbazmTvZwid2BYb
