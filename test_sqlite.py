import sqlite3
from typing import Final
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,Update, InputTextMessageContent,InlineQueryResultArticle,InlineQueryResultsButton
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



#TOKEN :Final='6787093165:AAFuTturOQaDQ1-EGPke32e_LY9lXdbok-M'
TOKEN :Final='6889510436:AAFdV8cnLmxl8R67Rr2iihlXy4VwcHtcz-E'#gazpromcert_bot
BOT_USERNAME :Final ='bgfbfbgfbfgbfgbb_bot'
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

async def start_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [InlineKeyboardButton("Status", callback_data="3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose:", reply_markup=reply_markup)    
    await update.message.reply_text('Hello! Thanks for chatting with me!', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print('Button data is....')
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    #await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")

async def help_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
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
    return 'I do not undestand you'

async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE):
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
    s=get_exp(query.strip())
    print(len(s))
    if not s:
        return
    d=get_device(query.strip())
    #print(f'SSSS{s[0]}')
    keyboard = [
        [
            InlineKeyboardButton("More", callback_data="more"),
            InlineKeyboardButton("Take", callback_data="take"),
        ],
        [InlineKeyboardButton("Status", callback_data="status")],
    ]
    reply_markup1 = InlineKeyboardMarkup(keyboard)
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f'{d}',
            input_message_content=InputTextMessageContent(f'{d}'),
            hide_url=True,
            reply_markup=reply_markup1
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            #title="Caps",
            title=f'Its expired {s}',
            input_message_content=InputTextMessageContent(f'Its expired {s}'),
            hide_url=True
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f'Cert {s[1]}',
            input_message_content=InputTextMessageContent(f'Cert {s[1]}'),
            hide_url=True
        ),
    ]    

    #btns=InlineQueryResultsButton('Take',start_parameter='1')#,
    #InlineQueryResultsButton('More',start_parameter='2'),]
    await update.inline_query.answer(results)
    #send_message(TOKEN,CHAT_ID,f'Its expired {s}')
def btn_take(update:Update, context:ContextTypes.DEFAULT_TYPE)->None:
    #query = update.callback_query
    print('Query data is....')
    #print(query.data)
    #await query.edit_message_text(text=f"Selected option: {query.data}")

def main():
    print('Starting bot...')
    app=Application.builder().token(TOKEN).build()
    #app.add_handler(CommandHandler('start',start_command))
    app.add_handler(CommandHandler('help',help_command))
    app.add_handler(CommandHandler('mydev',custom_command))
    app.add_handler(MessageHandler(filters.TEXT,handle_message))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(button))
    #app.add_handler(ChosenInlineResultHandler(btn_take))
    app.add_error_handler(error)
    print('Polling...')
    #app.run_polling(allowed_updates=Update.ALL_TYPES,poll_interval=3)
    app.run_polling(allowed_updates=Update.ALL_TYPES,poll_interval=3)

if __name__ =='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass