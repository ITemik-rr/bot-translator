import telebot
import datetime
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from googletrans import Translator
from logic import *
import asyncio


bot = telebot.TeleBot(TOKEN)
user_language_map = {}



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет, я бот-переводчик. Моя главная задача — переводить тексты, которые ты скажешь."
    )
    bot.send_message(
        message.chat.id,
        "Напиши мне /help и узнаешь подробности."
    )

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,
        """Введи /language — и тебе будут доступны на выбор 6 языков: английский, немецкий, испанский, французский, китайский и арабский.

Потом введи команду /text <текст> — и получишь перевод. Если хочешь поменять язык, напиши /language.

Твои запросы сохранятся, так что ты сможешь посмотреть свои фразы."""
    )

@bot.message_handler(commands=['language'])
def choice_language(message):
    languages = {
        'en': 'Английский 🇬🇧',
        'de': 'Немецкий 🇩🇪',
        'es': 'Испанский 🇪🇸',
        'fr': 'Французский 🇫🇷',
        'zh-cn': 'Китайский 🇨🇳',
        'ar': 'Арабский 🇦🇪'
    }

    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, label in languages.items():
        btn = InlineKeyboardButton(label, callback_data=f'set_lang_{code}')
        buttons.append(btn)
    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "Выбери язык для перевода:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_lang_'))
def set_language(call):
    lang_code = call.data.split('_')[-1]
    user_id = str(call.from_user.id)
    user_language_map[user_id] = lang_code

    lang_names = {
        'en': 'английский',
        'de': 'немецкий',
        'es': 'испанский',
        'fr': 'французский',
        'zh-cn': 'китайский',
        'ar': 'арабский'
    }
    lang_name = lang_names.get(lang_code, lang_code)

    bot.answer_callback_query(call.id, f"Язык установлен: {lang_name}")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Выбран язык: {lang_name}.\n\nТеперь отправь текст для перевода — я всё сделаю!"
    )

@bot.message_handler(commands=['text'])
def text_translate(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "❌ Пожалуйста, укажи текст для перевода.\nПример: /text Привет, как дела?"
        )
        return

    text_to_translate = parts[1]
    user_id = str(message.from_user.id)
    lang = user_language_map.get(user_id)

    if not lang:
        lang = 'en'
        bot.send_message(
            message.chat.id,
            f"⚠️ Язык не был выбран, использую английский ({lang}) по умолчанию. Нажми /language, чтобы выбрать другой."
        )

    try:
        translator = Translator()
        bot.send_chat_action(message.chat.id, "typing")

        result = asyncio.run(
            translator.translate(text_to_translate, dest=lang)
        )
        translated_text = result.text

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        manager.save_translation(
            user_id=user_id,
            user_text=text_to_translate,
            translation=translated_text,
            date=now
        )

        message_text = (
            f"📄 Исходный: {text_to_translate}\n\n"
            f"🌍 Перевод ({lang}): {translated_text}"
        )
        bot.send_message(message.chat.id, message_text)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"⚠️ Ошибка при переводе: {e}"
    )

if __name__ == '__main__':
    manager = BotTranslator(DATABASE)
    bot.polling()