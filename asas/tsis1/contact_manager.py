import csv, json, os, sys
from datetime import datetime
import psycopg2, psycopg2.extras

DB = dict(host="localhost", port=5432, dbname="contacts_db", user="postgres", password="")
PAGE = 5

def conn():
    return psycopg2.connect(**DB)

def cur(c):
    return c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# ── display ───────────────────────────────────────────────────────────────────

def show(rows):
    for r in rows:
        phones = r.get("phones") or "—"
        print(f"  [{r['id']:>4}] {r['name']:<28} {str(r.get('email') or '—'):<28}"
              f" bday:{str(r.get('birthday') or '—'):<12} "
              f"grp:{str(r.get('group_name') or '—'):<10} ph:{phones}")

# ── 3.2 browse ────────────────────────────────────────────────────────────────

def browse():
    grp   = input("Group filter (blank=all): ").strip() or None
    email = input("Email search (blank=skip): ").strip() or None
    sort  = input("Sort [name/birthday/date_added]: ").strip() or "name"
    sort  = {"name":"c.name","birthday":"c.birthday NULLS LAST","date_added":"c.created_at"}.get(sort,"c.name")

    where, params = [], []
    if grp:   where.append("g.name ILIKE %s");  params.append(grp)
    if email: where.append("c.email ILIKE %s"); params.append(f"%{email}%")
    w = ("WHERE " + " AND ".join(where)) if where else ""

    sql = f"""SELECT c.id,c.name,c.email,c.birthday,g.name AS group_name,
                     STRING_AGG(p.phone||' ('||p.type||')',', ') AS phones
              FROM contacts c
              LEFT JOIN groups g ON g.id=c.group_id
              LEFT JOIN phones p ON p.contact_id=c.id
              {w} GROUP BY c.id,c.name,c.email,c.birthday,g.name
              ORDER BY {sort} LIMIT %s OFFSET %s"""

    offset = 0
    with conn() as c:
        with cur(c) as cr:
            cr.execute(f"SELECT COUNT(*) AS n FROM contacts c LEFT JOIN groups g ON g.id=c.group_id {w}", params)
            total = cr.fetchone()["n"]
            pages = max(1, (total + PAGE - 1) // PAGE)
            while True:
                cr.execute(sql, params + [PAGE, offset])
                print(f"\n  Page {offset//PAGE+1}/{pages}  ({total} contacts)")
                show(cr.fetchall())
                cmd = input("  [next/prev/quit] > ").strip().lower()
                if cmd == "next" and offset + PAGE < total: offset += PAGE
                elif cmd == "prev" and offset > 0:          offset -= PAGE
                elif cmd in ("quit","q"):                   break

# ── 3.2 search ────────────────────────────────────────────────────────────────

def search():
    q = input("Query: ").strip()
    with conn() as c:
        with cur(c) as cr:
            cr.execute("SELECT * FROM search_contacts(%s)", (q,))
            show(cr.fetchall())

# ── 3.3 json export ───────────────────────────────────────────────────────────

def export_json():
    path = input("Output file [export.json]: ").strip() or "export.json"
    with conn() as c:
        with cur(c) as cr:
            cr.execute("""SELECT c.name,c.email,c.birthday,g.name AS grp,
                                 JSON_AGG(JSON_BUILD_OBJECT('phone',p.phone,'type',p.type))
                                 FILTER(WHERE p.id IS NOT NULL) AS phones
                          FROM contacts c
                          LEFT JOIN groups g ON g.id=c.group_id
                          LEFT JOIN phones p ON p.contact_id=c.id
                          GROUP BY c.name,c.email,c.birthday,g.name ORDER BY c.name""")
            rows = [dict(r) for r in cr.fetchall()]
    json.dump(rows, open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print(f"  ✓ Exported {len(rows)} contacts → {path}")

# ── 3.3 json import ───────────────────────────────────────────────────────────

def _group_id(cr, name):
    if not name: return None
    cr.execute("INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING", (name,))
    cr.execute("SELECT id FROM groups WHERE name=%s", (name,))
    return cr.fetchone()["id"]

def import_json():
    path = input("Input file [export.json]: ").strip() or "export.json"
    records = json.load(open(path, encoding="utf-8"))
    ins = skp = ovr = 0
    with conn() as c:
        with cur(c) as cr:
            for r in records:
                name = r.get("name","").strip()
                if not name: continue
                cr.execute("SELECT id FROM contacts WHERE name=%s", (name,))
                ex = cr.fetchone()
                if ex:
                    ch = input(f"  Duplicate '{name}' [s]kip/[o]verwrite? ").strip().lower()
                    if ch != "o": skp += 1; continue
                    cr.execute("UPDATE contacts SET email=%s,birthday=%s,group_id=%s WHERE id=%s",
                               (r.get("email"),r.get("birthday"),_group_id(cr,r.get("grp")),ex["id"]))
                    cr.execute("DELETE FROM phones WHERE contact_id=%s", (ex["id"],))
                    cid = ex["id"]; ovr += 1
                else:
                    cr.execute("INSERT INTO contacts(name,email,birthday,group_id) VALUES(%s,%s,%s,%s) RETURNING id",
                               (name,r.get("email"),r.get("birthday"),_group_id(cr,r.get("grp"))))
                    cid = cr.fetchone()["id"]; ins += 1
                for ph in (r.get("phones") or []):
                    cr.execute("INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s)",
                               (cid, ph.get("phone"), ph.get("type","mobile")))
        c.commit()
    print(f"  ✓ inserted:{ins} overwritten:{ovr} skipped:{skp}")

# ── 3.3 csv import ────────────────────────────────────────────────────────────

def import_csv():
    path = input("CSV file [contacts.csv]: ").strip() or "contacts.csv"
    ins = upd = 0
    with conn() as c:
        with cur(c) as cr, open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
            for r in reader:
                name = r.get("name","").strip()
                if not name: continue
                bday = None
                for fmt in ("%Y-%m-%d","%d.%m.%Y"):
                    try: bday = datetime.strptime(r.get("birthday","").strip(), fmt).date(); break
                    except: pass
                gid   = _group_id(cr, r.get("group","").strip())
                phone = r.get("phone","").strip() or None
                ptype = r.get("phone_type","mobile").strip().lower() or "mobile"
                cr.execute("SELECT id FROM contacts WHERE name=%s", (name,))
                ex = cr.fetchone()
                if ex:
                    cr.execute("UPDATE contacts SET email=COALESCE(%s,email),birthday=COALESCE(%s,birthday),"
                               "group_id=COALESCE(%s,group_id) WHERE id=%s",
                               (r.get("email") or None, bday, gid, ex["id"]))
                    cid = ex["id"]; upd += 1
                else:
                    cr.execute("INSERT INTO contacts(name,email,birthday,group_id) VALUES(%s,%s,%s,%s) RETURNING id",
                               (name, r.get("email") or None, bday, gid))
                    cid = cr.fetchone()["id"]; ins += 1
                if phone:
                    cr.execute("SELECT 1 FROM phones WHERE contact_id=%s AND phone=%s",(cid,phone))
                    if not cr.fetchone():
                        cr.execute("INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s)",(cid,phone,ptype))
        c.commit()
    print(f"  ✓ inserted:{ins} updated:{upd}")

# ── stored proc wrappers ──────────────────────────────────────────────────────

def add_phone():
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type [home/work/mobile]: ").strip() or "mobile"
    with conn() as c:
        with c.cursor() as cr: cr.execute("CALL add_phone(%s,%s,%s)", (name,phone,ptype))
        c.commit()
    print("  ✓ Done")

def move_group():
    name  = input("Contact name: ").strip()
    group = input("Group name:   ").strip()
    with conn() as c:
        with c.cursor() as cr: cr.execute("CALL move_to_group(%s,%s)", (name,group))
        c.commit()
    print("  ✓ Done")

# ── main ──────────────────────────────────────────────────────────────────────

MENU = """
  1  Browse / filter / sort / paginate
  2  Search (name / email / phone)
  3  Add phone  (stored proc)
  4  Move to group  (stored proc)
  5  Export → JSON
  6  Import ← JSON
  7  Import ← CSV
  0  Exit
"""
ACTIONS = {"1":browse,"2":search,"3":add_phone,"4":move_group,
           "5":export_json,"6":import_json,"7":import_csv}

if __name__ == "__main__":
    try:
        conn().cursor().execute("SELECT 1")
        print("Connected.")
    except Exception as e:
        print(f"DB error: {e}"); sys.exit(1)

    while True:
        print(MENU)
        a = ACTIONS.get(input("Choice > ").strip())
        if a is None: break
        try: a()
        except Exception as e: print(f"  Error: {e}")
