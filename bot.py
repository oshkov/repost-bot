import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.context import FSMContext

import config


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
media_groups = {} # Словарь для хранения временных данных медиа-групп

# Функция создания своего текста для поста
def create_caption(text: str):
    try:
        # Разделение строки на список строк
        lines = text.splitlines()

        if len(lines) > 1:
            # Удаление последней строчки с ссылкой на канал
            lines.pop()

            # Добавление собственной ссылки на канал
            lines.append(f'<b><a href="{config.CHANNEL_URL}">{config.INVITE_TEXT}</a></b>')

        # Объединение оставшихся строк в пост
        new_text = "\n".join(lines)
        return new_text
    
    except Exception as error:
        print(f'ERROR create_caption(): {error}')


# Команда /start
@dp.message(F.text.contains("/start"))
async def accept_agreement_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на владельца бота
    if config.ADMIN_ID != str(message.from_user.id):
        return

    await message.answer('Бот запущен')


# Обработка постов
@dp.message()
async def accept_agreement_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на владельца бота
    if config.ADMIN_ID != str(message.from_user.id):
        return

    try:
        new_caption = create_caption(message.html_text)

        # Отправка поста с несколькими медиа
        if message.media_group_id:

            # Если сообщение является частью медиа-группы
            media_group_id = message.media_group_id

            # Если у этого сообщения нет своего массива с файлами то он создается
            if media_group_id not in media_groups:
                media_groups[media_group_id] = []
                first_file_in_group = True
                # new_caption = f'EDITED: {message.caption}'
            else:
                first_file_in_group = False
                # new_caption= None

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

                # Отправка поста
                await bot.send_media_group(
                    chat_id=config.CHANNEL_ID,
                    media=media_groups[media_group_id]
                )

                # Очистка словаря с медиа-группами
                media_groups.clear()

        # Отпрвка одного фото
        elif message.photo:
            await bot.send_photo(
                chat_id=config.CHANNEL_ID,
                photo=message.photo[-1].file_id,
                caption=new_caption,
                parse_mode='html'
            )

        # Отправка одного видео
        elif message.video:
            await bot.send_video(
                chat_id=config.CHANNEL_ID,
                video=message.video.file_id,
                caption=new_caption,
                parse_mode='html'
            )

        # Отправка файла
        elif message.document:
            await bot.send_document(
                chat_id=config.CHANNEL_ID,
                document=message.document.file_id,
                caption=new_caption,
                parse_mode='html'
            )

        # Отправка аудио
        elif message.audio:
            await bot.send_audio(
                chat_id=config.CHANNEL_ID,
                audio=message.audio.file_id,
                caption=new_caption,
                parse_mode='html'
            )

        # Отправка текста
        else:
            await bot.send_message(
                    chat_id=config.CHANNEL_ID,
                    text=new_caption,
                    parse_mode='html'
                )

    except Exception as error:
        print(f'ERROR: {error}')
        await message.answer(f'ERROR: {error}')


# Запуск бота
async def start_bot():
    print('Бот запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())