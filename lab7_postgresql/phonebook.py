import psycopg2
from connect import get_connection, get_cursor
 
 
# ──────────────────────────────────────────────
# Создание таблицы + загрузка функций/процедур
# ──────────────────────────────────────────────
 
def setup():
    conn = get_connection()
    cur  = get_cursor(conn)
 
    # Создаём таблицу
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id    SERIAL PRIMARY KEY,
            name  VARCHAR(255) NOT NULL UNIQUE,
            phone VARCHAR(20)  NOT NULL
        )
    """)
 
    # Загружаем функции и процедуры из SQL файлов
    with open("functions.sql", "r", encoding="utf-8") as f:
        cur.execute(f.read())
 
    with open("procedures.sql", "r", encoding="utf-8") as f:
        cur.execute(f.read())
 
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Таблица и функции готовы")
 
 
# ──────────────────────────────────────────────
# 1. Поиск по паттерну
# ──────────────────────────────────────────────
 
def search_phonebook(pattern: str):
    conn = get_connection()
    cur  = get_cursor(conn)
 
    cur.execute("SELECT * FROM search_phonebook(%s);", (pattern,))
    rows = cur.fetchall()
 
    cur.close()
    conn.close()
    return rows
 
 
# ──────────────────────────────────────────────
# 2. Вставить или обновить одного пользователя
# ──────────────────────────────────────────────
 
def upsert_user(name: str, phone: str):
    conn = get_connection()
    cur  = get_cursor(conn)
 
    cur.execute("CALL upsert_user(%s, %s);", (name, phone))
    conn.commit()
 
    cur.close()
    conn.close()
 
 
# ──────────────────────────────────────────────
# 3. Массовая вставка с валидацией телефонов
# ──────────────────────────────────────────────
 
def upsert_many(names: list, phones: list):
    conn = get_connection()
    cur  = get_cursor(conn)
 
    cur.execute(
        "CALL upsert_many_users(%s::varchar[], %s::varchar[]);",
        (names, phones)
    )
 
    cur.execute("SELECT * FROM invalid_entries;")
    invalid = cur.fetchall()
 
    conn.commit()
    cur.close()
    conn.close()
    return invalid
 
 
# ──────────────────────────────────────────────
# 4. Пагинация
# ──────────────────────────────────────────────
 
def get_page(page_size: int = 5, page_number: int = 1):
    conn = get_connection()
    cur  = get_cursor(conn)
 
    cur.execute(
        "SELECT * FROM get_phonebook_page(%s, %s);",
        (page_size, page_number)
    )
    rows = cur.fetchall()
 
    cur.close()
    conn.close()
    return rows
 
 
# ──────────────────────────────────────────────
# 5. Удаление по имени или телефону
# ──────────────────────────────────────────────
 
def delete_user(name: str = None, phone: str = None):
    conn = get_connection()
    cur  = get_cursor(conn)
 
    cur.execute("CALL delete_user(%s, %s);", (name, phone))
    conn.commit()
 
    cur.close()
    conn.close()
 
 
# ──────────────────────────────────────────────
# Запуск
# ──────────────────────────────────────────────
 
if __name__ == "__main__":
 
    setup()
 
    print("\n--- Upsert одиночный ---")
    upsert_user("Aibek Dzhaksybekov", "+77011234567")
    upsert_user("Dana Nurlanova",     "+77029876543")
    upsert_user("Marat Seitkali",     "+77015550001")
    upsert_user("Zarina Askarova",    "+77044445566")
    # Обновление — Aibek уже есть, только телефон изменится
    upsert_user("Aibek Dzhaksybekov", "+77010000001")
    print("Готово")
 
    print("\n--- Массовая вставка ---")
    names  = ["Aliya Bekova", "Timur Omarov", "BadUser",    ""]
    phones = ["+77056667788", "+77099998877", "not-a-phone", "+77011111111"]
 
    invalid = upsert_many(names, phones)
    if invalid:
        print("❌ Некорректные записи:")
        for row in invalid:
            print(f"   имя={row['name']!r}  телефон={row['phone']!r}  причина={row['reason']}")
 
    print("\n--- Поиск ---")
    for row in search_phonebook("Dana"):
        print(dict(row))
 
    for row in search_phonebook("+7701"):
        print(dict(row))
 
    print("\n--- Пагинация ---")
    print("Страница 1:", [dict(r) for r in get_page(3, 1)])
    print("Страница 2:", [dict(r) for r in get_page(3, 2)])
 
    print("\n--- Удаление ---")
    delete_user(name="Marat Seitkali")
    delete_user(phone="+77044445566")
    print("Удалено")
 
    print("\n--- Все записи ---")
    for row in get_page(100):
        print(dict(row))
