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
import datetime
from datetime import datetime
import pytest
import csv


CHAT_ID :Final ='-1002068836030'
DB_FILE = 'ronktd'
TOKEN=''


def try_get_tgID(FN:str):
    """Попытаемся получить по ФИО TelegramId из БД"""
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()  
    req=(f"SELECT FIO FROM AllUsers WHERE TgId='{FN}'")
    print(req)
    try:
        cursor.execute(req)
        ret = cursor.fetchmany(1)
    except:
        err=('None')
        return err
    finally:
        connection.close()
    return ret

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

def convert_exp():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()  
    
    ret:str
    i=1
    while i < 342:
        #req=(f"SELECT ExpDate,Key FROM Prombez WHERE key={i}")
        req=(f"SELECT ExpDate,Key FROM Certificates WHERE key={i}")
        cursor.execute(req)        
        ret,key=cursor.fetchone() 
        print(ret)
        ret=ret.strip()
        YYYY=ret[6]+ret[7]+ret[8]+ret[9]
        MM=ret[3]+ret[4]
        DD=ret[0]+ret[1]
        date_=(f"{YYYY}-{MM}-{DD}")
        print(date_)
        #req1=(f"UPDATE Prombez SET ExpDateUS = '{date_}' WHERE Key={i}")
        req1=(f"UPDATE Certificates SET ExpDateUS = '{date_}' WHERE Key={i}")
        cursor.execute(req1)
        connection.commit()
        i=i+1
    connection.close()
    return

def get_prombez(FN:str,start_date,end_date)->list:
    user_id=get_user_id(FN)
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()   
    req=(f"SELECT Education.Name,ExpDate,Certificate,Protocol FROM Prombez,Education WHERE USER={user_id} AND Prombez.Education=Education.Key AND ExpDateUs BETWEEN '{start_date}' AND '{end_date}'")
    print(req)
    try:
        cursor.execute(req)
        ret = cursor.fetchmany(10)
        print(ret)
        return ret
    except:
        err=('None')
        return err
    finally:
        connection.close()


def get_user_id(FN:str)->str:
    print(FN)
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()   
    req=(f"SELECT DISTINCT Key FROM AllUsers WHERE FIO LIKE '{FN}%'")
    print(req)
    try:
        cursor.execute(req)
        user_id = cursor.fetchall()
        user_id= clear_FIO(user_id)
        print(user_id)
        connection.close()
        return user_id
    except:
        err=('None')
        return err
    finally:
        connection.close()

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
    finally:
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
    finally:
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
    finally:
        connection.close()
    return  ret#fio,exp,cert,method

def notify_me(tgId:str,notify:int):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()   
    req=(f"UPDATE AllUsers SET Notify={notify} WHERE TgId = '{tgId}'")
    print(req)
    cursor.execute(req)
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()

def set_tgId(FN:str,tgId:str):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()   
    print(FN)
    req=(f"UPDATE AllUsers SET TgId = {tgId} WHERE FIO = '{FN}'")
    print(req)
    cursor.execute(req)
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
 
def clear_FIO(s)->str:
    s=str(s).replace('(','')
    s=str(s).replace(')','')
    s=str(s).replace("'",'')
    s=str(s).replace(',','')
    s=str(s).replace('[','')
    s=str(s).replace(']','')
    return s

def prepare(list, expired)->str:
    list=str(list).replace('[','\n')
    if expired:
        list=str(list).replace('(','❌ ')
    else:
        list=str(list).replace('(','✅ ')
        #list=str(list).replace('(','✔️ ')
    list=str(list).replace(')','\n')
    list=str(list).replace("'",'')
    list=str(list).replace(',','')
    list=str(list).replace(']','')
    return list    

def get_date()->str:
    now = datetime.now() 
    return now.strftime("%Y-%m-%d")

# Define a `/start` command handler.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        "РОНКТД, НАКС, Промбезопасность",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Поиск обучений",
                web_app=WebAppInfo(url="https://gazpromcert-1be08.web.app"),
            )
        ),
    )

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

    if query.data=='prombez':
        
        print('prombez')
        list=get_prombez(FIOsearch,get_date(),'2100-01-01')  

    if query.data=='its_my':
        print('its_my')
        keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="yes"),
            InlineKeyboardButton("Нет", callback_data="no"),
        ],]
        reply_markup1 = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup1)
        return


    if query.data=='notify':
        print('notify')
        FIO=try_get_tgID(query.from_user.id)
        if len(FIO)==0:
            await query.edit_message_text(text=f"Необходимо привязать TelegramID")
        else:
            notify_me(query.from_user.id,1)
            await query.edit_message_text(text=f"Вы подписаны на уведомления")

    if query.data=='cancel':
        print('notify')
        FIO=try_get_tgID(query.from_user.id)
        if len(FIO)==0:
            await query.edit_message_text(text=f"Необходимо привязать TelegramID")
        else:
            notify_me(query.from_user.id,0)
            await query.edit_message_text(text=f"Вы отписались от уведомлений")

    if query.data=='yes':
        print('yes')
        set_tgId(FIOsearch,query.from_user.id) 
        await query.edit_message_text(text=f"{FIOsearch} соответствует TgId={query.from_user.id}")
        return
    
    if query.data=='no':
        print('no')
        await query.edit_message_text(text=f"Ну и ладно")
    list=prepare(list,False)
    print(list)
     # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    #await query.answer()
    #await query.edit_message_text(text=f"Selected option: {query.data}")
    await query.edit_message_text(text=f"👷 {FIOsearch} {list}")
async def help_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    #convert_exp()
    await update.message.reply_text('I can help you!')

async def custom_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(update.message.from_user.id)
    FIO=try_get_tgID(update.message.from_user.id)
    if (len(FIO)==0):
        await update.message.reply_text(f'Не найдено')
        return
    print(FIO)
    FIO=clear_FIO(FIO)
    print(FIO)
    now = datetime.now() 
    list=get_cert(FIO)
    list2=get_prombez(FIO,'1950-01-01',get_date())
    list22=get_prombez(FIO,get_date(),'2100-01-01')
    list3=get_cert_naks(FIO)           
    list=prepare(list,False)
    list2=prepare(list2,True)
    list22=prepare(list22,False) 
    list3=prepare(list3,False)    
    print(list)
    await update.message.reply_text(f'РОНКТД {list}\nПромбез {list2} {list22}\nНАКС {list3}')

async def csv_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    #await update.message.reply_text(f'Не реализовано')    
    await update._bot.send_document(update.message.from_user.id,'1.csv')
    return

def test_runonce ():
    assert True,"Error"
#@pytest.fixture


async def pdf_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
    await update._bot.send_document(update.message.from_user.id,'1.pdf')
    return

async def notify_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
        FIO=try_get_tgID(update.message.from_user.id)
        if not FIO:
            await update.message.reply_text(text=f"Необходимо привязать TelegramID")
        else:
            notify_me(update.message.from_user.id,1)
            await update.message.reply_text(text=f"Вы подписаны на уведомления")

async def cancel_command(update: Update, context:ContextTypes.DEFAULT_TYPE):
        FIO=try_get_tgID(update.message.from_user.id)
        if not FIO:
            await update.message.reply_text(text=f"Необходимо привязать TelegramID")
        else:
            notify_me(update.message.from_user.id,0)
            await update.message.reply_text(text=f"Вы отписались от уведомлений")


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
    if not s:
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
        keyboard = [
        [
            InlineKeyboardButton("РОНКТД", callback_data="ronktd"),
            InlineKeyboardButton("НАКС", callback_data="naks"),
        ],

        [InlineKeyboardButton("Промбезопасность", callback_data="prombez"),],

        [InlineKeyboardButton("Это я!",callback_data="its_my"),
         InlineKeyboardButton("Уведомлять",callback_data="notify"),
         InlineKeyboardButton("Отменить", callback_data="cancel"),
        ]]
        reply_markup1 = InlineKeyboardMarkup(keyboard)
        i=0
        results=list()
        while i < (len(s)):
            if len(s[i])>0:
                #s=clear_FIO(s)
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
    await update.inline_query.answer(results)
    
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
    app.add_handler(CommandHandler('help',help_command))
    app.add_handler(CommandHandler('start',start))
    app.add_handler(CommandHandler('myedu',custom_command))
    app.add_handler(CommandHandler('csv',csv_command))
    app.add_handler(CommandHandler('pdf',pdf_command))
    app.add_handler(CommandHandler('notify',notify_command))
    app.add_handler(CommandHandler('cancel',cancel_command))
    app.add_handler(MessageHandler(filters.TEXT,handle_message))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(ChosenInlineResultHandler(btn_take))
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
