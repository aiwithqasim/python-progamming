import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


DB_NAME = "class_management.db"


class Database:
    def __init__(self, db_name: str = DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                grade_level TEXT NOT NULL
            );
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                instructor TEXT NOT NULL,
                schedule TEXT NOT NULL
            );
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                UNIQUE(student_id, course_id),
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def add_student(self, name: str, email: str, grade_level: str) -> None:
        self.conn.execute(
            "INSERT INTO students(name, email, grade_level) VALUES(?, ?, ?);",
            (name, email, grade_level),
        )
        self.conn.commit()

    def get_students(self):
        cursor = self.conn.execute(
            "SELECT id, name, email, grade_level FROM students ORDER BY id DESC;"
        )
        return cursor.fetchall()

    def delete_student(self, student_id: int) -> None:
        self.conn.execute("DELETE FROM students WHERE id = ?;", (student_id,))
        self.conn.commit()

    def add_course(self, title: str, instructor: str, schedule: str) -> None:
        self.conn.execute(
            "INSERT INTO courses(title, instructor, schedule) VALUES(?, ?, ?);",
            (title, instructor, schedule),
        )
        self.conn.commit()

    def get_courses(self):
        cursor = self.conn.execute(
            "SELECT id, title, instructor, schedule FROM courses ORDER BY id DESC;"
        )
        return cursor.fetchall()

    def delete_course(self, course_id: int) -> None:
        self.conn.execute("DELETE FROM courses WHERE id = ?;", (course_id,))
        self.conn.commit()

    def add_enrollment(self, student_id: int, course_id: int) -> None:
        self.conn.execute(
            "INSERT INTO enrollments(student_id, course_id) VALUES(?, ?);",
            (student_id, course_id),
        )
        self.conn.commit()

    def get_enrollments(self):
        cursor = self.conn.execute(
            """
            SELECT e.id, s.name, c.title
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
            ORDER BY e.id DESC;
            """
        )
        return cursor.fetchall()

    def delete_enrollment(self, enrollment_id: int) -> None:
        self.conn.execute("DELETE FROM enrollments WHERE id = ?;", (enrollment_id,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


class ClassManagementUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Class Management System")
        self.root.geometry("950x600")
        self.db = Database()

        self.student_map = {}
        self.course_map = {}

        self.build_ui()
        self.refresh_all()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.students_tab = ttk.Frame(notebook)
        self.courses_tab = ttk.Frame(notebook)
        self.enrollments_tab = ttk.Frame(notebook)

        notebook.add(self.students_tab, text="Students")
        notebook.add(self.courses_tab, text="Courses")
        notebook.add(self.enrollments_tab, text="Enrollments")

        self.build_students_tab()
        self.build_courses_tab()
        self.build_enrollments_tab()

    def build_students_tab(self) -> None:
        form = ttk.LabelFrame(self.students_tab, text="Add Student")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Name").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        ttk.Label(form, text="Email").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        ttk.Label(form, text="Grade").grid(row=0, column=4, padx=8, pady=8, sticky="w")

        self.student_name_var = tk.StringVar()
        self.student_email_var = tk.StringVar()
        self.student_grade_var = tk.StringVar()

        ttk.Entry(form, textvariable=self.student_name_var, width=25).grid(
            row=0, column=1, padx=8, pady=8
        )
        ttk.Entry(form, textvariable=self.student_email_var, width=25).grid(
            row=0, column=3, padx=8, pady=8
        )
        ttk.Entry(form, textvariable=self.student_grade_var, width=14).grid(
            row=0, column=5, padx=8, pady=8
        )
        ttk.Button(form, text="Add Student", command=self.add_student).grid(
            row=0, column=6, padx=8, pady=8
        )

        table_frame = ttk.Frame(self.students_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.students_tree = ttk.Treeview(
            table_frame,
            columns=("id", "name", "email", "grade"),
            show="headings",
            selectmode="browse",
        )
        for col, title, width in (
            ("id", "ID", 70),
            ("name", "Name", 230),
            ("email", "Email", 280),
            ("grade", "Grade Level", 140),
        ):
            self.students_tree.heading(col, text=title)
            self.students_tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.students_tree.yview
        )
        self.students_tree.configure(yscroll=scrollbar.set)
        self.students_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(
            self.students_tab, text="Delete Selected Student", command=self.delete_student
        ).pack(anchor="e", padx=10, pady=(0, 10))

    def build_courses_tab(self) -> None:
        form = ttk.LabelFrame(self.courses_tab, text="Add Course")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Course Title").grid(
            row=0, column=0, padx=8, pady=8, sticky="w"
        )
        ttk.Label(form, text="Instructor").grid(
            row=0, column=2, padx=8, pady=8, sticky="w"
        )
        ttk.Label(form, text="Schedule").grid(
            row=0, column=4, padx=8, pady=8, sticky="w"
        )

        self.course_title_var = tk.StringVar()
        self.course_instructor_var = tk.StringVar()
        self.course_schedule_var = tk.StringVar()

        ttk.Entry(form, textvariable=self.course_title_var, width=25).grid(
            row=0, column=1, padx=8, pady=8
        )
        ttk.Entry(form, textvariable=self.course_instructor_var, width=20).grid(
            row=0, column=3, padx=8, pady=8
        )
        ttk.Entry(form, textvariable=self.course_schedule_var, width=20).grid(
            row=0, column=5, padx=8, pady=8
        )
        ttk.Button(form, text="Add Course", command=self.add_course).grid(
            row=0, column=6, padx=8, pady=8
        )

        table_frame = ttk.Frame(self.courses_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.courses_tree = ttk.Treeview(
            table_frame,
            columns=("id", "title", "instructor", "schedule"),
            show="headings",
            selectmode="browse",
        )
        for col, title, width in (
            ("id", "ID", 70),
            ("title", "Course Title", 280),
            ("instructor", "Instructor", 220),
            ("schedule", "Schedule", 210),
        ):
            self.courses_tree.heading(col, text=title)
            self.courses_tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.courses_tree.yview
        )
        self.courses_tree.configure(yscroll=scrollbar.set)
        self.courses_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(
            self.courses_tab, text="Delete Selected Course", command=self.delete_course
        ).pack(anchor="e", padx=10, pady=(0, 10))

    def build_enrollments_tab(self) -> None:
        form = ttk.LabelFrame(self.enrollments_tab, text="Enroll Student in Course")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Student").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        ttk.Label(form, text="Course").grid(row=0, column=2, padx=8, pady=8, sticky="w")

        self.student_choice = ttk.Combobox(form, state="readonly", width=34)
        self.course_choice = ttk.Combobox(form, state="readonly", width=34)
        self.student_choice.grid(row=0, column=1, padx=8, pady=8)
        self.course_choice.grid(row=0, column=3, padx=8, pady=8)

        ttk.Button(form, text="Enroll", command=self.add_enrollment).grid(
            row=0, column=4, padx=8, pady=8
        )

        table_frame = ttk.Frame(self.enrollments_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.enrollments_tree = ttk.Treeview(
            table_frame,
            columns=("id", "student", "course"),
            show="headings",
            selectmode="browse",
        )
        for col, title, width in (
            ("id", "ID", 70),
            ("student", "Student Name", 340),
            ("course", "Course Title", 340),
        ):
            self.enrollments_tree.heading(col, text=title)
            self.enrollments_tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.enrollments_tree.yview
        )
        self.enrollments_tree.configure(yscroll=scrollbar.set)
        self.enrollments_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(
            self.enrollments_tab,
            text="Delete Selected Enrollment",
            command=self.delete_enrollment,
        ).pack(anchor="e", padx=10, pady=(0, 10))

    def refresh_students(self) -> None:
        for row in self.students_tree.get_children():
            self.students_tree.delete(row)
        students = self.db.get_students()
        for student in students:
            self.students_tree.insert("", "end", values=student)

        self.student_map = {f"{s[1]} ({s[3]})": s[0] for s in students}
        self.student_choice["values"] = list(self.student_map.keys())
        if self.student_map:
            self.student_choice.current(0)
        else:
            self.student_choice.set("")

    def refresh_courses(self) -> None:
        for row in self.courses_tree.get_children():
            self.courses_tree.delete(row)
        courses = self.db.get_courses()
        for course in courses:
            self.courses_tree.insert("", "end", values=course)

        self.course_map = {f"{c[1]} - {c[2]}": c[0] for c in courses}
        self.course_choice["values"] = list(self.course_map.keys())
        if self.course_map:
            self.course_choice.current(0)
        else:
            self.course_choice.set("")

    def refresh_enrollments(self) -> None:
        for row in self.enrollments_tree.get_children():
            self.enrollments_tree.delete(row)
        for enrollment in self.db.get_enrollments():
            self.enrollments_tree.insert("", "end", values=enrollment)

    def refresh_all(self) -> None:
        self.refresh_students()
        self.refresh_courses()
        self.refresh_enrollments()

    def add_student(self) -> None:
        name = self.student_name_var.get().strip()
        email = self.student_email_var.get().strip()
        grade = self.student_grade_var.get().strip()
        if not name or not email or not grade:
            messagebox.showerror("Input Error", "Please fill all student fields.")
            return
        try:
            self.db.add_student(name, email, grade)
            self.student_name_var.set("")
            self.student_email_var.set("")
            self.student_grade_var.set("")
            self.refresh_students()
            messagebox.showinfo("Success", "Student added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Email", "This email is already registered.")

    def delete_student(self) -> None:
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Select a student to delete.")
            return
        student_id = int(self.students_tree.item(selected[0], "values")[0])
        self.db.delete_student(student_id)
        self.refresh_all()

    def add_course(self) -> None:
        title = self.course_title_var.get().strip()
        instructor = self.course_instructor_var.get().strip()
        schedule = self.course_schedule_var.get().strip()
        if not title or not instructor or not schedule:
            messagebox.showerror("Input Error", "Please fill all course fields.")
            return
        self.db.add_course(title, instructor, schedule)
        self.course_title_var.set("")
        self.course_instructor_var.set("")
        self.course_schedule_var.set("")
        self.refresh_courses()
        messagebox.showinfo("Success", "Course added successfully.")

    def delete_course(self) -> None:
        selected = self.courses_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Select a course to delete.")
            return
        course_id = int(self.courses_tree.item(selected[0], "values")[0])
        self.db.delete_course(course_id)
        self.refresh_all()

    def add_enrollment(self) -> None:
        student_key = self.student_choice.get()
        course_key = self.course_choice.get()
        if not student_key or not course_key:
            messagebox.showerror("Input Error", "Please choose both student and course.")
            return

        student_id = self.student_map.get(student_key)
        course_id = self.course_map.get(course_key)
        if not student_id or not course_id:
            messagebox.showerror("Selection Error", "Invalid student/course selection.")
            return

        try:
            self.db.add_enrollment(student_id, course_id)
            self.refresh_enrollments()
            messagebox.showinfo("Success", "Enrollment added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Already Enrolled", "This student is already enrolled in this course."
            )

    def delete_enrollment(self) -> None:
        selected = self.enrollments_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Select an enrollment to delete.")
            return
        enrollment_id = int(self.enrollments_tree.item(selected[0], "values")[0])
        self.db.delete_enrollment(enrollment_id)
        self.refresh_enrollments()

    def on_close(self) -> None:
        self.db.close()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    ClassManagementUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
