import sqlite3

def setup():
    conn = sqlite3.connect('movies.db')  # Создаем файл базы данных
    cursor = conn.cursor()

    # Создаем таблицу для фильмов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID фильма
        code TEXT UNIQUE NOT NULL,             -- Код фильма
        title_ru TEXT NOT NULL,                -- Название фильма на русском
        title_uz TEXT NOT NULL,                -- Название фильма на узбекском
        image_url TEXT                         -- Ссылка на изображение
    )
    ''')

    # Создаем таблицу для пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,                -- ID пользователя
        username TEXT,                         -- Username
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата добавления
    )
    ''')

    # Создаем таблицу для каналов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movie_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID канала
        channel_url TEXT UNIQUE NOT NULL       -- Ссылка на канал
    )
    ''')

    conn.commit()  # Сохраняем изменения
    conn.close()   # Закрываем соединение

if __name__ == '__main__':
    setup()
