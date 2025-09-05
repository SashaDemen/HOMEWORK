from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from db import init_db, seed_if_empty, get_conn
from weather import get_weather

app = Flask(__name__)
app.secret_key = "dev-key"
ADMIN_PASSWORD = "admin123"
class FeedbackForm(FlaskForm):
    name = StringField("Ім'я", validators=[Length(max=120)])
    message = TextAreaField("Повідомлення", validators=[DataRequired(message="Напишіть відгук"), Length(min=5, max=1000)])
    rating = SelectField("Оцінка", choices=[("5","5"),("4","4"),("3","3"),("2","2"),("1","1")], validators=[DataRequired()])


@app.before_first_request
def setup():
    init_db()
    seed_if_empty()

@app.route("/")
def index():
    city = request.args.get("city","Kyiv")
    date_str = request.args.get("date")
    if not date_str:
        import datetime
        date_str = datetime.date.today().isoformat()
    weather = get_weather(city, date_str)
    return render_template("index.html", title="Oderman Pizzeria", city=city, date_str=date_str, weather=weather)

# MENU
@app.route("/menu")
def menu():
    sort = request.args.get("sort","name")
    if sort == "price_asc":
        order = "price ASC, name ASC"
    elif sort == "price_desc":
        order = "price DESC, name ASC"
    else:
        order = "name ASC"
        sort = "name"
    conn = get_conn()
    items = conn.execute(f"SELECT id, name, description, price FROM menu_items ORDER BY {order}").fetchall()
    conn.close()
    return render_template("menu.html", title="Меню", items=items, sort=sort)

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

@app.route("/admin/menu/<int:item_id>/edit", methods=["GET","POST"])
def admin_edit_item(item_id):
    conn = get_conn()
    item = conn.execute("SELECT id, name, description, price FROM menu_items WHERE id=?", (item_id,)).fetchone()
    if not item:
        conn.close()
        return ("Not found", 404)
    if request.method == "POST":
        if request.form.get("admin_password") != ADMIN_PASSWORD:
            flash("Невірний пароль адміністратора")
            conn.close()
            return render_template("edit_form.html", title="Редагувати страву", item=item, form=request.form), 400
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip()
        price_raw = (request.form.get("price") or "").strip()
        try:
            price = float(price_raw)
        except ValueError:
            price = -1
        if not name or price <= 0:
            flash("Перевірте поля")
            conn.close()
            return render_template("edit_form.html", title="Редагувати страву", item=item, form=request.form), 400
        conn.execute("UPDATE menu_items SET name=?, description=?, price=? WHERE id=?", (name, description, price, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for("menu"))
    conn.close()
    return render_template("edit_form.html", title="Редагувати страву", item=item, form={})

@app.route("/admin/menu/<int:item_id>/delete", methods=["POST"])
def admin_delete_item(item_id):
    if request.form.get("admin_password") != ADMIN_PASSWORD:
        flash("Невірний пароль адміністратора")
        return redirect(url_for("menu"))
    conn = get_conn()
    conn.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("menu"))

# LESSONS
@app.route("/lessons")
def lessons_list():
    conn = get_conn()
    items = conn.execute("SELECT id, title, lesson_date, note FROM lessons ORDER BY lesson_date").fetchall()
    conn.close()
    return render_template("lessons.html", title="Уроки", lessons=items)

@app.route("/admin/lessons/new", methods=["GET","POST"])
def lessons_new():
    if request.method == "POST":
        if request.form.get("admin_password") != ADMIN_PASSWORD:
            flash("Невірний пароль адміністратора")
            return render_template("lesson_form.html", title="Додати урок", form=request.form), 400
        title = (request.form.get("title") or "").strip()
        lesson_date = (request.form.get("lesson_date") or "").strip()
        note = (request.form.get("note") or "").strip()
        if not title or not lesson_date:
            flash("Назва та дата обов'язкові")
            return render_template("lesson_form.html", title="Додати урок", form=request.form), 400
        conn = get_conn()
        conn.execute("INSERT INTO lessons(title, lesson_date, note) VALUES(?,?,?)", (title, lesson_date, note))
        conn.commit()
        conn.close()
        return redirect(url_for("lessons_list"))
    return render_template("lesson_form.html", title="Додати урок", form={})

# SURVEY
@app.route("/survey", methods=["GET","POST"])
def survey():
    conn = get_conn()
    items = conn.execute("SELECT id, name FROM menu_items ORDER BY name").fetchall()
    if request.method == "POST":
        choice = request.form.get("menu_item_id")
        if not choice:
            flash("Оберіть страву")
            conn.close()
            return render_template("survey.html", title="Опитування", items=items), 400
        conn.execute("INSERT INTO votes(menu_item_id) VALUES(?)", (int(choice),))
        conn.commit()
        conn.close()
        return redirect(url_for("survey_results"))
    conn.close()
    return render_template("survey.html", title="Опитування", items=items)

@app.route("/survey/results")
def survey_results():
    conn = get_conn()
    rows = conn.execute(
        """SELECT m.name, COUNT(v.id) as votes
               FROM menu_items m
               LEFT JOIN votes v ON v.menu_item_id = m.id
               GROUP BY m.id
               ORDER BY votes DESC, m.name ASC"""
    ).fetchall()
    conn.close()
    return render_template("survey_results.html", title="Результати опитування", results=rows)

@app.route("/feedback", methods=["GET","POST"])
def feedback_form():
    form = FeedbackForm()
    if form.validate_on_submit():
        name = (form.name.data or "").strip()
        message = form.message.data.strip()
        try:
            rating = int(form.rating.data)
        except Exception:
            rating = 3
        conn = get_conn()
        conn.execute("INSERT INTO feedbacks(name, message, rating) VALUES(?,?,?)", (name, message, rating))
        conn.commit()
        conn.close()
        flash("Дякуємо за відгук!")
        return redirect(url_for("feedbacks_list"))
    return render_template("feedback_form.html", title="Залишити відгук", form=form)

@app.route("/feedbacks")
def feedbacks_list():
    conn = get_conn()
    rows = conn.execute("SELECT id, name, message, rating, created_at FROM feedbacks ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("feedback_list.html", title="Відгуки", items=rows)

if __name__ == "__main__":
    app.run(debug=True)
