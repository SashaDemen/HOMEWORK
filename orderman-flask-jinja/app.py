from flask import Flask, render_template, request, redirect, url_for, flash
from db import init_db, seed_if_empty, get_conn

app = Flask(__name__)
app.secret_key = "dev-key"
ADMIN_PASSWORD = "admin123"

@app.before_first_request
def setup():
    init_db()
    seed_if_empty()

@app.route("/")
def index():
    return render_template("index.html", title="Oderman Pizzeria")

@app.route("/menu")
def menu():
    conn = get_conn()
    items = conn.execute("SELECT id, name, description, price FROM menu_items ORDER BY name").fetchall()
    conn.close()
    return render_template("menu.html", title="Меню", items=items)

@app.route("/admin/menu/new", methods=["GET","POST"])
def admin_new_item():
    if request.method == "POST":
        if request.form.get("admin_password") != ADMIN_PASSWORD:
            flash("Невірний пароль адміністратора")
            return render_template("admin_form.html", title="Додати страву", form=request.form), 400
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip()
        price_raw = (request.form.get("price") or "").strip()
        try:
            price = float(price_raw)
        except ValueError:
            price = -1
        if not name:
            flash("Назва обов'язкова")
            return render_template("admin_form.html", title="Додати страву", form=request.form), 400
        if price <= 0:
            flash("Ціна має бути > 0")
            return render_template("admin_form.html", title="Додати страву", form=request.form), 400
        conn = get_conn()
        conn.execute("INSERT INTO menu_items(name, description, price) VALUES(?,?,?)", (name, description, price))
        conn.commit()
        conn.close()
        return redirect(url_for("menu"))
    return render_template("admin_form.html", title="Додати страву", form={})

if __name__ == "__main__":
    app.run(debug=True)
