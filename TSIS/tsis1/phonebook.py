import psycopg2, csv, json
from connect import get_conn

# ── Init ──────────────────────────────────────────────────────────

def init_db():
    conn = get_conn(); cur = conn.cursor()
    for fname in ("schema.sql", "procedures.sql"):
        with open(fname) as f:
            cur.execute(f.read())
    conn.commit(); cur.close(); conn.close()
    print("DB ready.")

# ── Helpers ───────────────────────────────────────────────────────

def get_group_id(cur, name):
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None

def print_rows(rows, headers):
    if not rows:
        print("  (nothing found)")
        return
    for row in rows:
        line = "  |  ".join(str(v) if v else "-" for v in row)
        print(" ", line)

# ── 1. Add contact ────────────────────────────────────────────────

def add():
    name     = input("Name: ").strip()
    email    = input("Email (enter to skip): ").strip() or None
    birthday = input("Birthday yyyy-mm-dd (enter to skip): ").strip() or None
    print("Groups: Family / Work / Friend / Other")
    group    = input("Group (enter to skip): ").strip() or None
    phone    = input("Phone (+7701...): ").strip()
    ptype    = input("Phone type (home/work/mobile): ").strip() or "mobile"

    conn = get_conn(); cur = conn.cursor()
    gid = get_group_id(cur, group) if group else None
    cur.execute(
        "INSERT INTO contacts (name,email,birthday,group_id) VALUES (%s,%s,%s,%s) RETURNING id",
        (name, email, birthday, gid)
    )
    cid = cur.fetchone()[0]
    cur.execute("INSERT INTO phones (contact_id,phone,type) VALUES (%s,%s,%s)", (cid, phone, ptype))
    conn.commit(); cur.close(); conn.close()
    print("Added.")

# ── 2. Show all ───────────────────────────────────────────────────

def show_all():
    print("Sort by: 1. name  2. birthday  3. date added")
    s = input("> ").strip()
    order = {"1": "c.name", "2": "c.birthday", "3": "c.created"}.get(s, "c.name")
    conn = get_conn(); cur = conn.cursor()
    cur.execute(f"""
        SELECT c.name, c.email, c.birthday::text, g.name,
               string_agg(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ')
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        GROUP BY c.name, c.email, c.birthday, g.name, c.created
        ORDER BY {order} NULLS LAST
    """)
    print("\n  Name  |  Email  |  Birthday  |  Group  |  Phones")
    print("  " + "-"*60)
    print_rows(cur.fetchall(), [])
    cur.close(); conn.close()

# ── 3. Search ─────────────────────────────────────────────────────

def search():
    q = input("Search (name / email / phone): ").strip()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (q,))
    print("\n  Name  |  Email  |  Phone  |  Group")
    print("  " + "-"*50)
    print_rows(cur.fetchall(), [])
    cur.close(); conn.close()

# ── 4. Filter by group ────────────────────────────────────────────

def filter_group():
    g = input("Group name: ").strip()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT c.name, c.email, ph.phone, ph.type
        FROM contacts c
        LEFT JOIN phones ph ON ph.contact_id = c.id
        JOIN  groups g ON g.id = c.group_id
        WHERE g.name ILIKE %s
        ORDER BY c.name
    """, (g,))
    print_rows(cur.fetchall(), [])
    cur.close(); conn.close()

# ── 5. Add phone to existing contact ─────────────────────────────

def add_phone():
    name  = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    ptype = input("Type (home/work/mobile): ").strip() or "mobile"
    conn = get_conn(); cur = conn.cursor()
    cur.execute("CALL add_phone(%s,%s,%s)", (name, phone, ptype))
    conn.commit(); cur.close(); conn.close()
    print("Phone added.")

# ── 6. Move to group ──────────────────────────────────────────────

def move_group():
    name  = input("Contact name: ").strip()
    group = input("New group: ").strip()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("CALL move_to_group(%s,%s)", (name, group))
    conn.commit(); cur.close(); conn.close()
    print(f"Moved to {group}.")

# ── 7. Delete ─────────────────────────────────────────────────────

def delete():
    name = input("Name to delete: ").strip()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE name ILIKE %s", (name,))
    conn.commit(); cur.close(); conn.close()
    print("Deleted.")

# ── 8. Import CSV ─────────────────────────────────────────────────

def import_csv():
    path = input("CSV path (default: contacts.csv): ").strip() or "contacts.csv"
    conn = get_conn(); cur = conn.cursor()
    count = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cur.execute("SELECT id FROM contacts WHERE name=%s", (row["name"],))
            if cur.fetchone():
                print(f"  Skipping duplicate: {row['name']}")
                continue
            gid = get_group_id(cur, row.get("group")) if row.get("group") else None
            cur.execute(
                "INSERT INTO contacts (name,email,birthday,group_id) VALUES (%s,%s,%s,%s) RETURNING id",
                (row["name"], row.get("email") or None, row.get("birthday") or None, gid)
            )
            cid = cur.fetchone()[0]
            if row.get("phone"):
                cur.execute("INSERT INTO phones (contact_id,phone,type) VALUES (%s,%s,%s)",
                            (cid, row["phone"], row.get("type","mobile")))
            count += 1
    conn.commit(); cur.close(); conn.close()
    print(f"Imported {count} contacts.")

# ── 9. Export JSON ────────────────────────────────────────────────

def export_json():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT c.name, c.email, c.birthday::text, g.name,
               json_agg(json_build_object('phone', ph.phone, 'type', ph.type))
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        GROUP BY c.name, c.email, c.birthday, g.name
    """)
    result = []
    for name, email, bday, grp, phones in cur.fetchall():
        result.append({"name": name, "email": email, "birthday": bday,
                       "group": grp, "phones": phones})
    cur.close(); conn.close()
    with open("contacts.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(result)} contacts to contacts.json.")

# ── 10. Import JSON ───────────────────────────────────────────────

def import_json():
    path = input("JSON path (default: contacts.json): ").strip() or "contacts.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    conn = get_conn(); cur = conn.cursor()
    for c in data:
        cur.execute("SELECT id FROM contacts WHERE name=%s", (c["name"],))
        existing = cur.fetchone()
        if existing:
            ans = input(f"  '{c['name']}' exists — (s)kip / (o)verwrite? ").strip().lower()
            if ans != "o":
                continue
            cur.execute("DELETE FROM contacts WHERE id=%s", (existing[0],))
        gid = get_group_id(cur, c.get("group")) if c.get("group") else None
        cur.execute(
            "INSERT INTO contacts (name,email,birthday,group_id) VALUES (%s,%s,%s,%s) RETURNING id",
            (c["name"], c.get("email"), c.get("birthday"), gid)
        )
        cid = cur.fetchone()[0]
        for ph in c.get("phones") or []:
            if ph.get("phone"):
                cur.execute("INSERT INTO phones (contact_id,phone,type) VALUES (%s,%s,%s)",
                            (cid, ph["phone"], ph.get("type","mobile")))
    conn.commit(); cur.close(); conn.close()
    print("JSON import done.")

# ── 11. Paginated browse ──────────────────────────────────────────

def paginate():
    size = 2; offset = 0
    conn = get_conn(); cur = conn.cursor()
    while True:
        cur.execute("""
            SELECT c.name, g.name, string_agg(ph.phone, ', ')
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.name, g.name, c.created
            ORDER BY c.created
            LIMIT %s OFFSET %s
        """, (size, offset))
        rows = cur.fetchall()
        print(f"\n  --- Page (showing {offset+1}-{offset+len(rows)}) ---")
        print_rows(rows, [])
        if not rows:
            print("  End of list."); offset = max(0, offset - size); continue
        cmd = input("  [n]ext / [p]rev / [q]uit: ").strip().lower()
        if   cmd == "n": offset += size
        elif cmd == "p": offset = max(0, offset - size)
        elif cmd == "q": break
    cur.close(); conn.close()



# ── Menu ──────────────────────────────────────────────────────────


init_db()
while True:
    print("""
  1.  Show all (with sort)
  2.  Add contact
  3.  Search (name / email / phone)
  4.  Filter by group
  5.  Add phone to contact
  6.  Move contact to group
  7.  Delete contact
  8.  Import CSV
  9.  Export JSON
  10. Import JSON
  11. Browse pages
  0.  Exit
    """)
    choice = input("> ").strip()
    if   choice == "1":  show_all()
    elif choice == "2":  add()
    elif choice == "3":  search()
    elif choice == "4":  filter_group()
    elif choice == "5":  add_phone()
    elif choice == "6":  move_group()
    elif choice == "7":  delete()
    elif choice == "8":  import_csv()
    elif choice == "9":  export_json()
    elif choice == "10": import_json()
    elif choice == "11": paginate()
    elif choice == "0":  break