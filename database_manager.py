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
            print("Connected to MySQL successfully.")
            return True
        except Error as e:
            return False, str(e)
    
    def _execute_query(self, query, params=None, fetch=None, commit=False):
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            result = None
            if fetch == 'all':
                result = cursor.fetchall()
            elif fetch == 'one':
                result = cursor.fetchone()
            
            if commit:
                conn.commit()
            
            cursor.close()
            conn.close()
            return True, result
        
        except Error as e:
            return False, str(e)

    def get_all_students(self):
        success, result = self._execute_query(
            "SELECT id, firstname, lastname, program_code, year_level AS year, gender FROM students",
            fetch='all'
        )
        return result if success else []

    def get_students_with_details(self):
        success, result = self._execute_query("""
            SELECT 
                s.id, s.firstname, s.lastname,
                s.program_code,
                COALESCE(p.name, 'NULL') AS program_name,
                COALESCE(p.college_code, 'NULL') AS college_code,
                COALESCE(c.name, 'NULL') AS college_name,
                s.year_level AS year,
                s.gender
            FROM students s
            LEFT JOIN programs p ON s.program_code = p.code
            LEFT JOIN colleges c ON p.college_code = c.code
        """, fetch='all')
        return result if success else []

    def add_student(self, student_data):
        success, result = self._execute_query(
            "INSERT INTO students (id, firstname, lastname, program_code, year_level, gender) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                student_data['id'],
                student_data['firstname'],
                student_data['lastname'],
                student_data['program_code'] if student_data['program_code'] != 'NULL' else None,
                student_data['year'],
                student_data['gender']
            ),
            commit=True
        )
        if not success:
            if '1062' in str(result):
                return False, f"Student ID {student_data['id']} already exists"
            return False, f"Database error: {result}"
        return True, f"Student {student_data['id']} added successfully"

    def update_student(self, student_data, original_id=None):
        search_id = original_id if original_id else student_data['id']
        success, result = self._execute_query(
            "UPDATE students SET id=%s, firstname=%s, lastname=%s, "
            "program_code=%s, year_level=%s, gender=%s WHERE id=%s",
            (
                student_data['id'],
                student_data['firstname'],
                student_data['lastname'],
                student_data['program_code'] if student_data['program_code'] != 'NULL' else None,
                student_data['year'],
                student_data['gender'],
                search_id
            ),
            commit=True
        )
        if not success:
            if '1062' in str(result):
                return False, f"Student ID {student_data['id']} already exists"
            return False, f"Database error: {result}"
        return True, f"Student {student_data['firstname']} {student_data['lastname']} updated successfully!"

    def delete_student(self, student_id):
        success, student = self._execute_query(
            "SELECT firstname, lastname FROM students WHERE id=%s",
            (student_id,),
            fetch='one'
        )
        if not success or not student:
            return False, f"Student with ID {student_id} not found"
        
        success, result = self._execute_query(
            "DELETE FROM students WHERE id=%s",
            (student_id,),
            commit=True
        )
        if not success:
            return False, f"Database error: {result}"
        return True, f"Student {student['firstname']} {student['lastname']} (ID: {student_id}) deleted successfully!"

    def get_all_programs(self):
        success, result = self._execute_query(
            "SELECT code, name, college_code AS college FROM programs",
            fetch='all'
        )
        return result if success else []

    def get_program_by_code(self, code):
        success, result = self._execute_query(
            "SELECT code, name, college_code AS college FROM programs WHERE code=%s",
            (code,),
            fetch='one'
        )
        return result if success else None

    def add_program(self, program_data):
        success, result = self._execute_query(
            "INSERT INTO programs (code, name, college_code) VALUES (%s, %s, %s)",
            (
                program_data['code'],
                program_data['name'],
                program_data['college'] if program_data['college'] != 'NULL' else None
            ),
            commit=True
        )
        if not success:
            if '1062' in str(result):
                return False, f"Program code {program_data['code']} already exists"
            return False, f"Database error: {result}"
        return True, f"Program {program_data['code']} added successfully"

    def update_program(self, program_data, old_code=None):
        search_code = old_code if old_code else program_data['code']
        success, result = self._execute_query(
            "UPDATE programs SET code=%s, name=%s, college_code=%s WHERE code=%s",
            (
                program_data['code'],
                program_data['name'],
                program_data['college'] if program_data['college'] != 'NULL' else None,
                search_code
            ),
            commit=True
        )
        if not success:
            return False, f"Database error: {result}"
        return True, f"Program {program_data['name']} updated successfully!"

    def delete_program(self, program_code):
        success, program = self._execute_query(
            "SELECT name FROM programs WHERE code=%s",
            (program_code,),
            fetch='one'
        )
        if not success or not program:
            return False, f"Program {program_code} not found"
        
        success, result = self._execute_query(
            "DELETE FROM programs WHERE code=%s",
            (program_code,),
            commit=True
        )
        if not success:
            return False, f"Database error: {result}"
        return True, f"Program {program['name']} ({program_code}) deleted successfully!"

    def get_all_colleges(self):
        success, result = self._execute_query(
            "SELECT code, name FROM colleges",
            fetch='all'
        )
        return result if success else []

    def get_college_by_code(self, code):
        success, result = self._execute_query(
            "SELECT code, name FROM colleges WHERE code=%s",
            (code,),
            fetch='one'
        )
        return result if success else None

    def add_college(self, college_data):
        success, result = self._execute_query(
            "INSERT INTO colleges (code, name) VALUES (%s, %s)",
            (college_data['code'], college_data['name']),
            commit=True
        )
        if not success:
            if '1062' in str(result):
                return False, f"College code {college_data['code']} already exists"
            return False, f"Database error: {result}"
        return True, f"College {college_data['code']} added successfully"

    def update_college(self, college_data, old_code=None):
        search_code = old_code if old_code else college_data['code']
        success, result = self._execute_query(
            "UPDATE colleges SET code=%s, name=%s WHERE code=%s",
            (college_data['code'], college_data['name'], search_code),
            commit=True
        )
        if not success:
            return False, f"Database error: {result}"
        return True, f"College {college_data['name']} updated successfully!"

    def delete_college(self, college_code):
        success, college = self._execute_query(
            "SELECT name FROM colleges WHERE code=%s",
            (college_code,),
            fetch='one'
        )
        if not success or not college:
            return False, f"College {college_code} not found"
        
        success, result = self._execute_query(
            "DELETE FROM colleges WHERE code=%s",
            (college_code,),
            commit=True
        )
        if not success:
            return False, f"Database error: {result}"
        return True, f"College {college['name']} ({college_code}) deleted successfully!"