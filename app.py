from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "12345"

def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''create table if not exists expenses(id integer primary key autoincrement, name text, category text, amount real)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("select * from expenses")
    expenses = cursor.fetchall()
    conn.close()
    total = sum(i[3] for i in expenses)
    return render_template('index.html', expenses=expenses, total=total)

@app.route("/add", methods=['POST'])
def addExpenses():
    name = request.form['name'].strip()
    category = request.form['category'].strip()
    amount = request.form['amount'].strip()

    if not name or not category or not amount:
        flash("All fields are required", 'error')
        return redirect(url_for('index'))

    try:
        amount = float(amount)
    except ValueError:
        flash("Invalid amount", 'error')
        return redirect(url_for('index'))

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("insert into expenses (name, category, amount) values (?, ?, ?)", (name, category, amount))
    conn.commit()
    conn.close()
    flash("Expense added successfully", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
