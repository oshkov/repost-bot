import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.context import FSMContext
import threading
import time

import config
import utils


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
media_groups = {} # Словарь для хранения временных данных медиа-групп
posts_query = []


# Команда /start
@dp.message(F.text.contains("/start"))
async def accept_agreement_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на владельца бота
    if config.ADMIN_ID != str(message.from_user.id):
        return

    await message.answer('Бот запущен')


# Команда /posts
@dp.message(F.text.contains("/posts"))
async def posts_amount(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на владельца бота
    if config.ADMIN_ID != str(message.from_user.id):
        return

    await message.answer(f'Постов в очереди: {len(posts_query)}')


# Обработка постов
@dp.message()
async def accept_agreement_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на владельца бота
    if config.ADMIN_ID != str(message.from_user.id):
        return

    try:
        new_caption = utils.create_caption(message.html_text)

        # Отправка поста с несколькими медиа
        if message.media_group_id:

            # Если сообщение является частью медиа-группы
            media_group_id = message.media_group_id

            # Если у этого сообщения нет своего массива с файлами то он создается
            if media_group_id not in media_groups:
                media_groups[media_group_id] = []
                first_file_in_group = True
            else:
                first_file_in_group = False

            # Доабвление фото и видео
            try:
                media_groups[media_group_id].append(
                    InputMediaPhoto(
                        media=message.photo[-1].file_id,
                        caption= new_caption,
                        parse_mode='html',
                        has_spoiler=message.has_media_spoiler
                    )
                )
            except:
                media_groups[media_group_id].append(
                    InputMediaVideo(
                        media=message.video.file_id,
                        caption= new_caption,
                        parse_mode='html',
                        has_spoiler=message.has_media_spoiler
                    )
                )

            # После первого файла создается задержка для получения всех файлов, после чего отправляются все файлы в канал
            if first_file_in_group:

                # Задержка 2 сек
                await asyncio.sleep(2)

                posts_query.append({
                    'post_type': 'media_group',
                    'media': media_groups[media_group_id],
                    'caption': new_caption
                })

                # Очистка словаря с медиа-группами
                media_groups.clear()

        # Отпрвка одного фото
        elif message.photo:
            posts_query.append({
                'post_type': 'photo',
                'photo': message.photo[-1].file_id,
                'caption': new_caption
            })

        # Отправка одного видео
        elif message.video:
            posts_query.append({
                'post_type': 'video',
                'video': message.video.file_id,
                'caption': new_caption
            })

        # Отправка файла
        elif message.document:
            posts_query.append({
                'post_type': 'document',
                'document': message.document.file_id,
                'caption': new_caption
            })

        # Отправка аудио
        elif message.audio:
            posts_query.append({
                'post_type': 'audio',
                'document': message.audio.file_id,
                'caption': new_caption
            })

        # Отправка текста
        else:
            posts_query.append({
                'post_type': 'message',
                'caption': new_caption
            })

    except Exception as error:
        print(f'ERROR: {error}')
        await message.answer(f'ERROR: {error}')




# Запуск бота
async def start_bot():
    print('Бот запущен')
    await dp.start_polling(bot)

# Автопостинг постов
async def autoposting():
    while True:
        # Задержка на час
        await asyncio.sleep(3600)

        # Проверка на наличие постов в очереди
        if len(posts_query) != 0:
            try:
                if posts_query[0]['post_type'] == 'media_group':
                    await bot.send_media_group(
                        chat_id=config.CHANNEL_ID,
                        media=posts_query[0]['media']
                    )

                elif posts_query[0]['post_type'] == 'photo':
                    await bot.send_photo(
                        chat_id=config.CHANNEL_ID,
                        photo=posts_query[0]['photo'],
                        caption=posts_query[0]['caption'],
                        parse_mode='html'
                    )

                elif posts_query[0]['post_type'] == 'video':
                    await bot.send_video(
                        chat_id=config.CHANNEL_ID,
                        video=posts_query[0]['video'],
                        caption=posts_query[0]['caption'],
                        parse_mode='html'
                    )

                elif posts_query[0]['post_type'] == 'document':
                    await bot.send_document(
                        chat_id=config.CHANNEL_ID,
                        document=posts_query[0]['document'],
                        caption=posts_query[0]['caption'],
                        parse_mode='html'
                    )

                elif posts_query[0]['post_type'] == 'audio':
                    await bot.send_audio(
                        chat_id=config.CHANNEL_ID,
                        audio=posts_query[0]['audio'],
                        caption=posts_query[0]['caption'],
                        parse_mode='html'
                    )

                elif posts_query[0]['post_type'] == 'message':
                    await bot.send_message(
                        chat_id=config.CHANNEL_ID,
                        text=posts_query[0]['caption'],
                        parse_mode='html'
                    )
            except Exception as error:
                print(f'ERROR autoposting: {error}')
            
            posts_query.pop(0)

# Объединение запуска бота и автопостинга
async def main():
    await asyncio.gather(
        start_bot(),
        autoposting()
    )

if __name__ == '__main__':
    asyncio.run(main())