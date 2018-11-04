#! /usr/bin/env python
# -*- coding: utf-8 -*-
import tempfile
from telebot import types
import telebot
from zipfile import ZipFile
import logging
from PIL import Image
import pytesseract
import cv2
import os


API_TOKEN = '585299899:AAGxkkmOKgJY8t8wYUyLgaAwQtuu95FT0B4'

dic = {'А': 'A', 'а': 'a', 'Ә': 'Á', 'ә': 'á', 'Б': 'B', 'б': 'b', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
       'Ф': 'F', 'ф': 'f', 'Ғ': 'Ǵ', 'ғ': 'ǵ', 'Г': 'G', 'г': 'g', 'Х': 'H', 'х': 'h', 'І': 'I', 'і': 'i',
       'И': 'I', 'и': 'ı', 'Й': 'I', 'й': 'ı', 'Һ': 'H', 'һ': 'h', 'Ж': 'J', 'ж': 'j', 'К': 'K', 'к': 'k',
       'Л': 'L', 'л': 'l', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n', 'Ң': 'Ń', 'ң': 'ń', 'О': 'O', 'о': 'o',
       'Ө': 'Ó', 'ө': 'ó', 'П': 'P', 'п': 'p', 'Қ': 'Q', 'қ': 'q', 'Р': 'R', 'р': 'r', 'Ш': 'Sh', 'ш': 'sh',
       'С': 'S', 'с': 's', 'Т': 'T', 'т': 't', 'Ұ': 'U', 'ұ': 'u', 'Ү': 'Ú', 'ү': 'ú', 'В': 'V', 'в': 'v',
       'Ы': 'Y', 'ы': 'y', 'У': 'Ý', 'у': 'ý', 'З': 'Z', 'з': 'z', 'Ч': 'Ch', 'ч': 'ch', 'Э': 'E', 'э': 'e',
       'Щ': '', 'щ': '', 'Ь': '', 'ь': '', 'Ъ': '', 'ъ': '', 'Я': 'Ia', 'я': 'ia', 'Ц': 'Ts', 'ц': 'ts'}

alphabet = ['А', 'а', 'Ә', 'ә', 'Б', 'б', 'Д', 'д', 'Е', 'е', 'Ф', 'ф', 'Ғ', 'ғ', 'Г', 'г', 'Х', 'х',
            'І', 'і', 'И', 'и', 'Й', 'й', 'Һ', 'һ', 'Ж', 'ж', 'К', 'к', 'Л', 'л', 'М', 'м', 'Н', 'н',
            'Ң', 'ң', 'О', 'о', 'Ө', 'ө', 'П', 'п', 'Қ', 'қ', 'Р', 'р', 'Ш', 'ш', 'С', 'с', 'Т', 'т',
            'Ұ', 'ұ', 'Ү', 'ү', 'В', 'в', 'Ы', 'ы', 'У', 'у', 'З', 'з', 'Ч', 'ч', 'Э', 'э', 'Щ', 'щ',
            'Ь', 'ь', 'Ъ', 'ъ', 'Я', 'я', 'Ц', 'ц']

preprocess = "thresh"
bot = telebot.TeleBot(API_TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['📖 Помощь', '⚙️ Настройки']])
    bot.send_message(message.chat.id, '*✨ Привет, ' + message.chat.first_name + '!*', parse_mode='Markdown', reply_markup=keyboard)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['❓ Как это работает?']])
    bot.send_message(message.chat.id,'*С помощью, Вы можете конвертировать текст, документы, картинки на казахскую латиницу*',
                     parse_mode='Markdown', reply_markup=keyboard)



@bot.message_handler(func=lambda message: True, content_types=['text'])
def latin(message):
    textcyr = message.text
    st = str(textcyr)
    resultx = str()

    len_st = len(st)
    for i in range(0, len_st):
        if st[i] in alphabet:
            simb = dic[st[i]]
        else:
            simb = st[i]
        resultx = resultx + simb
    bot.send_message(message.chat.id, resultx)


@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    try:
        chat_id = message.chat.id
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bot.send_message(message.chat.id, '📝 Пожалуйста подождите, идет конвертирование текста на латиницу...')
        src='~/telebot/telebot_kaz/docx/'+message.document.file_name;
        with open(src, 'wb') as new_file:
          new_file.write(downloaded_file)
        bot.send_message(message.chat.id,'💾 Исходный размер файла: ' + format(os.path.getsize(src) / 1024 / 1024, '.2f') + 'Mb')
        with tempfile.TemporaryDirectory(prefix='my-encoder-') as tempdir:
            # Распаковка документа во временную папку.
            doc_x = ZipFile(src)
            doc_x.extractall(tempdir)
            doc_x.close()

            # Обработка файла, содержащего текст документа, как текстового.
            doc_xml = open(os.path.join(tempdir, 'word', 'document.xml'))
            new_xml = ''

            for line in doc_xml:
                for char in line:
                    if char in dic.keys():
                        new_xml += dic[char]
                    else:
                        new_xml += char
                new_xml += '\n'

            doc_xml.close()

            # Запись нового содержимого.
            doc_xml = open(os.path.join(tempdir, 'word', 'document.xml'), mode='w')
            doc_xml.write(new_xml)
            doc_xml.close()

            # Сборка нового документа.
            doc2_x = ZipFile(message.document.file_name, mode='w')
            for root, dirs, files in os.walk(tempdir):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(os.path.join(root, file), tempdir)
                    doc2_x.write(abs_path, rel_path)


            doc2_x.close()
            doc = open(message.document.file_name, 'rb')
            bot.send_document(chat_id,doc)
            bot.send_message(message.chat.id,'💾 Конвертированный размер файла: ' + format(os.path.getsize(message.document.file_name) / 1024 / 1024, '.2f') + 'Mb')
            os.remove(src)
            os.remove(message.document.file_name)
            #bot.send_document(message.chat.id, src)


    except Exception as e:
        bot.send_message(message.chat.id, e)


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:

        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bot.send_message(message.chat.id,'📝 Пожалуйста подождите, идет конвертирование текста на латиницу...')
        src = '~/telebot/telebot_kaz/img/' + file_info.file_path;
        image = src
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
            image = cv2.imread(image)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            if preprocess == "thresh":
                gray = cv2.threshold(gray, 0, 255,
                                     cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            elif preprocess == "blur":
                gray = cv2.medianBlur(gray, 3)
            filename = "{}.png".format(os.getpid())
            cv2.imwrite(filename, gray)
            lines = pytesseract.image_to_string(Image.open(src), lang='kaz')
            os.remove(filename)
            os.remove(src)
            for line in lines:
                lat = (''.join([dic.get(char, char) for char in lines]))
        bot.send_message(message.chat.id,'📋 Текст с изображения:')
        bot.send_message(message.chat.id, lat)

    except Exception as e:
        bot.send_message(message.chat.id, e)


@bot.callback_query_handler(func=lambda call: call.data)  # func=lambda call:True
def inline(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['Следующий >>']])
    if call.data == '❓ Как это работает?':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='*📖 Помощь (1 из 3)* \n'
                                                                                                     '\n'
                                                                                                     'Для мгновенной конвертации Вашего текста на латинский алфавит казахского языка просто отправьте сообщение с Вашим текстом боту',
                              parse_mode='Markdown',reply_markup=keyboard)
    keyboard2 = types.InlineKeyboardMarkup()
    keyboard2.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['<< Предыдущий', 'Следующий >> ']])
    if call.data == 'Следующий >>':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='*📖 Помощь (2 из 3)* \n'
                                                                                                     '\n'
                                                                                                     'Для конвертации вашего документа на латинский алфавит казахского языка просто отправьте Ваш документ боту \n'
                                                                                                     '\n'
                                                                                                     '*Внимание!* Бот принимает документы расширения docx, с другими расширениями бот работать не будет',
                              parse_mode='Markdown', reply_markup=keyboard2)
    if call.data == '<< Предыдущий':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='*📖 Помощь (1 из 3)* \n'
                                   '\n'
                                   'Для мгновенной конвертации Вашего текста на латинский алфавит казахского языка просто отправьте сообщение с Вашим текстом боту',
                              parse_mode='Markdown', reply_markup=keyboard)
    keyboard3 = types.InlineKeyboardMarkup()
    keyboard3.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['<< Предыдущий ']])
    if call.data == 'Следующий >> ':
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text='*📖 Помощь (3 из 3)* \n'
                                                                                                     '\n'
                                                                                                     'Для конвертации текста с Вашего изображения просто отправьте изображение боту\n'
                                                                                                    '\n'
                                                                                                    '*Внимание!* Чем выше качество изображения, тем лучше распознование текста с изображения', parse_mode='Markdown', reply_markup=keyboard3)


    if call.data == '<< Предыдущий ':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='*📖 Помощь (2 из 3)* \n'
                                   '\n'
                                   'Для конвертации вашего документа на латинский алфавит казахского языка просто отправьте Ваш документ боту \n'
                                   '\n'
                                   '*Внимание!* Бот принимает документы расширения docx, с другими расширениями бот работать не будет',
                              parse_mode='Markdown', reply_markup=keyboard2)
    if call.data == '⚙️ Настройки':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Для продолжения нажмите /doc', parse_mode='Markdown')




bot.polling(none_stop=True, interval=0, timeout=3)
