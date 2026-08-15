from flask import Blueprint, request, render_template, abort, redirect, url_for
import pymysql
from db import get_db_connection

employee_bp = Blueprint('employee', __name__)

def validate_employee_data(data):
    name = data.get('name')
    fname = data.get('fname')
    gsm = data.get('gsm')
    adress = data.get('adr')
    emp_type = data.get('type')
    gender = data.get('gender')

    if not name or not fname or not gsm or not adress or not emp_type or not gender:
        abort(400, description="Missing required fields")
    if len(gsm) != 8 or not gsm.isdigit():
        abort(400, description="Invalid GSM number")
    if emp_type not in ['manager', 'driver', 'stocker', 'financer']:
        abort(400, description="Invalid employee type")
    if gender not in ['M', 'F']:
        abort(400, description="Invalid gender")

    return name, fname, gsm, adress, emp_type, gender

@employee_bp.route('/', methods=['GET'])
def show_form():
    return render_template('show.html')

@employee_bp.route('/add_employee', methods=['POST'])
def add_employee():
    name, fname, gsm, adress, emp_type, gender = validate_employee_data(request.form)

    conn = get_db_connection()
    cursor = conn.cursor()
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

@employee_bp.route('/employees', methods=['GET'])
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

@employee_bp.route('/delete_employee/<int:employee_id>', methods=['POST'])
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
    return redirect(url_for('employee.get_employees'))

@employee_bp.route('/edit_employee/<int:employee_id>', methods=['GET'])
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

@employee_bp.route('/edit_employee/<int:employee_id>', methods=['POST'])
def edit_employee(employee_id):
    name, fname, gsm, adress, emp_type, gender = validate_employee_data(request.form)

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

@employee_bp.route('/vehicules', methods = ['GET'])
def get_vehicules():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT immat, marque, last_maintenance FROM truck"
    try:
        cursor.execute(sql)
        trucks = cursor.fetchall()
    except Exception as e:
        print(e)
        abort(500, description = "Database error")
    finally:
        cursor.close()
        conn.close()
    return render_template('trucks.html', trucks = trucks)