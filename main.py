import os

from dotenv import load_dotenv
from flask import Flask, url_for, request, render_template, abort, redirect
from markupsafe import escape
import pymysql

load_dotenv()

app = Flask(__name__)  #__name__ references this file, and no Farouk this is written by me not AI

#@app.route('/user/<username>')
#def profile(username):
#    return f'{escape(username)}\'s profile'   #added escape() to stop javascript attacks because it changes the script thing to normal text

def get_db_connection():
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        port=int(os.environ['DB_PORT']))

@app.route('/', methods = ['GET'])
def show_form():
    return render_template('show.html')

@app.route('/add_employee', methods = ['POST'])
def add_employee():
    name = request.form.get('name')
    fname = request.form.get('fname')
    gsm = request.form.get('gsm')
    adress = request.form.get('adr')
    emp_type = request.form.get('type')
    gender = request.form.get('gender')
    if not name or not fname or not gsm or not adress or not emp_type or not gender:
        abort(400, description="Missing required fields")
    if len(gsm) != 8 or not gsm.isdigit():
        abort(400, description="Invalid GSM number")
    if emp_type not in ['manager', 'driver', 'stocker', 'financer']:
        abort(400, description="Invalid employee type")
    if gender not in ['M', 'F']:
        abort(400, description="Invalid gender")

    conn = get_db_connection()
    cursor = conn.cursor() #cursors are basically a pointer to the database they allow you to execute queries i think ?
    sql = "INSERT INTO personnel (name, fname, gsm, adr, type, gender) VALUES (%s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(sql, (name, fname, gsm, adress, emp_type, gender))
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
        abort(500, description="Database error")
    finally:
        cursor.close()
        conn.close()
    return render_template('success.html')
@app.route('/employees', methods=['GET'])
def get_employees():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT id, name, fname, gsm, adr, type, gender FROM personnel"
    try:
        cursor.execute(sql)
        employees = cursor.fetchall()
    except Exception as e:
        print(e)
        abort(500, description="Database error")
    finally:
        cursor.close()
        conn.close()
    return render_template('employees.html', employees=employees)
@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM personnel WHERE id = %s"
    try:
        cursor.execute(sql, (employee_id,))
        conn.commit()
        if cursor.rowcount == 0:
            abort(404, description="Employee not found")
    except Exception as e:
        print(e)
        conn.rollback()
        abort(500, description="Database error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('get_employees'))
@app.route('/edit_employee/<int:employee_id>', methods=['GET'])
def edit_employee_form(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT id, name, fname, gsm, adr, type, gender FROM personnel WHERE id = %s"
    try:
        cursor.execute(sql, (employee_id,))
        emp = cursor.fetchone()
    except Exception as e:
        print(e)
        abort(500, description="Database error")
    finally:
        cursor.close()
        conn.close()
    if emp is None:
        abort(404, description="Employee not found")
    return render_template('edit.html', emp=emp)
@app.route('/edit_employee/<int:employee_id>', methods=['POST'])
def edit_employee(employee_id):
    name = request.form.get('name')
    fname = request.form.get('fname')
    gsm = request.form.get('gsm')
    adress = request.form.get('adr')
    emp_type = request.form.get('type')
    gender = request.form.get('gender')
    if not name or not fname or not gsm or not adress or not emp_type or not gender:
        abort(400, description="Missing required fields")
    if len(gsm) != 8 or not gsm.isdigit():
        abort(400, description="Invalid GSM number")
    if emp_type not in ['manager', 'driver', 'stocker', 'financer']:
        abort(400, description="Invalid employee type")
    if gender not in ['M', 'F']:
        abort(400, description="Invalid gender")

    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE personnel SET name=%s, fname=%s, gsm=%s, adr=%s, type=%s, gender=%s WHERE id=%s"
    try:
        cursor.execute(sql, (name, fname, gsm, adress, emp_type, gender, employee_id))
        conn.commit()
        if cursor.rowcount == 0:
            abort(404, description="Employee not found")
    except Exception as e:
        print(e)
        conn.rollback()
        abort(500, description="Database error")
    finally:
        cursor.close()
        conn.close()
    return render_template('success.html')

    
if __name__ == '__main__':
    app.run(debug=True)