import json
import time
from threading import Thread
import telebot, wikipedia, re, os
from dotenv import load_dotenv
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()
bot = telebot.TeleBot(os.getenv("API_KEY"))

try:
    with open("settings.json", 'r', encoding='utf-8') as j:
        settings = json.loads(j.read())
except:
    settings = {}
bot_work = True

alphabet = ' 1234567890-йцукенгшщзхъфывапролджэячсмитьбюёqwertyuiopasdfghjklzxcvbnm?%.,()!:;'


def getwiki(s, lang):
    try:
        page = wikipedia.page(s)
        wikitext = page.content[:1000]
        wiki_url = page.url
        wikimas = wikitext.split('.')
        wikimas = wikimas[:-1]
        wikitext2 = ''
        for x in wikimas:
            if not ('==' in x):
                if (len((x.strip())) > 3):
                    wikitext2 = wikitext2 + x + '.'
            else:
                break
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2 + f"\n{wiki_url}"
    except Exception as e:
        if lang == "ru":
            return f'В энциклопедии нет информации об {s}\n\nВозможно следует уточнить запрос'
        else:
            return f'The encyclopaedia has no information on ' \
                   f'{s}\n\nPerhaps the request should be clarified'


@bot.message_handler(commands=['start'])
def start_message(message):
    global settings
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/help")
    btn2 = types.KeyboardButton("/lang")
    markup.add(btn1, btn2)
    settings[str(message.from_user.id)] = "ru"
    bot.send_message(message.from_user.id, '👋 Привет! Я твой бот-помощник!', reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_message(message):
    if settings[str(message.from_user.id)] == "ru":
        bot.send_message(message.chat.id,
                         "Бот предназначен для поиска статей на Wikipedia\n\nДля начала поиска отправьте любое "
                         "сообщение\n\nTo change language use command /lang")
    else:
        bot.send_message(message.chat.id,
                         "The bot is designed to search for Wikipedia articles \n\nTo start a search, send any "
                         "message \n\nДля изменения языка используйте команду /lang")


@bot.message_handler(commands=['lang'])
def lang_change(message):
    if settings[str(message.from_user.id)] == "ru":
        settings[str(message.from_user.id)] = "en"
        bot.send_message(message.chat.id, "Language change")
    else:
        settings[str(message.from_user.id)] = "ru"
        bot.send_message(message.chat.id, "Язык изменён")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global settings
    try:
        wikipedia.set_lang(settings[str(message.from_user.id)])
        bot.send_message(message.from_user.id, getwiki(message.text, settings[str(message.from_user.id)]))
    except:
        start_message(message)

def saver():
    global bot_work, settings
    while bot_work:
        with open('settings.json', "w", encoding='utf-8') as f:
            json.dump(settings, f)
        time.sleep(5)


thread = Thread(target=saver)
thread.start()
bot.polling(none_stop=True)
bot_work = False
