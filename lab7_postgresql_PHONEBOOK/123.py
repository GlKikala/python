import csv
from connect import get_connection


def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name TEXT,
            phone TEXT
        )
    """)
def insert_from_console(cur):
    name = input("Name: ")
    phone = input("Phone: ")

    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)
    )
def insert_from_csv(cur):
    with open("contacts.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            name = row[0]
            phone = row[1]

            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (name, phone)
            )
def show_all(cur):
    cur.execute("SELECT * FROM phonebook")
    rows = cur.fetchall()

    for row in rows:
        print(row)
def delete_contact(cur):
    phone = input("Phone to delete: ")

    cur.execute(
        "DELETE FROM phonebook WHERE phone = %s",
        (phone,)
    )
def main():
    conn = get_connection()
    cur = conn.cursor()
    create_table(cur)
    conn.commit()
    while True:
        print("\n1. Add from console")
        print("2. Add from CSV")
        print("3. Show all")
        print("4. Delete")
        print("5. Exit")
        choice = input("Choose: ")
        if choice == "1":
            insert_from_console(cur)
        elif choice == "2":
            insert_from_csv(cur)
        elif choice == "3":
            show_all(cur)
        elif choice == "4":
            delete_contact(cur)
        elif choice == "5":
            break
        conn.commit()
    cur.close()
    conn.close()


main()
# import psycopg2

# conn = psycopg2.connect(
#     host="localhost",
#     port=5432,
#     dbname="postgres",
#     user="postgres",
#     password="newpass123"
# )

# cursor = conn.cursor()

# cursor.execute("""
#                CREATE TABLE IF NOT EXISTS users (
#                      id SERIAL PRIMARY KEY,
#                      name VARCHAR(255) NOT NULL,
#                      email VARCHAR(255) NOT NULL UNIQUE
#                 )
# """)
# conn.commit()

# while True:
#     print("--------------")
#     print("- 1. add info ")
#     print("- 2. delete info ")
#     print("- 3. update info ")
#     print("- 4. flush all info ")
#     print("- 5. exit ")
#     print("--------------")
#     if input("Enter your choice: ") == "1":
#         name = input("Enter name: ")
#         email = input("Enter email: ")
#         if name == "" or name == " " or email == "" or email == " ":
#             print("Name and email cannot be empty.")
#             continue
#         cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
#         conn.commit()
#     elif input("Enter your choice: ") == "2":
#         cursor.execute("SELECT * FROM users")
#         row = cursor.fetchall()
#         for r in row:
#             print(r)
#         while True:
#             email = input("\nEnter email to delete: ")
#             if email == " " or email == "":
#                 break
#             cursor.execute("DELETE FROM users WHERE email = %s", (email,))
#             conn.commit()
#     elif input("Enter your choice: ") == "3":
#         cursor.execute("SELECT * FROM users")
#         row = cursor.fetchall()
#         for r in row:
#             print(r)
#         while True:
#             email = input("\nEnter email to update: ")
#             if email == " " or email == "":
#                 break
#             name = input("Enter new name: ")
#             cursor.execute("UPDATE users SET name = %s WHERE email = %s", (name, email))
#             conn.commit()


# cursor.execute("SELECT * FROM users")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)