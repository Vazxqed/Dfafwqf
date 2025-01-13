import sqlite3

def view_movies():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM movies')
    movies = cursor.fetchall()
    for movie in movies:
        print(movie)

    conn.close()

def view_users():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    for user in users:
        print(user)

    conn.close()

def view_channels():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM movie_channels')
    channels = cursor.fetchall()
    for channel in channels:
        print(channel)

    conn.close()

# Примеры использования
if __name__ == '__main__':
    print("Фильмы:")
    view_movies()

    print("\nПользователи:")
    view_users()

    print("\nКаналы:")
    view_channels()
