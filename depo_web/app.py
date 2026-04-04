import os
import hashlib
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "depo-gizli-anahtar-2024")

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# ── Veritabanı ────────────────────────────────────────────────────────────────
def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         SERIAL PRIMARY KEY,
            username   TEXT NOT NULL UNIQUE,
            password   TEXT NOT NULL,
            lang       TEXT DEFAULT 'tr',
            created_at TEXT DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS products (
            id        SERIAL PRIMARY KEY,
            name      TEXT    NOT NULL,
            category  TEXT    DEFAULT '',
            stock     INTEGER DEFAULT 0,
            min_stock INTEGER DEFAULT 5,
            unit      TEXT    DEFAULT 'adet',
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS movements (
            id           SERIAL PRIMARY KEY,
            product_id   INTEGER NOT NULL REFERENCES products(id),
            type         TEXT    NOT NULL CHECK(type IN ('in','out')),
            quantity     INTEGER NOT NULL,
            stock_after  INTEGER NOT NULL,
            note         TEXT    DEFAULT '',
            created_by   INTEGER REFERENCES users(id),
            created_at   TIMESTAMP DEFAULT NOW()
        );
    """)
    # Varsayılan admin kullanıcısı
    cur.execute("SELECT id FROM users WHERE username='admin'")
    if not cur.fetchone():
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            ("admin", pw))
    conn.commit()
    cur.close()
    conn.close()

# ── Yardımcılar ───────────────────────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

STRINGS = {
    "tr": {
        "dashboard":      "Kontrol Paneli",
        "products":       "Ürünler",
        "movements":      "Hareketler",
        "history":        "Geçmiş",
        "settings":       "Ayarlar",
        "logout":         "Çıkış",
        "login":          "Giriş Yap",
        "username":       "Kullanıcı Adı",
        "password":       "Şifre",
        "total":          "Toplam Ürün",
        "critical":       "Kritik Stok",
        "out_of_stock":   "Tükenen",
        "add_product":    "Ürün Ekle",
        "add_movement":   "Hareket Ekle",
        "product_name":   "Ürün Adı",
        "category":       "Kategori",
        "stock":          "Stok",
        "min_stock":      "Min. Stok",
        "unit":           "Birim",
        "type_in":        "Giriş",
        "type_out":       "Çıkış",
        "quantity":       "Miktar",
        "note":           "Not",
        "save":           "Kaydet",
        "cancel":         "İptal",
        "delete":         "Sil",
        "edit":           "Düzenle",
        "status_ok":      "Yeterli",
        "status_low":     "Kritik",
        "status_out":     "Tükendi",
        "date":           "Tarih",
        "product":        "Ürün",
        "remaining":      "Kalan",
        "no_products":    "Henüz ürün eklenmedi.",
        "no_movements":   "Henüz hareket kaydı yok.",
        "saved":          "Kaydedildi!",
        "deleted":        "Silindi!",
        "error_stock":    "Yetersiz stok!",
        "error_fields":   "Lütfen tüm alanları doldurun.",
        "confirm_delete": "Silmek istediğinize emin misiniz?",
        "search":         "Ara...",
        "welcome":        "Hoş geldiniz",
        "language":       "Dil",
        "change_password":"Şifre Değiştir",
        "new_password":   "Yeni Şifre",
        "current_password":"Mevcut Şifre",
        "in_movement":    "Giriş hareketi",
        "out_movement":   "Çıkış hareketi",
        "undo":           "Geri Al",
        "undo_confirm":   "Bu hareketi geri almak istiyor musunuz? Stok eski haline dönecektir.",
        "critical_alert": "Kritik stok seviyesinde ürünler",
    },
    "en": {
        "dashboard":      "Dashboard",
        "products":       "Products",
        "movements":      "Movements",
        "history":        "History",
        "settings":       "Settings",
        "logout":         "Logout",
        "login":          "Login",
        "username":       "Username",
        "password":       "Password",
        "total":          "Total Products",
        "critical":       "Critical Stock",
        "out_of_stock":   "Out of Stock",
        "add_product":    "Add Product",
        "add_movement":   "Add Movement",
        "product_name":   "Product Name",
        "category":       "Category",
        "stock":          "Stock",
        "min_stock":      "Min. Stock",
        "unit":           "Unit",
        "type_in":        "In",
        "type_out":       "Out",
        "quantity":       "Quantity",
        "note":           "Note",
        "save":           "Save",
        "cancel":         "Cancel",
        "delete":         "Delete",
        "edit":           "Edit",
        "status_ok":      "OK",
        "status_low":     "Low",
        "status_out":     "Out",
        "date":           "Date",
        "product":        "Product",
        "remaining":      "Remaining",
        "no_products":    "No products added yet.",
        "no_movements":   "No movement records yet.",
        "saved":          "Saved!",
        "deleted":        "Deleted!",
        "error_stock":    "Insufficient stock!",
        "error_fields":   "Please fill in all fields.",
        "confirm_delete": "Are you sure you want to delete?",
        "search":         "Search...",
        "welcome":        "Welcome",
        "language":       "Language",
        "change_password":"Change Password",
        "new_password":   "New Password",
        "current_password":"Current Password",
        "in_movement":    "Stock in",
        "out_movement":   "Stock out",
        "undo":           "Undo",
        "undo_confirm":   "Undo this movement? Stock will be reverted.",
        "critical_alert": "Products at critical stock level",
    }
}

def t(key):
    lang = session.get("lang", "tr")
    return STRINGS.get(lang, STRINGS["tr"]).get(key, key)

app.jinja_env.globals["t"] = t

# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        uname = request.form.get("username","").strip()
        pw    = hash_pw(request.form.get("password",""))
        conn  = get_db(); cur = conn.cursor()
        cur.execute("SELECT id,lang FROM users WHERE username=%s AND password=%s",
                    (uname, pw))
        user = cur.fetchone()
        cur.close(); conn.close()
        if user:
            session["user_id"]  = user["id"]
            session["username"] = uname
            session["lang"]     = user["lang"] or "tr"
            return redirect(url_for("dashboard"))
        flash("Hatalı kullanıcı adı veya şifre." if session.get("lang","tr")=="tr"
              else "Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/lang/<code>")
@login_required
def set_lang(code):
    if code in ("tr","en"):
        session["lang"] = code
        conn = get_db(); cur = conn.cursor()
        cur.execute("UPDATE users SET lang=%s WHERE id=%s",
                    (code, session["user_id"]))
        conn.commit(); cur.close(); conn.close()
    return redirect(request.referrer or url_for("dashboard"))

# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def dashboard():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM products")
    total = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM products WHERE stock<=0")
    out   = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM products WHERE stock>0 AND stock<=min_stock")
    crit  = cur.fetchone()["c"]
    cur.execute("""SELECT name,stock,unit FROM products
                   WHERE stock<=min_stock ORDER BY stock ASC LIMIT 10""")
    alerts = cur.fetchall()
    cur.execute("""SELECT m.created_at, p.name, m.type, m.quantity, m.stock_after, m.note
                   FROM movements m JOIN products p ON p.id=m.product_id
                   ORDER BY m.id DESC LIMIT 8""")
    recent = cur.fetchall()
    cur.close(); conn.close()
    return render_template("dashboard.html",
        total=total, out=out, crit=crit,
        alerts=alerts, recent=recent)

# ── Ürünler ───────────────────────────────────────────────────────────────────
@app.route("/products")
@login_required
def products():
    q    = request.args.get("q","")
    conn = get_db(); cur = conn.cursor()
    if q:
        cur.execute("""SELECT * FROM products
                       WHERE name ILIKE %s OR category ILIKE %s
                       ORDER BY name""", (f"%{q}%", f"%{q}%"))
    else:
        cur.execute("SELECT * FROM products ORDER BY name")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("products.html", products=rows, q=q)

@app.route("/products/add", methods=["GET","POST"])
@login_required
def product_add():
    if request.method == "POST":
        name  = request.form.get("name","").strip()
        if not name:
            flash(t("error_fields"))
            return redirect(url_for("product_add"))
        conn = get_db(); cur = conn.cursor()
        cur.execute("""INSERT INTO products (name,category,stock,min_stock,unit)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (name,
                     request.form.get("category",""),
                     int(request.form.get("stock",0)),
                     int(request.form.get("min_stock",5)),
                     request.form.get("unit","adet")))
        conn.commit(); cur.close(); conn.close()
        flash(t("saved"))
        return redirect(url_for("products"))
    return render_template("product_form.html", product=None)

@app.route("/products/<int:pid>/edit", methods=["GET","POST"])
@login_required
def product_edit(pid):
    conn = get_db(); cur = conn.cursor()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        if not name:
            flash(t("error_fields"))
            return redirect(url_for("product_edit", pid=pid))
        cur.execute("""UPDATE products SET name=%s,category=%s,min_stock=%s,unit=%s
                       WHERE id=%s""",
                    (name,
                     request.form.get("category",""),
                     int(request.form.get("min_stock",5)),
                     request.form.get("unit","adet"),
                     pid))
        conn.commit(); cur.close(); conn.close()
        flash(t("saved"))
        return redirect(url_for("products"))
    cur.execute("SELECT * FROM products WHERE id=%s", (pid,))
    product = cur.fetchone()
    cur.close(); conn.close()
    return render_template("product_form.html", product=product)

@app.route("/products/<int:pid>/delete", methods=["POST"])
@login_required
def product_delete(pid):
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM movements WHERE product_id=%s", (pid,))
    cur.execute("DELETE FROM products WHERE id=%s", (pid,))
    conn.commit(); cur.close(); conn.close()
    flash(t("deleted"))
    return redirect(url_for("products"))

# ── Hareketler ────────────────────────────────────────────────────────────────
@app.route("/movements", methods=["GET","POST"])
@login_required
def movements():
    conn = get_db(); cur = conn.cursor()
    if request.method == "POST":
        pid      = int(request.form.get("product_id",0))
        mov_type = request.form.get("type","in")
        qty      = int(request.form.get("quantity",0))
        note     = request.form.get("note","").strip()

        if pid == 0 or qty <= 0:
            flash(t("error_fields"))
            return redirect(url_for("movements"))

        cur.execute("SELECT stock FROM products WHERE id=%s", (pid,))
        row = cur.fetchone()
        if not row:
            return redirect(url_for("movements"))

        new_stock = row["stock"] + (qty if mov_type=="in" else -qty)
        if new_stock < 0:
            flash(t("error_stock"))
            cur.close(); conn.close()
            return redirect(url_for("movements"))

        cur.execute("UPDATE products SET stock=%s WHERE id=%s", (new_stock, pid))
        cur.execute("""INSERT INTO movements
                       (product_id,type,quantity,stock_after,note,created_by)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (pid, mov_type, qty, new_stock, note, session["user_id"]))
        conn.commit()
        flash(t("saved"))
        cur.close(); conn.close()
        return redirect(url_for("movements"))

    cur.execute("SELECT id,name,stock,unit FROM products ORDER BY name")
    products = cur.fetchall()
    cur.close(); conn.close()
    return render_template("movements.html", products=products)

# ── Geçmiş ────────────────────────────────────────────────────────────────────
@app.route("/history")
@login_required
def history():
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.created_at, p.name, m.type,
               m.quantity, m.stock_after, m.note, u.username
        FROM movements m
        JOIN products p ON p.id=m.product_id
        LEFT JOIN users u ON u.id=m.created_by
        ORDER BY m.id DESC LIMIT 500
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("history.html", movements=rows)

@app.route("/history/<int:mid>/undo", methods=["POST"])
@login_required
def undo_movement(mid):
    conn = get_db(); cur = conn.cursor()
    cur.execute("""SELECT product_id,type,quantity FROM movements WHERE id=%s""", (mid,))
    mov = cur.fetchone()
    if not mov:
        cur.close(); conn.close()
        return redirect(url_for("history"))

    cur.execute("SELECT stock FROM products WHERE id=%s", (mov["product_id"],))
    prod = cur.fetchone()
    revert = prod["stock"] + (-mov["quantity"] if mov["type"]=="in" else mov["quantity"])

    if revert < 0:
        flash(t("error_stock"))
        cur.close(); conn.close()
        return redirect(url_for("history"))

    cur.execute("UPDATE products SET stock=%s WHERE id=%s", (revert, mov["product_id"]))
    cur.execute("DELETE FROM movements WHERE id=%s", (mid,))
    conn.commit(); cur.close(); conn.close()
    flash(t("deleted"))
    return redirect(url_for("history"))

# ── Ayarlar ───────────────────────────────────────────────────────────────────
@app.route("/settings", methods=["GET","POST"])
@login_required
def settings():
    if request.method == "POST":
        cur_pw  = hash_pw(request.form.get("current_password",""))
        new_pw  = request.form.get("new_password","")
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE id=%s AND password=%s",
                    (session["user_id"], cur_pw))
        if cur.fetchone() and new_pw:
            cur.execute("UPDATE users SET password=%s WHERE id=%s",
                        (hash_pw(new_pw), session["user_id"]))
            conn.commit()
            flash(t("saved"))
        else:
            flash("Hatalı şifre." if session.get("lang")=="tr" else "Wrong password.")
        cur.close(); conn.close()
    return render_template("settings.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
