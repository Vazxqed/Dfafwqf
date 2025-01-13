import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters
import logging
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Настроим логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание и подключение к базе данных
def init_db():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            language TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            movie_code TEXT PRIMARY KEY,
            title_ru TEXT,
            title_uz TEXT,
            image_url TEXT,
            video_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Функция для получения текста на текущем языке
def get_text(key, language):
    texts = {
        'start': {'ru': "Добро пожаловать! Выберите действие:", 'uz': "Xush kelibsiz! Amalni tanlang:"},
        'search_movie': {'ru': "Введите код фильма:", 'uz': "Film kodini kiriting:"},
        'invalid_code': {'ru': "Неверный код! Попробуйте снова.", 'uz': "Kod noto‘g‘ri! Yana urinib ko‘ring."},
        'subscribe_prompt': {
            'ru': "Подпишитесь на каналы и нажмите 'Проверить подписку'.",
            'uz': "Kanallarga obuna bo‘ling va 'Obunani tekshirish' tugmasini bosing."
        },
        'not_subscribed': {
            'ru': "Вы не подписаны на следующие каналы:",
            'uz': "Quyidagi kanallarga obuna bo‘lmagansiz:"
        },
        'loading': {'ru': "Загрузка...", 'uz': "Yuklanmoqda..."},
        'set_lang_ru': {'ru': "Язык установлен: Русский.", 'uz': "Til o‘zgartirildi: Rus tili."},
        'set_lang_uz': {'ru': "Язык установлен: Узбекский.", 'uz': "Til o‘zgartirildi: O‘zbek tili."},
        'movie_title': {'ru': "Название фильма", 'uz': "Film nomi"},
        'movie_link': {'ru': "Ссылка на видео", 'uz': "Video havolasi"}
    }
    return texts[key][language]

# Функция для отправки информации о фильме
async def send_movie_info(update: Update, movie, context: CallbackContext):
    language = context.user_data.get('language', 'ru')
    context.user_data['required_channels'] = movie.get('channels', [])
    context.user_data['movie_code'] = update.message.text.strip()

    # Выводим URL изображения в консоль для отладки
    logger.info(f"Movie Image URL: {movie['image']}")

    # Проверка и отправка изображения фильма
    if movie.get('image'):
        try:
            sent_message = await update.message.reply_photo(
                photo=movie['image'],
                caption=f"{get_text('movie_title', language)}: {movie['title'][language]}"
            )
        except Exception as e:
            logger.error(f"Error sending movie image: {e}")
            await update.message.reply_text("Произошла ошибка при отправке изображения фильма.")
            return
    else:
        await update.message.reply_text("Изображение для этого фильма недоступно.")

    # Клавиатура для подписки на каналы
    keyboard = [
        [InlineKeyboardButton(
            f"Obuna bo‘lish: {channel}" if language == 'uz' else f"Подписаться на {channel}",
            url=f"https://t.me/{channel[1:]}"
        )] for channel in movie['channels']
    ]
    keyboard.append([InlineKeyboardButton(
        "Obunani tekshirish" if language == 'uz' else "Проверить подписку",
        callback_data="check_subscription"
    )])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        get_text('subscribe_prompt', language),
        reply_markup=reply_markup
    )

    # Сохраняем сообщение для дальнейшего удаления
    context.user_data['sent_message'] = sent_message

# Добавление нового пользователя в базу данных
def add_user_to_db(user_id, username, language):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute('''
      INSERT OR REPLACE INTO users (id, username)
      VALUES (?, ?)
    ''', (user_id, username))

    conn.commit()
    conn.close()

# Функция для получения фильма из базы данных
def get_movie_from_db(movie_code):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    # Используйте правильное имя столбца 'code'
    cursor.execute('''
    SELECT * FROM movies WHERE code = ?
    ''', (movie_code,))
    movie = cursor.fetchone()

    conn.close()
    
    if movie:
        return {
            'movie_code': movie[1],
            'title': {'ru': movie[2], 'uz': movie[3]},
            'image': movie[4],
            'channels': ['@dececc34d2', '@ADdamdwc' , '@fvwfeq3'] # Убедитесь, что каналы соответствуют
        }
    return None

# Обработчик команды "Искать фильм"
async def search_movie(update: Update, context: CallbackContext):
    language = context.user_data.get('language', 'ru')
    context.user_data['waiting_for_code'] = True
    await update.message.reply_text(get_text('search_movie', language))

# Обработчик кода фильма
async def get_movie_code(update: Update, context: CallbackContext):
    language = context.user_data.get('language', 'ru')
    user_code = update.message.text.strip()

    if context.user_data.get('waiting_for_code', False):
        movie = get_movie_from_db(user_code)

        if movie:
            await send_movie_info(update, movie, context)
        else:
            await update.message.reply_text(get_text('invalid_code', language))
        
        context.user_data['waiting_for_code'] = False
    else:
        await update.message.reply_text(get_text('start', language))

# Проверка подписки
# Проверка подписки
async def check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    language = context.user_data.get('language', 'ru')
    await query.answer()

    user_id = query.from_user.id
    required_channels = context.user_data.get('required_channels', [])
    not_subscribed_channels = []

    for channel in required_channels:
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                not_subscribed_channels.append(channel)
        except Exception as e:
            logger.warning(f"Error checking subscription for {channel}: {e}")
            not_subscribed_channels.append(channel)

    if not not_subscribed_channels:
        if 'sent_message' in context.user_data:
            await context.user_data['sent_message'].delete()

        loading_message = await query.edit_message_text(get_text('loading', language))
        await loading_message.delete()

        # Получаем код фильма из контекста пользователя
        movie_code = context.user_data.get('movie_code')

        if movie_code:
            # Получаем фильм из базы данных по коду
            movie = get_movie_from_db(movie_code)

            if movie:
                # Отправляем информацию о фильме
                await query.message.reply_photo(
                    photo=movie['image'],
                    caption='Film tayyor , havolaga bosing \nФильм готов , нажмите на ссылку \nhttps://t.me/fvwfeq3'
                )
            else:
                await query.message.reply_text(get_text('invalid_code', language))
        else:
            await query.message.reply_text(get_text('invalid_code', language))
    else:
        keyboard = [
            [InlineKeyboardButton(f"Obuna bo‘lish: {channel}" if language == 'uz' else f"Подписаться на {channel}",
                                  url=f"https://t.me/{channel[1:]}")]
            for channel in not_subscribed_channels
        ]
        keyboard.append([InlineKeyboardButton(
            "Obunani tekshirish" if language == 'uz' else "Проверить подписку",
            callback_data="check_subscription"
        )])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(get_text('not_subscribed', language), reply_markup=reply_markup)


# Обработчик изменения языка
async def change_language(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("O‘zbek", callback_data='lang_uz')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите язык:", reply_markup=reply_markup)

# Установка языка
async def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'lang_ru':
        context.user_data['language'] = 'ru'
        await query.edit_message_text(get_text('set_lang_ru', 'ru'))
        await show_start_buttons(update, context, 'ru')
    elif query.data == 'lang_uz':
        context.user_data['language'] = 'uz'
        await query.edit_message_text(get_text('set_lang_uz', 'uz'))
        await show_start_buttons(update, context, 'uz')

# Функция для показа начальных кнопок
async def show_start_buttons(update: Update, context: CallbackContext, language):
    query = update.callback_query
    if query:
        message = query.message
    else:
        message = update.message

    keyboard = [
        ['Искать фильм', 'Изменить язык'] if language == 'ru' else ['Film qidirish', 'Tilni o‘zgartirish']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await message.reply_text(get_text('start', language), reply_markup=reply_markup)

# Стартовая команда
async def start(update: Update, context: CallbackContext):
    language = context.user_data.get('language', 'ru')
    add_user_to_db(update.message.from_user.id, update.message.from_user.username, language)
    await show_start_buttons(update, context, language)

# Основная функция бота
def main():
    init_db()
    application = Application.builder().token(TELEGRAM_TOKEN).read_timeout(60).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(Искать фильм|Film qidirish)$'), search_movie))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(Изменить язык|Tilni o‘zgartirish)$'), change_language))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.Regex('^(Искать фильм|Film qidirish|Изменить язык|Tilni o‘zgartirish)$'), get_movie_code))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern='^check_subscription$'))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))

    application.run_polling()

if __name__ == '__main__':
    main()
