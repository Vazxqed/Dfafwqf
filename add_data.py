import sqlite3

# Функция для добавления фильма
def add_movie(code, title_ru, title_uz, image_url):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO movies (code, title_ru, title_uz, image_url)
    VALUES (?, ?, ?, ?)
    ''', (code, title_ru, title_uz, image_url))

    conn.commit()
    conn.close()

# Функция для добавления пользователя
def add_user(user_id, username):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO users (id, username)
    VALUES (?, ?)
    ''', (user_id, username))

    conn.commit()
    conn.close()

# Функция для добавления канала
def add_channel(channel_url):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO movie_channels (channel_url)
    VALUES (?)
    ''', (channel_url,))

    conn.commit()
    conn.close()

# Примеры использования
if __name__ == '__main__':
    # Добавляем фильм
    add_movie("123", "Пример фильма", "Film namunasi", "https://example.com/image.jpg")

    # Добавляем пользователя
    add_user(1, "example_user")

    # Добавляем канал
    add_channel("@channel1")
