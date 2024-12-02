import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import EmployeeDB
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

class EmployeeAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة غياب الموظفين")
        self.root.geometry("800x600")
        
        # تكوين الخط العربي
        self.arabic_font = ('DejaVu Sans', 12)
        
        style = ttk.Style()
        style.configure('.', font=self.arabic_font)
        style.configure('Treeview', font=self.arabic_font)
        style.configure('Treeview.Heading', font=self.arabic_font)
        
        # ضبط اتجاه النص من اليمين إلى اليسار
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.db = EmployeeDB()
        
        # Create tabs
        self.tab_control = ttk.Notebook(root)
        
        # Employee Management Tab
        self.emp_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.emp_tab, text=self.reshape_text('إدارة الموظفين'))
        
        # Attendance Tab
        self.attendance_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.attendance_tab, text=self.reshape_text('تسجيل الغياب'))
        
        # Reports Tab
        self.reports_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.reports_tab, text=self.reshape_text('التقارير'))
        
        self.tab_control.pack(expand=1, fill="both")
        
        self.setup_employee_tab()
        self.setup_attendance_tab()
        self.setup_reports_tab()

    def reshape_text(self, text):
        return get_display(arabic_reshaper.reshape(text))

    def create_rtl_entry(self, parent, **kwargs):
        entry = ttk.Entry(parent, font=self.arabic_font, justify='right', **kwargs)
        entry.bind('<KeyRelease>', lambda e: self.handle_arabic_input(e, entry))
        return entry

    def handle_arabic_input(self, event, entry):
        text = entry.get()
        if text:
            reshaped_text = self.reshape_text(text)
            if reshaped_text != text:
                current_position = entry.index(tk.INSERT)
                entry.delete(0, tk.END)
                entry.insert(0, reshaped_text)
                entry.icursor(current_position)

    def setup_employee_tab(self):
        # Employee Form
        form_frame = ttk.LabelFrame(self.emp_tab, text=self.reshape_text("إضافة موظف جديد"), padding=20)
        form_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        name_label = ttk.Label(form_frame, text=self.reshape_text("الاسم:"), font=self.arabic_font, justify='right')
        name_label.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry = self.create_rtl_entry(form_frame)
        self.name_entry.grid(row=0, column=0, padx=5, pady=5)

        dept_label = ttk.Label(form_frame, text=self.reshape_text("القسم:"), font=self.arabic_font, justify='right')
        dept_label.grid(row=1, column=1, padx=5, pady=5)
        self.dept_entry = self.create_rtl_entry(form_frame)
        self.dept_entry.grid(row=1, column=0, padx=5, pady=5)

        phone_label = ttk.Label(form_frame, text=self.reshape_text("الهاتف:"), font=self.arabic_font, justify='right')
        phone_label.grid(row=2, column=1, padx=5, pady=5)
        self.phone_entry = self.create_rtl_entry(form_frame)
        self.phone_entry.grid(row=2, column=0, padx=5, pady=5)

        add_button = ttk.Button(form_frame, text=self.reshape_text("إضافة موظف"), command=self.add_employee)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Employee List
        list_frame = ttk.LabelFrame(self.emp_tab, text=self.reshape_text("قائمة الموظفين"), padding=20)
        list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(list_frame, columns=('ID', 'Name', 'Department', 'Phone'), show='headings')
        self.tree.heading('ID', text=self.reshape_text('الرقم'))
        self.tree.heading('Name', text=self.reshape_text('الاسم'))
        self.tree.heading('Department', text=self.reshape_text('القسم'))
        self.tree.heading('Phone', text=self.reshape_text('الهاتف'))
        self.tree.grid(row=0, column=0, pady=10)

        delete_button = ttk.Button(list_frame, text=self.reshape_text("حذف الموظف"), command=self.delete_employee)
        delete_button.grid(row=1, column=0, pady=5)
        
        self.refresh_employee_list()

    def setup_attendance_tab(self):
        frame = ttk.LabelFrame(self.attendance_tab, text=self.reshape_text("تسجيل الغياب"), padding=20)
        frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        emp_label = ttk.Label(frame, text=self.reshape_text("الموظف:"), font=self.arabic_font, justify='right')
        emp_label.grid(row=0, column=1, padx=5, pady=5)
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(frame, textvariable=self.employee_var, font=self.arabic_font, justify='right')
        self.employee_combo.grid(row=0, column=0, padx=5, pady=5)

        date_label = ttk.Label(frame, text=self.reshape_text("التاريخ:"), font=self.arabic_font, justify='right')
        date_label.grid(row=1, column=1, padx=5, pady=5)
        self.date_entry = DateEntry(frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, font=self.arabic_font)
        self.date_entry.grid(row=1, column=0, padx=5, pady=5)

        status_label = ttk.Label(frame, text=self.reshape_text("الحالة:"), font=self.arabic_font, justify='right')
        status_label.grid(row=2, column=1, padx=5, pady=5)
        self.status_var = tk.StringVar(value=self.reshape_text("غائب"))
        self.status_combo = ttk.Combobox(frame, textvariable=self.status_var, 
                                       values=[self.reshape_text("غائب"), self.reshape_text("حاضر"), self.reshape_text("إجازة")],
                                       font=self.arabic_font, justify='right')
        self.status_combo.grid(row=2, column=0, padx=5, pady=5)

        record_button = ttk.Button(frame, text=self.reshape_text("تسجيل"), command=self.mark_attendance)
        record_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.update_employee_combo()

    def setup_reports_tab(self):
        frame = ttk.LabelFrame(self.reports_tab, text=self.reshape_text("تقارير الغياب"), padding=20)
        frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        # Date range selection
        date_frame = ttk.Frame(frame)
        date_frame.grid(row=0, column=0, pady=10)

        from_label = ttk.Label(date_frame, text=self.reshape_text("من:"), font=self.arabic_font, justify='right')
        from_label.grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(date_frame, width=12, font=self.arabic_font)
        self.start_date.grid(row=0, column=1, padx=5)

        to_label = ttk.Label(date_frame, text=self.reshape_text("إلى:"), font=self.arabic_font, justify='right')
        to_label.grid(row=0, column=2, padx=5)
        self.end_date = DateEntry(date_frame, width=12, font=self.arabic_font)
        self.end_date.grid(row=0, column=3, padx=5)

        show_report_button = ttk.Button(date_frame, text=self.reshape_text("عرض التقرير"), command=self.show_report)
        show_report_button.grid(row=0, column=4, padx=10)

        self.report_tree = ttk.Treeview(frame, columns=('Name', 'Date', 'Status'), show='headings')
        self.report_tree.heading('Name', text=self.reshape_text('الاسم'))
        self.report_tree.heading('Date', text=self.reshape_text('التاريخ'))
        self.report_tree.heading('Status', text=self.reshape_text('الحالة'))
        self.report_tree.grid(row=1, column=0, pady=10)

    def add_employee(self):
        name = self.name_entry.get()
        dept = self.dept_entry.get()
        phone = self.phone_entry.get()
        
        if name and dept and phone:
            self.db.add_employee(name, dept, phone)
            self.refresh_employee_list()
            self.update_employee_combo()
            self.name_entry.delete(0, tk.END)
            self.dept_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            messagebox.showinfo(self.reshape_text("نجاح"), self.reshape_text("تمت إضافة الموظف بنجاح"))
        else:
            messagebox.showerror(self.reshape_text("خطأ"), self.reshape_text("الرجاء ملء جميع الحقول"))

    def delete_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror(self.reshape_text("خطأ"), self.reshape_text("الرجاء اختيار موظف"))
            return
        
        employee_id = self.tree.item(selected_item)['values'][0]
        self.db.delete_employee(employee_id)
        self.refresh_employee_list()
        self.update_employee_combo()
        messagebox.showinfo(self.reshape_text("نجاح"), self.reshape_text("تم حذف الموظف بنجاح"))

    def refresh_employee_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        employees = self.db.get_all_employees()
        for emp in employees:
            self.tree.insert('', 'end', values=emp)

    def update_employee_combo(self):
        employees = self.db.get_all_employees()
        self.employee_combo['values'] = [f"{emp[0]} - {emp[1]}" for emp in employees]

    def mark_attendance(self):
        if not self.employee_var.get():
            messagebox.showerror(self.reshape_text("خطأ"), self.reshape_text("الرجاء اختيار موظف"))
            return

        employee_id = int(self.employee_var.get().split('-')[0])
        date = self.date_entry.get_date().strftime('%Y-%m-%d')
        status = self.status_var.get()

        self.db.mark_attendance(employee_id, date, status)
        messagebox.showinfo(self.reshape_text("نجاح"), self.reshape_text("تم تسجيل الغياب بنجاح"))

    def show_report(self):
        start = self.start_date.get_date().strftime('%Y-%m-%d')
        end = self.end_date.get_date().strftime('%Y-%m-%d')

        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        records = self.db.get_attendance_report(start, end)
        for record in records:
            self.report_tree.insert('', 'end', values=record)

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#f0f0f0')
    style = ttk.Style()
    style.theme_use('clam')
    app = EmployeeAttendanceSystem(root)
    root.mainloop()
