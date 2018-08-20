import os
import re

import numpy as np
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

import config
from face_recognition_model import FaceR
from loader import load_group

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

model = FaceR()


def error(bot, update, err):
    logger.warning('Update "%s" caused error "%s"', update, err)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Взгляд кошьки грация картошьки')


def send_images(bot, chat_id, images_names, peoples=None):
    url = "https://api.telegram.org/bot" + config.token + "/sendPhoto"
    caption = ''
    for img_name in images_names:
        files = {'photo': open('groups/-80270762/GoTo Camp SPb 2017/' + img_name, 'rb')}
        data = {'chat_id': chat_id}
        r = requests.post(url, files=files, data=data)
        print(r.status_code, r.reason, r.content)
    if peoples is not None:
        for name in list(peoples.keys()):
            caption += name + ': ' + peoples[name] + '\n'
        bot.send_message(chat_id=chat_id, text=caption, disable_web_page_preview=True)


def photo_handler(bot, update):
    file_id = update.message.photo[-1].file_id
    file = bot.getFile(file_id)

    source = 'user_face/'
    photo = str(file_id)

    file.download('user_face/' + str(file_id))
    update.message.reply_text('Фото загружено, ждите - мы ищем вас)')

    model.user_photo(source, photo)

    another_source = "users/"
    photos = [i for i in os.listdir(another_source) if i[-4:] == '.jpg']
    model.users_photos(source, photos)

    another_another_source = "groups/-80270762/GoTo Camp Summer 07_2018"
    vk_imgs = [i for i in os.listdir(another_another_source)]

    names_list = model.album_recog(vk_imgs)

    for img_index in range(5):
        send_images(bot, update.message.chat_id, [names_list[img_index], names_list[img_index + 1]])


def message_handler(bot, update):
    links = re.findall(r'vk.com+/(?P<group_name>\w+)', update.message.text)
    group_name = links[0]

    bot.send_message(chat_id=update.message.chat_id, text='Искаем вас на пикчах паблика: ' + group_name + ' ...\n'
                                                          'Если наш бот получил запрос на эту группу впервые, то '
                                                          'это может занять продолжительное время')
    print(load_group(group_name))
    bot.send_message(chat_id=update.message.chat_id, text='Пикчи из группы загружены')
    oops = np.random.randint(0, 200, 4)
    images = [str(i) + '.jpg' for i in oops]
    send_images(
        bot,
        update.message.chat_id,
        images, {}
    )


def main():
    updater = Updater(config.token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(MessageHandler(Filters.photo, photo_handler))

    # dp.add_handler(MessageHandler(Filters.text, message_handler))

    dp.add_error_handler(error)

    print('bot started')

    # updater.start_webhook(listen='0.0.0.0',
    #                       port=PORT,
    #                       url_path=config.token)
    # updater.bot.set_webhook('https://f1nd-me-bot.herokuapp.com/' + config.token)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
