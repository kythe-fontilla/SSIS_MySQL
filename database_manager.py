import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
from models import DataLookup


class DatabaseManager:

    def __init__(self):
        self.config = DB_CONFIG
        self._test_connection()

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def _test_connection(self):
        try:
            conn = self._get_connection()
            conn.close()
            print("✅ Connected to MySQL successfully.")
        except Error as e:
            print(f"❌ MySQL connection failed: {e}")

    # ========== STUDENT OPERATIONS ==========
    def get_all_students(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, firstname, lastname, program_code, year_level AS year, gender FROM students")
            students = cursor.fetchall()
            cursor.close()
            conn.close()
            return students
        except Error as e:
            print(f"Error fetching students: {e}")
            return []

    def get_students_with_details(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    s.id, s.firstname, s.lastname,
                    s.program_code,
                    COALESCE(p.name, 'N/A') AS program_name,
                    COALESCE(p.college_code, 'N/A') AS college_code,
                    COALESCE(c.name, 'N/A') AS college_name,
                    s.year_level AS year,
                    s.gender
                FROM students s
                LEFT JOIN programs p ON s.program_code = p.code
                LEFT JOIN colleges c ON p.college_code = c.code
            """)
            students = cursor.fetchall()
            cursor.close()
            conn.close()
            return students
        except Error as e:
            print(f"Error fetching student details: {e}")
            return []

    def add_student(self, student_data):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (id, firstname, lastname, program_code, year_level, gender) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    student_data['id'],
                    student_data['firstname'],
                    student_data['lastname'],
                    student_data['program_code'] if student_data['program_code'] != 'N/A' else None,
                    student_data['year'],
                    student_data['gender']
                )
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True, f"Student {student_data['id']} added successfully"
        except mysql.connector.IntegrityError as e:
            if e.errno == 1062:
                return False, f"Student ID {student_data['id']} already exists"
            return False, str(e)
        except Error as e:
            return False, f"Error saving student: {str(e)}"

    def update_student(self, student_data, original_id=None):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            search_id = original_id if original_id else student_data['id']
            cursor.execute(
                "UPDATE students SET id=%s, firstname=%s, lastname=%s, "
                "program_code=%s, year_level=%s, gender=%s WHERE id=%s",
                (
                    student_data['id'],
                    student_data['firstname'],
                    student_data['lastname'],
                    student_data['program_code'] if student_data['program_code'] != 'N/A' else None,
                    student_data['year'],
                    student_data['gender'],
                    search_id
                )
            )
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            if affected == 0:
                return False, f"Student with ID {search_id} not found"
            return True, f"Student {student_data['firstname']} {student_data['lastname']} updated successfully!"
        except mysql.connector.IntegrityError as e:
            if e.errno == 1062:
                return False, f"Student ID {student_data['id']} already exists"
            return False, str(e)
        except Error as e:
            return False, f"Error updating student: {str(e)}"

    def delete_student(self, student_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT firstname, lastname FROM students WHERE id=%s", (student_id,))
            student = cursor.fetchone()
            if not student:
                return False, f"Student with ID {student_id} not found"
            cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return True, f"Student {student['firstname']} {student['lastname']} (ID: {student_id}) deleted successfully!"
        except Error as e:
            return False, f"Error deleting student: {str(e)}"

    # ========== PROGRAM OPERATIONS ==========
    def get_all_programs(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT code, name, college_code AS college FROM programs")
            programs = cursor.fetchall()
            cursor.close()
            conn.close()
            return programs
        except Error as e:
            print(f"Error fetching programs: {e}")
            return []

    def get_programs_cached(self):
        return self.get_all_programs()

    def get_colleges_cached(self):
        return self.get_all_colleges()

    def get_program_by_code(self, code):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT code, name, college_code AS college FROM programs WHERE code=%s", (code,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
        except Error:
            return None

    def get_program_display_list(self):
        programs = self.get_all_programs()
        return DataLookup.get_program_display_list(programs)

    def program_exists(self, program_code):
        return self.get_program_by_code(program_code) is not None

    def add_program(self, program_data):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO programs (code, name, college_code) VALUES (%s, %s, %s)",
                (program_data['code'], program_data['name'],
                 program_data['college'] if program_data['college'] != 'N/A' else None)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True, f"Program {program_data['code']} added successfully"
        except mysql.connector.IntegrityError as e:
            if e.errno == 1062:
                return False, f"Program code {program_data['code']} already exists"
            return False, str(e)
        except Error as e:
            return False, f"Error saving program: {str(e)}"

    def update_program(self, program_data, old_code=None):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            search_code = old_code if old_code else program_data['code']
            # ON UPDATE CASCADE handles student program_code updates automatically
            cursor.execute(
                "UPDATE programs SET code=%s, name=%s, college_code=%s WHERE code=%s",
                (program_data['code'], program_data['name'],
                 program_data['college'] if program_data['college'] != 'N/A' else None,
                 search_code)
            )
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            if affected == 0:
                return False, f"Program {search_code} not found"
            return True, f"Program {program_data['name']} updated successfully!"
        except Error as e:
            return False, f"Error updating program: {str(e)}"

    def delete_program(self, program_code):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name FROM programs WHERE code=%s", (program_code,))
            program = cursor.fetchone()
            if not program:
                return False, f"Program {program_code} not found"
            # ON DELETE SET NULL handles student program_code automatically
            cursor.execute("DELETE FROM programs WHERE code=%s", (program_code,))
            conn.commit()
            cursor.close()
            conn.close()
            return True, f"Program {program['name']} ({program_code}) deleted successfully!"
        except Error as e:
            return False, f"Error deleting program: {str(e)}"

    # ========== COLLEGE OPERATIONS ==========
    def get_all_colleges(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT code, name FROM colleges")
            colleges = cursor.fetchall()
            cursor.close()
            conn.close()
            return colleges
        except Error as e:
            print(f"Error fetching colleges: {e}")
            return []

    def get_college_by_code(self, code):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT code, name FROM colleges WHERE code=%s", (code,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
        except Error:
            return None

    def add_college(self, college_data):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO colleges (code, name) VALUES (%s, %s)",
                (college_data['code'], college_data['name'])
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True, f"College {college_data['code']} added successfully"
        except mysql.connector.IntegrityError as e:
            if e.errno == 1062:
                return False, f"College code {college_data['code']} already exists"
            return False, str(e)
        except Error as e:
            return False, f"Error saving college: {str(e)}"

    def update_college(self, college_data, old_code=None):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            search_code = old_code if old_code else college_data['code']
            # ON UPDATE CASCADE handles programs automatically
            cursor.execute(
                "UPDATE colleges SET code=%s, name=%s WHERE code=%s",
                (college_data['code'], college_data['name'], search_code)
            )
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            if affected == 0:
                return False, f"College {search_code} not found"
            return True, f"College {college_data['name']} updated successfully!"
        except Error as e:
            return False, f"Error updating college: {str(e)}"

    def delete_college(self, college_code):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name FROM colleges WHERE code=%s", (college_code,))
            college = cursor.fetchone()
            if not college:
                return False, f"College {college_code} not found"
            # ON DELETE SET NULL on programs.college_code handles cascade automatically
            cursor.execute("DELETE FROM colleges WHERE code=%s", (college_code,))
            conn.commit()
            cursor.close()
            conn.close()
            return True, f"College {college['name']} ({college_code}) deleted successfully!"
        except Error as e:
            return False, f"Error deleting college: {str(e)}"

    def _refresh_cache(self):
        pass  # No cache needed with MySQL — queries are always live