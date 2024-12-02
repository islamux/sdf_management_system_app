import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import EmployeeDB
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

class ArabicTextHandler:
    @staticmethod
    def process(text):
        if not text:
            return ""
        try:
            return get_display(arabic_reshaper.reshape(text))
        except:
            return text

class RightToLeftEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._original_text = ""
        self.bind('<KeyRelease>', self._on_key_release)

    def _on_key_release(self, event):
        current = self.get()
        if current != self._original_text:
            self._original_text = current
            reshaped = arabic_reshaper.reshape(current)
            bidi_text = get_display(reshaped)
            cursor_pos = self.index(tk.INSERT)
            self.delete(0, tk.END)
            self.insert(0, bidi_text)
            self.icursor(cursor_pos)

    def get_original(self):
        return self._original_text

class EmployeeAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة غياب الموظفين")
        self.root.geometry("800x600")
        
        # تكوين الخط العربي
        self.arabic_font = ('DejaVu Sans', 12)
        
        style = ttk.Style()
        style.configure('TEntry', font=self.arabic_font)
        style.configure('Treeview', font=self.arabic_font)
        style.configure('Treeview.Heading', font=self.arabic_font)
        
        # Initialize database
        self.db = EmployeeDB()
        
        # Create tabs
        self.tab_control = ttk.Notebook(root)
        
        # Employee Management Tab
        self.emp_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.emp_tab, text=ArabicTextHandler.process('إدارة الموظفين'))
        
        # Attendance Tab
        self.attendance_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.attendance_tab, text=ArabicTextHandler.process('تسجيل الغياب'))
        
        # Reports Tab
        self.reports_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.reports_tab, text=ArabicTextHandler.process('التقارير'))
        
        self.tab_control.pack(expand=1, fill="both")
        
        self.setup_employee_tab()
        self.setup_attendance_tab()
        self.setup_reports_tab()

    def create_rtl_entry(self, parent, **kwargs):
        return RightToLeftEntry(parent, font=self.arabic_font, justify='right', **kwargs)

    def setup_employee_tab(self):
        # Employee Form
        form_frame = ttk.LabelFrame(self.emp_tab, text=ArabicTextHandler.process("إضافة موظف جديد"), padding=20)
        form_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        # Name field
        name_label = ttk.Label(form_frame, text=ArabicTextHandler.process("الاسم:"), font=self.arabic_font)
        name_label.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry = self.create_rtl_entry(form_frame)
        self.name_entry.grid(row=0, column=0, padx=5, pady=5)

        # Department field
        dept_label = ttk.Label(form_frame, text=ArabicTextHandler.process("القسم:"), font=self.arabic_font)
        dept_label.grid(row=1, column=1, padx=5, pady=5)
        self.dept_entry = self.create_rtl_entry(form_frame)
        self.dept_entry.grid(row=1, column=0, padx=5, pady=5)

        # Phone field
        phone_label = ttk.Label(form_frame, text=ArabicTextHandler.process("الهاتف:"), font=self.arabic_font)
        phone_label.grid(row=2, column=1, padx=5, pady=5)
        self.phone_entry = self.create_rtl_entry(form_frame)
        self.phone_entry.grid(row=2, column=0, padx=5, pady=5)

        # Add button
        add_button = ttk.Button(form_frame, text=ArabicTextHandler.process("إضافة موظف"), command=self.add_employee)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Employee List
        list_frame = ttk.LabelFrame(self.emp_tab, text=ArabicTextHandler.process("قائمة الموظفين"), padding=20)
        list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(list_frame, columns=('ID', 'Name', 'Department', 'Phone'), show='headings')
        self.tree.heading('ID', text=ArabicTextHandler.process('الرقم'))
        self.tree.heading('Name', text=ArabicTextHandler.process('الاسم'))
        self.tree.heading('Department', text=ArabicTextHandler.process('القسم'))
        self.tree.heading('Phone', text=ArabicTextHandler.process('الهاتف'))
        self.tree.grid(row=0, column=0, pady=10)

        delete_button = ttk.Button(list_frame, text=ArabicTextHandler.process("حذف الموظف"), command=self.delete_employee)
        delete_button.grid(row=1, column=0, pady=5)
        
        self.refresh_employee_list()

    def add_employee(self):
        name = self.name_entry.get_original()
        dept = self.dept_entry.get_original()
        phone = self.phone_entry.get_original()
        
        if name and dept and phone:
            try:
                self.db.add_employee(name, dept, phone)
                self.refresh_employee_list()
                self.update_employee_combo()
                
                self.name_entry.delete(0, tk.END)
                self.dept_entry.delete(0, tk.END)
                self.phone_entry.delete(0, tk.END)
                
                messagebox.showinfo(
                    ArabicTextHandler.process("نجاح"), 
                    ArabicTextHandler.process("تمت إضافة الموظف بنجاح")
                )
            except Exception as e:
                messagebox.showerror(
                    ArabicTextHandler.process("خطأ"), 
                    ArabicTextHandler.process("حدث خطأ في إضافة الموظف")
                )
                print(f"Error in add_employee: {e}")
        else:
            messagebox.showerror(
                ArabicTextHandler.process("خطأ"), 
                ArabicTextHandler.process("الرجاء ملء جميع الحقول")
            )

    def delete_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror(ArabicTextHandler.process("خطأ"), ArabicTextHandler.process("الرجاء اختيار موظف"))
            return
        
        employee_id = self.tree.item(selected_item)['values'][0]
        self.db.delete_employee(employee_id)
        self.refresh_employee_list()
        self.update_employee_combo()
        messagebox.showinfo(ArabicTextHandler.process("نجاح"), ArabicTextHandler.process("تم حذف الموظف بنجاح"))

    def refresh_employee_list(self):
        """تحديث قائمة الموظفين"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            employees = self.db.get_all_employees()
            for emp in employees:
                # عرض البيانات في الجدول بدون معالجة إضافية
                self.tree.insert('', 'end', values=[
                    emp[0],  # ID
                    emp[1],  # Name
                    emp[2],  # Department
                    emp[3]   # Phone
                ])
        except Exception as e:
            print(f"Error in refresh_employee_list: {e}")

    def update_employee_combo(self):
        """تحديث قائمة اختيار الموظفين"""
        try:
            employees = self.db.get_all_employees()
            employee_list = [f"{emp[0]} - {emp[1]}" for emp in employees]
            self.employee_combo['values'] = employee_list
            if employee_list:
                self.employee_combo.current(0)
        except Exception as e:
            print(f"Error in update_employee_combo: {e}")

    def setup_attendance_tab(self):
        frame = ttk.LabelFrame(self.attendance_tab, text=ArabicTextHandler.process("تسجيل الغياب"), padding=20)
        frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        emp_label = ttk.Label(frame, text=ArabicTextHandler.process("الموظف:"), font=self.arabic_font)
        emp_label.grid(row=0, column=1, padx=5, pady=5)
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(frame, textvariable=self.employee_var, font=self.arabic_font)
        self.employee_combo.grid(row=0, column=0, padx=5, pady=5)

        date_label = ttk.Label(frame, text=ArabicTextHandler.process("التاريخ:"), font=self.arabic_font)
        date_label.grid(row=1, column=1, padx=5, pady=5)
        self.date_entry = DateEntry(frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, font=self.arabic_font)
        self.date_entry.grid(row=1, column=0, padx=5, pady=5)

        status_label = ttk.Label(frame, text=ArabicTextHandler.process("الحالة:"), font=self.arabic_font)
        status_label.grid(row=2, column=1, padx=5, pady=5)
        self.status_var = tk.StringVar(value=ArabicTextHandler.process("غائب"))
        self.status_combo = ttk.Combobox(frame, textvariable=self.status_var, 
                                       values=[ArabicTextHandler.process("غائب"), ArabicTextHandler.process("حاضر"), ArabicTextHandler.process("إجازة")],
                                       font=self.arabic_font)
        self.status_combo.grid(row=2, column=0, padx=5, pady=5)

        record_button = ttk.Button(frame, text=ArabicTextHandler.process("تسجيل"), command=self.mark_attendance)
        record_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.update_employee_combo()

    def mark_attendance(self):
        if not self.employee_var.get():
            messagebox.showerror(ArabicTextHandler.process("خطأ"), ArabicTextHandler.process("الرجاء اختيار موظف"))
            return

        try:
            employee_id = int(self.employee_var.get().split('-')[0].strip())
            date = self.date_entry.get_date().strftime('%Y-%m-%d')
            status = self.status_var.get()
            
            # إزالة معالجة النص العربي قبل الحفظ في قاعدة البيانات
            original_status = status
            if status.startswith('\u202e'): # إذا كان النص يبدأ بعلامة RTL
                original_status = status[1:]  # إزالة علامة RTL
            
            self.db.mark_attendance(employee_id, date, original_status)
            messagebox.showinfo(ArabicTextHandler.process("نجاح"), ArabicTextHandler.process("تم تسجيل الغياب بنجاح"))
        except Exception as e:
            messagebox.showerror(ArabicTextHandler.process("خطأ"), ArabicTextHandler.process("حدث خطأ في تسجيل الغياب"))

    def setup_reports_tab(self):
        frame = ttk.LabelFrame(self.reports_tab, text=ArabicTextHandler.process("تقارير الغياب"), padding=20)
        frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        # Date range selection
        date_frame = ttk.Frame(frame)
        date_frame.grid(row=0, column=0, pady=10)

        from_label = ttk.Label(date_frame, text=ArabicTextHandler.process("من:"), font=self.arabic_font)
        from_label.grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(date_frame, width=12, font=self.arabic_font)
        self.start_date.grid(row=0, column=1, padx=5)

        to_label = ttk.Label(date_frame, text=ArabicTextHandler.process("إلى:"), font=self.arabic_font)
        to_label.grid(row=0, column=2, padx=5)
        self.end_date = DateEntry(date_frame, width=12, font=self.arabic_font)
        self.end_date.grid(row=0, column=3, padx=5)

        show_report_button = ttk.Button(date_frame, text=ArabicTextHandler.process("عرض التقرير"), command=self.show_report)
        show_report_button.grid(row=0, column=4, padx=10)

        self.report_tree = ttk.Treeview(frame, columns=('Name', 'Date', 'Status'), show='headings')
        self.report_tree.heading('Name', text=ArabicTextHandler.process('الاسم'))
        self.report_tree.heading('Date', text=ArabicTextHandler.process('التاريخ'))
        self.report_tree.heading('Status', text=ArabicTextHandler.process('الحالة'))
        self.report_tree.grid(row=1, column=0, pady=10)

    def show_report(self):
        start = self.start_date.get_date().strftime('%Y-%m-%d')
        end = self.end_date.get_date().strftime('%Y-%m-%d')
        
        # Clear previous entries
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
            
        try:
            records = self.db.get_attendance_report(start, end)
            for record in records:
                emp_id, name, date, status = record
                # معالجة النص العربي للعرض
                displayed_name = name
                displayed_status = status
                self.report_tree.insert('', 'end', values=(displayed_name, date, displayed_status))
        except Exception as e:
            messagebox.showerror(ArabicTextHandler.process("خطأ"), ArabicTextHandler.process("حدث خطأ في عرض التقرير"))
            print(f"Error in show_report: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#f0f0f0')
    app = EmployeeAttendanceSystem(root)
    root.mainloop()
