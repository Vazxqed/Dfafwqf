from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3
import nest_asyncio
import asyncio

# Применение патча для событийного цикла
nest_asyncio.apply()

ADMIN_ID = [707355088]  # Укажите ваш Telegram ID

# Подключение к базе данных
def connect_db():
    return sqlite3.connect('movies.db')

# Функция для отправки кнопок
async def send_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Добавить фильм", callback_data='/add_movie')],
        [InlineKeyboardButton("Удалить фильм", callback_data='/delete_movie')],
        [InlineKeyboardButton("Просмотр фильмов", callback_data='/view_movies')],
        [InlineKeyboardButton("Добавить канал", callback_data='/add_channel')],
        [InlineKeyboardButton("Удалить канал", callback_data='/delete_channel')],
        [InlineKeyboardButton("Просмотр каналов", callback_data='/view_channels')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите команду:', reply_markup=reply_markup)

# Команда для обработки нажатия на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    command = query.data

    # Отправка команды, как если бы она была написана вручную
    if command:
        await context.bot.send_message(chat_id=query.message.chat_id, text=command)
        await update.message.reply_text(f"Выполнена команда: {command}")

# Команда для добавления фильма
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        code, title_ru, title_uz, image_url = context.args
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO movies (code, title_ru, title_uz, image_url) VALUES (?, ?, ?, ?)''', (code, title_ru, title_uz, image_url))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"Фильм '{title_ru}' добавлен!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Команда для удаления фильма
async def delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        code = context.args[0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM movies WHERE code = ?', (code,))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"Фильм с кодом '{code}' удален!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Команда для просмотра фильмов
async def view_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT code, title_ru FROM movies')
    movies = cursor.fetchall()
    conn.close()

    if not movies:
        await update.message.reply_text("Список фильмов пуст.")
    else:
        reply = "Список фильмов:\n" + "\n".join([f"{code}: {title}" for code, title in movies])
        await update.message.reply_text(reply)

# Команда для добавления канала
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        channel_url = context.args[0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO movie_channels (channel_url) VALUES (?)', (channel_url,))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"Канал '{channel_url}' добавлен!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Команда для удаления канала
async def delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        channel_url = context.args[0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM movie_channels WHERE channel_url = ?', (channel_url,))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"Канал '{channel_url}' удален!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Команда для просмотра каналов
async def view_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT channel_url FROM movie_channels')
    channels = cursor.fetchall()
    conn.close()

    if not channels:
        await update.message.reply_text("Список каналов пуст.")
    else:
        reply = "Список каналов:\n" + "\n".join([channel for (channel,) in channels])
        await update.message.reply_text(reply)

# Основной обработчик
async def main():
    application = Application.builder().token("7935650526:AAHwI7XNQRfKfbn02A3oVjuGIOP_FqoAgFU").build()

    # Добавляем команду для кнопок
    application.add_handler(CommandHandler("start", send_buttons))
    
    # Обработчик нажатий на кнопки
    application.add_handler(CallbackQueryHandler(button))
    
    # Добавляем команды для выполнения
    application.add_handler(CommandHandler("add_movie", add_movie))
    application.add_handler(CommandHandler("delete_movie", delete_movie))
    application.add_handler(CommandHandler("view_movies", view_movies))
    application.add_handler(CommandHandler("add_channel", add_channel))
    application.add_handler(CommandHandler("delete_channel", delete_channel))
    application.add_handler(CommandHandler("view_channels", view_channels))

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
