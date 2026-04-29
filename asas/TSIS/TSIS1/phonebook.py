import csv
import json
from connect import connect


def add_contact():
    conn = connect()
    cur = conn.cursor()

    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group_name = input("Group: ")
    phone = input("Phone: ")
    phone_type = input("Phone type (home/work/mobile): ")

    cur.execute("SELECT id FROM groups WHERE name=%s", (group_name,))
    group = cur.fetchone()

    if group:
        group_id = group[0]
    else:
        cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (group_name,))
        group_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (name, email, birthday, group_id))

    contact_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO phones(contact_id, phone, type)
        VALUES (%s, %s, %s)
    """, (contact_id, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added successfully!")


def filter_by_group():
    conn = connect()
    cur = conn.cursor()

    group_name = input("Enter group: ")

    cur.execute("""
        SELECT c.name, c.email, c.birthday
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s
    """, (group_name,))

    rows = cur.fetchall()

    if not rows:
        print("No contacts found.")
    else:
        for row in rows:
            print(row)

    cur.close()
    conn.close()


def search_by_email():
    conn = connect()
    cur = conn.cursor()

    email = input("Search email: ")

    cur.execute("""
        SELECT name, email
        FROM contacts
        WHERE email ILIKE %s
    """, ('%' + email + '%',))

    rows = cur.fetchall()

    if not rows:
        print("No contacts found.")
    else:
        for row in rows:
            print(row)

    cur.close()
    conn.close()


def sort_contacts():
    conn = connect()
    cur = conn.cursor()

    field = input("Sort by (name/birthday/date): ")

    if field == "date":
        field = "created_at"

    if field not in ["name", "birthday", "created_at"]:
        print("Invalid sort field.")
        cur.close()
        conn.close()
        return

    cur.execute(f"SELECT name, email, birthday FROM contacts ORDER BY {field}")

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def export_json():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
    """)

    rows = cur.fetchall()
    contacts = []

    for row in rows:
        contacts.append({
            "name": row[0],
            "email": row[1],
            "birthday": str(row[2]),
            "group": row[3],
            "phone": row[4],
            "type": row[5]
        })

    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=4)

    cur.close()
    conn.close()
    print("Exported to contacts.json")


def import_json():
    conn = connect()
    cur = conn.cursor()

    with open("contacts.json", "r") as f:
        contacts = json.load(f)

    for c in contacts:
        cur.execute("SELECT id FROM contacts WHERE name=%s", (c["name"],))
        existing = cur.fetchone()

        if existing:
            choice = input(f"{c['name']} exists. skip/overwrite: ").lower()

            if choice == "skip":
                continue
            elif choice == "overwrite":
                cur.execute("DELETE FROM contacts WHERE name=%s", (c["name"],))
            else:
                continue

        cur.execute("SELECT id FROM groups WHERE name=%s", (c["group"],))
        group = cur.fetchone()

        if group:
            group_id = group[0]
        else:
            cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (c["group"],))
            group_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (c["name"], c["email"], c["birthday"], group_id))

        contact_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO phones(contact_id, phone, type)
            VALUES (%s, %s, %s)
        """, (contact_id, c["phone"], c["type"]))

    conn.commit()
    cur.close()
    conn.close()
    print("Imported from contacts.json")


def import_csv():
    conn = connect()
    cur = conn.cursor()

    with open("contacts.csv", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute("SELECT id FROM groups WHERE name=%s", (row["group"],))
            group = cur.fetchone()

            if group:
                group_id = group[0]
            else:
                cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (row["group"],))
                group_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (row["name"], row["email"], row["birthday"], group_id))

            contact_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, row["phone"], row["type"]))

    conn.commit()
    cur.close()
    conn.close()
    print("CSV imported successfully!")


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Add Contact")
        print("2. Filter by Group")
        print("3. Search by Email")
        print("4. Sort Contacts")
        print("5. Export to JSON")
        print("6. Import from JSON")
        print("7. Import from CSV")
        print("8. Exit")

        choice = input("Choose: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            filter_by_group()
        elif choice == "3":
            search_by_email()
        elif choice == "4":
            sort_contacts()
        elif choice == "5":
            export_json()
        elif choice == "6":
            import_json()
        elif choice == "7":
            import_csv()
        elif choice == "8":
            break
        else:
            print("Invalid choice.")


menu()