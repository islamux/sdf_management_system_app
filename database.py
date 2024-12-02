import sqlite3
from datetime import datetime

class EmployeeDB:
    def __init__(self):
        self.conn = sqlite3.connect('employees.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create employees table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            phone TEXT
        )
        ''')

        # Create attendance table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')
        
        self.conn.commit()

    def add_employee(self, name, department, phone):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO employees (name, department, phone) VALUES (?, ?, ?)',
                      (name, department, phone))
        self.conn.commit()

    def get_all_employees(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM employees')
        return cursor.fetchall()

    def delete_employee(self, employee_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        self.conn.commit()

    def mark_attendance(self, employee_id, date, status):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO attendance (employee_id, date, status) VALUES (?, ?, ?)',
                      (employee_id, date, status))
        self.conn.commit()

    def get_attendance_report(self, start_date=None, end_date=None):
        cursor = self.conn.cursor()
        if start_date and end_date:
            cursor.execute('''
                SELECT e.name, a.date, a.status 
                FROM employees e 
                JOIN attendance a ON e.id = a.employee_id
                WHERE a.date BETWEEN ? AND ?
                ORDER BY a.date DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT e.name, a.date, a.status 
                FROM employees e 
                JOIN attendance a ON e.id = a.employee_id
                ORDER BY a.date DESC
            ''')
        return cursor.fetchall()

    def __del__(self):
        self.conn.close()
