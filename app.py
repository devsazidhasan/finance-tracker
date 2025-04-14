from flask import Flask, render_template, request, redirect, url_for, jsonify # type: ignore
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            category TEXT,
            amount REAL,
            note TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Home Page
@app.route('/')
def home():
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions ORDER BY date DESC")
    transactions = c.fetchall()
 
    c.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
    income = c.fetchone()[0] or 0

    c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
    expense = c.fetchone()[0] or 0

    conn.close()
    balance = income - expense
    return render_template('home.html', transactions=transactions, income=income, expense=expense, balance=balance)
#    return jsonify({
#        'transactions':transactions,
#        'income':income,
#        'balance':balance
#    })

# Add Transaction
@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        t_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        note = request.form['note']

        conn = sqlite3.connect('transactions.db')
        c = conn.cursor()
        c.execute("INSERT INTO transactions (type, category, amount, note) VALUES (?, ?, ?, ?)",
                  (t_type, category, amount, note))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('add_transaction.html')

# Edit Transaction
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    if request.method == 'POST':
        t_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        note = request.form['note']
        c.execute("UPDATE transactions SET type=?, category=?, amount=?, note=? WHERE id=?",
                  (t_type, category, amount, note, id))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    else:
        c.execute("SELECT * FROM transactions WHERE id=?", (id,))
        transaction = c.fetchone()
        conn.close()
        return render_template('edit_transaction.html', transaction=transaction)

# Delete Transaction
@app.route('/delete/<int:id>')
def delete_transaction(id):
    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
