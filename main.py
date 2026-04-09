from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, 
                             QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QRadioButton, QButtonGroup, QCompleter, QWidget)
from PyQt6.QtCore import Qt
import sys
from database_manager import DatabaseManager
from models import StudentValidator, CollegeValidator, ProgramValidator


class AddStudentDialog(QDialog):
    
    def __init__(self, db_manager, parent=None, student_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.student_data = student_data
        self.is_edit_mode = student_data is not None
        self.original_id = student_data['id'] if student_data else None
        
        self.setWindowTitle("Edit Student" if self.is_edit_mode else "Add New Student")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.program_display_list = self.db_manager.get_program_display_list()
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.populate_form()
        
        self.id_input.setFocus()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.create_id_field(layout)
        self.create_firstname_field(layout)
        self.create_lastname_field(layout)
        self.create_program_field(layout)
        self.create_year_field(layout)
        self.create_gender_field(layout)
        
        if not hasattr(self, 'program_data'):
            self.program_data = {}

        layout.addSpacing(20)
        self.create_buttons(layout)
        
        self.setLayout(layout)
    
    def create_id_field(self, layout):
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Student ID (YYYY-NNNN):*"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("2024-0001")
        
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)
    
    def create_firstname_field(self, layout):
        firstname_layout = QHBoxLayout()
        firstname_layout.addWidget(QLabel("First Name:*"))
        self.firstname_input = QLineEdit()
        self.firstname_input.setPlaceholderText("John")
        firstname_layout.addWidget(self.firstname_input)
        layout.addLayout(firstname_layout)
    
    def create_lastname_field(self, layout):
        lastname_layout = QHBoxLayout()
        lastname_layout.addWidget(QLabel("Last Name:*"))
        self.lastname_input = QLineEdit()
        self.lastname_input.setPlaceholderText("Smith")
        lastname_layout.addWidget(self.lastname_input)
        layout.addLayout(lastname_layout)
    
    def create_program_field(self, layout):
        program_layout = QHBoxLayout()
        program_layout.addWidget(QLabel("Program Name:*"))
        
        self.program_combo = QComboBox()
        self.program_combo.setEditable(True)
        self.program_combo.setMinimumWidth(350)
        
        display_texts = [item['display'] for item in self.program_display_list]
        self.program_combo.addItems(display_texts)
        
        completer = QCompleter(display_texts)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.program_combo.setCompleter(completer)
        
        self.program_data = {item['display']: item for item in self.program_display_list}
        
        program_layout.addWidget(self.program_combo)
        layout.addLayout(program_layout)
    
    def create_year_field(self, layout):
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Year Level:*"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(['1', '2', '3', '4', '5'])
        year_layout.addWidget(self.year_combo)
        layout.addLayout(year_layout)
    
    def create_gender_field(self, layout):
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(QLabel("Gender:*"))
        
        self.gender_group = QButtonGroup(self)
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        
        self.gender_group.addButton(self.male_radio)
        self.gender_group.addButton(self.female_radio)
        self.male_radio.setChecked(True)
        
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        layout.addLayout(gender_layout)
    
    def create_buttons(self, layout):
        button_layout = QHBoxLayout()
        
        save_text = "Update Student" if self.is_edit_mode else "Save Student"
        self.save_button = QPushButton(save_text)
        self.save_button.clicked.connect(self.save_student)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def populate_form(self):
        if not self.student_data:
            return
        
        self.id_input.setText(self.student_data['id'])
        self.firstname_input.setText(self.student_data['firstname'])
        self.lastname_input.setText(self.student_data['lastname'])
        
        program_name = self.student_data.get('program_name', '')
        for i in range(self.program_combo.count()):
            if program_name in self.program_combo.itemText(i):
                self.program_combo.setCurrentIndex(i)
                break
        
        year_index = self.year_combo.findText(self.student_data['year'])
        if year_index >= 0:
            self.year_combo.setCurrentIndex(year_index)
        
        if self.student_data['gender'] == 'Male':
            self.male_radio.setChecked(True)
        else:
            self.female_radio.setChecked(True)
    
    def get_selected_program_code(self):
        selected_text = self.program_combo.currentText().strip()
        
        if selected_text == 'N/A':
            return 'N/A'
    
        if selected_text in self.program_data:
            return self.program_data[selected_text]['code']
        
        for display, data in self.program_data.items():
            if selected_text.lower() in display.lower():
                return data['code']
        
        return None
        
    def validate_student_data(self, student_data):
    
        # Validate Student ID
        valid, message = StudentValidator.validate_student_id(student_data['id'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.id_input.setFocus()
            return False
        
        if self.is_edit_mode:
            # If ID is different from original, check for duplicates
            if student_data['id'] != self.original_id:
                students = self.db_manager.get_all_students()
                for student in students:
                    if student['id'] == student_data['id']:
                        QMessageBox.warning(
                            self, 
                            "Validation Error", 
                            f"Student ID {student_data['id']} already exists in the database."
                        )
                        self.id_input.setFocus()
                        return False
        else:
            students = self.db_manager.get_all_students()
            for student in students:
                if student['id'] == student_data['id']:
                    QMessageBox.warning(
                        self, 
                        "Validation Error", 
                        f"Student ID {student_data['id']} already exists in the database."
                    )
                    self.id_input.setFocus()
                    return False
        
        # Modify program validation to accept 'N/A'
        if student_data['program_code']:
            reply = QMessageBox.warning(
                self, "No Program Selected",
                "You are setting this student to have no program. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.program_combo.setFocus()
                return False
        else:
            if not self.db_manager.program_exists(student_data['program_code']):
                QMessageBox.warning(self, "Validation Error", 
                                f"Program '{self.program_combo.currentText()}' does not exist.\n"
                                "Please select a program from the list.")
                self.program_combo.setFocus()
                return False
        
        # Validate First Name
        valid, message = StudentValidator.validate_name(student_data['firstname'], "First Name")
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.firstname_input.setFocus()
            return False
        
        # Validate Last Name
        valid, message = StudentValidator.validate_name(student_data['lastname'], "Last Name")
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.lastname_input.setFocus()
            return False
        
        # Validate Program Selection
        if not student_data['program_code']:
            QMessageBox.warning(self, "Validation Error", 
                              "Please select a valid program from the list")
            self.program_combo.setFocus()
            return False
        
        if not self.db_manager.program_exists(student_data['program_code']):
            QMessageBox.warning(self, "Validation Error", 
                              f"Program '{self.program_combo.currentText()}' does not exist.\n"
                              "Please select a program from the list.")
            self.program_combo.setFocus()
            return False
        
        # Validate Year
        valid, message = StudentValidator.validate_year(student_data['year'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return False
        
        return True
    
    def get_student_data(self):
        selected_program_code = self.get_selected_program_code()
        
        return {
            'id': self.id_input.text().strip(),
            'firstname': self.firstname_input.text().strip(),
            'lastname': self.lastname_input.text().strip(),
            'program_code': selected_program_code,
            'year': self.year_combo.currentText(),
            'gender': 'Male' if self.male_radio.isChecked() else 'Female'
        }
    
    def save_student(self):
        try:
            # Validate and save the student
            student_data = self.get_student_data()
            
            if not self.validate_student_data(student_data):
                return
            
            program_display = self.program_combo.currentText()
            action = "update" if self.is_edit_mode else "add"
            
            if self.is_edit_mode and student_data['id'] != self.original_id:
                confirm_msg = (
                    f"⚠️  You are changing the student ID!\n\n"
                    f"Old ID: {self.original_id}\n"
                    f"New ID: {student_data['id']}\n"
                    f"Name: {student_data['lastname']}, {student_data['firstname']}\n"
                    f"Program: {program_display}\n"
                    f"Year: {student_data['year']}\n"
                    f"Gender: {student_data['gender']}\n\n"
                    f"Are you sure you want to continue?"
                )
            else:
                confirm_msg = (
                    f"Are you sure you want to {action} this student?\n\n"
                    f"Student ID: {student_data['id']}\n"
                    f"Name: {student_data['lastname']}, {student_data['firstname']}\n"
                    f"Program: {program_display}\n"
                    f"Year: {student_data['year']}\n"
                    f"Gender: {student_data['gender']}"
                )
            
            reply = QMessageBox.question(
                self, f"Confirm {action.title()}", confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                
                if self.is_edit_mode:
                    success, message = self.db_manager.update_student(student_data, self.original_id)
                else:
                    success, message = self.db_manager.add_student(student_data)
                
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", message)
        
        except Exception as e:
            print(f"ERROR in save_student: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred:\n{str(e)}")


class AddCollegeDialog(QDialog):
    
    def __init__(self, db_manager, parent=None, college_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.college_data = college_data 
        self.is_edit_mode = college_data is not None
        
        self.setWindowTitle("Edit College" if self.is_edit_mode else "Add New College")
        self.setModal(True)
        self.setMinimumWidth(400)
        
    
        self.setup_ui()
        
        # Pre-fill data if editing
        if self.is_edit_mode:
            self.populate_form()
        
        self.collegename_input.setFocus()
    
    def setup_ui(self):
        """Create and arrange all UI elements"""
        layout = QVBoxLayout()
        
        self.create_collegename_field(layout)
        self.create_collegecode_field(layout)
        
        layout.addSpacing(20)
        self.create_buttons(layout)
        
        self.setLayout(layout)
    
    def create_collegename_field(self, layout):
        collegename_layout = QHBoxLayout()
        collegename_layout.addWidget(QLabel("College name:*"))
        self.collegename_input = QLineEdit()
        self.collegename_input.setPlaceholderText("College of Computer Studies")
        collegename_layout.addWidget(self.collegename_input)
        layout.addLayout(collegename_layout)
        
    def create_collegecode_field(self, layout):
        collegecode_layout = QHBoxLayout()
        collegecode_layout.addWidget(QLabel("College Code:*"))
        self.collegecode_input = QLineEdit()
        self.collegecode_input.setPlaceholderText("CCS")
        collegecode_layout.addWidget(self.collegecode_input)
        layout.addLayout(collegecode_layout)
    
    def create_buttons(self, layout):
        button_layout = QHBoxLayout()
        
        save_text = "Update College" if self.is_edit_mode else "Save College"
        self.save_button = QPushButton(save_text)
        self.save_button.clicked.connect(self.save_college)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def populate_form(self):
        if not self.college_data:
            return
        
        self.collegename_input.setText(self.college_data['name'])
        self.collegecode_input.setText(self.college_data['code'])
    
    def validate_college_data(self, college_data):

        # Validate college name
        valid, message = CollegeValidator.validate_college_name(college_data['name'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.collegename_input.setFocus()
            return False
        
        # Validate college code format
        valid, message = CollegeValidator.validate_college_code(college_data['code'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.collegecode_input.setFocus()
            return False
        if self.is_edit_mode:
            current_code = self.college_data['code']  
        else:
            current_code = None
        
        valid, message = CollegeValidator.check_duplicate_code(
            self.db_manager, 
            college_data['code'], 
            current_code  
        )
        
        if not valid:
            QMessageBox.warning(self, "Duplicate Error", message)
            self.collegecode_input.setFocus()
            return False
        
        return True
    
    def get_college_data(self):
        """Collect data from form inputs"""
        college_data = {
            'code': self.collegecode_input.text().strip().upper(),
            'name': self.collegename_input.text().strip()
        }

        return college_data
    
    def save_college(self):
        """Validate and save the college"""
        college_data = self.get_college_data()
        
        if not self.validate_college_data(college_data):
            return
        
        action = "update" if self.is_edit_mode else "add"
        if self.is_edit_mode and self.college_data['code'] != college_data['code']:
            confirm_msg = (
                f"⚠️  You are changing the college code!\n\n"
                f"Old Code: {self.college_data['code']}\n"
                f"New Code: {college_data['code']}\n"
                f"College Name: {college_data['name']}\n\n"
                f"This will update ALL programs that reference this college.\n"
                f"Are you sure you want to continue?"
            )
        else:
            confirm_msg = (
                f"Are you sure you want to {action} this college?\n\n"
                f"College Code: {college_data['code']}\n"
                f"College Name: {college_data['name']}"
            )
        
        reply = QMessageBox.question(
            self, f"Confirm {action.title()}", confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.is_edit_mode:
                old_code = self.college_data['code']
                success, message = self.db_manager.update_college(college_data, old_code)
            else:
                success, message = self.db_manager.add_college(college_data)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", message)

class AddProgramDialog(QDialog):
    """Dialog for adding/editing programs"""
    
    def __init__(self, db_manager, parent=None, program_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.program_data = program_data 
        self.is_edit_mode = program_data is not None
        
        self.setWindowTitle("Edit Program" if self.is_edit_mode else "Add New Program")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.colleges = self.db_manager.get_all_colleges()
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.populate_form()
        
        self.programname_input.setFocus()
    
    def setup_ui(self):
        """Create and arrange all UI elements"""
        layout = QVBoxLayout()
        
        self.create_programname_field(layout)
        self.create_programcode_field(layout)
        self.create_college_field(layout)
        
        layout.addSpacing(20)
        self.create_buttons(layout)
        
        self.setLayout(layout)
    
    def create_programname_field(self, layout):
        programname_layout = QHBoxLayout()
        programname_layout.addWidget(QLabel("Program name:*"))
        self.programname_input = QLineEdit()
        self.programname_input.setPlaceholderText("Bachelor of Science in Computer Science")
        programname_layout.addWidget(self.programname_input)
        layout.addLayout(programname_layout)
        
    def create_programcode_field(self, layout):
        programcode_layout = QHBoxLayout()
        programcode_layout.addWidget(QLabel("Program Code:*"))
        self.programcode_input = QLineEdit()
        self.programcode_input.setPlaceholderText("BSCS")
        programcode_layout.addWidget(self.programcode_input)
        layout.addLayout(programcode_layout)

    def create_college_field(self, layout):
        college_layout = QHBoxLayout()
        college_layout.addWidget(QLabel("College:*"))
        
        self.college_combo = QComboBox()
        self.college_combo.setMinimumWidth(350)
        
        for college in self.colleges:
            display_text = f"{college['code']} - {college['name']}"
            self.college_combo.addItem(display_text, college['code']) 
        
        college_layout.addWidget(self.college_combo)
        layout.addLayout(college_layout)
    
    def create_buttons(self, layout):
        button_layout = QHBoxLayout()
        
        save_text = "Update Program" if self.is_edit_mode else "Save Program"
        self.save_button = QPushButton(save_text)
        self.save_button.clicked.connect(self.save_program)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def populate_form(self):
        if not self.program_data:
            return
        
        self.programname_input.setText(self.program_data['name'])
        self.programcode_input.setText(self.program_data['code'])

        college_code = self.program_data['college']
        for i in range(self.college_combo.count()):
            if self.college_combo.itemData(i) == college_code:
                self.college_combo.setCurrentIndex(i)
                break
    
    def validate_program_data(self, program_data):

        # Validate program name
        valid, message = ProgramValidator.validate_program_name(program_data['name'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.programname_input.setFocus()
            return False
        
        # Validate program code format
        valid, message = ProgramValidator.validate_program_code(program_data['code'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.programcode_input.setFocus()
            return False
        
        # Validate college is selected
        if not program_data['college']:
            QMessageBox.warning(self, "Validation Error", 
                            "Please select a college")
            self.college_combo.setFocus()
            return False


        if self.is_edit_mode:
            current_code = self.program_data['code']  
        else:
            current_code = None
        
        valid, message = ProgramValidator.check_duplicate_code(
            self.db_manager, 
            program_data['code'], 
            current_code 
        )
        
        if not valid:
            QMessageBox.warning(self, "Duplicate Error", message)
            self.programcode_input.setFocus()
            return False
        
        return True
    
    def get_program_data(self):
        program_data = {
            'code': self.programcode_input.text().strip().upper(),
            'name': self.programname_input.text().strip(),
            'college': self.college_combo.currentData()
        }
        
        return program_data
    
    def save_program(self):
        program_data = self.get_program_data()
        
        if not self.validate_program_data(program_data):
            return
        
        action = "update" if self.is_edit_mode else "add"

        college_display = self.college_combo.currentText()

        if self.is_edit_mode and self.program_data['code'] != program_data['code']:
            confirm_msg = (
                f"⚠️  You are changing the program code!\n\n"
                f"Old Code: {self.program_data['code']}\n"
                f"New Code: {program_data['code']}\n"
                f"Program Name: {program_data['name']}\n\n"
                f"College: {college_display}\n\n"
                f"This will update ALL students that reference this program.\n"
                f"Are you sure you want to continue?"
            )
        else:
            confirm_msg = (
                f"Are you sure you want to {action} this program?\n\n"
                f"Program Code: {program_data['code']}\n"
                f"Program Name: {program_data['name']}\n"
                f"College: {college_display}"
            )
        
        reply = QMessageBox.question(
            self, f"Confirm {action.title()}", confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.is_edit_mode:
                old_code = self.program_data['code']
                success, message = self.db_manager.update_program(program_data, old_code)
            else:
                success, message = self.db_manager.add_program(program_data)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", message)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        uic.loadUi('main_window.ui', self)
        self.center_window()

        self.db_manager = DatabaseManager()
        result = self.db_manager._test_connection()
        if result != True:
            QMessageBox.critical(
                None,
                "Database Connection Error",
                f"Could not connect to MySQL.\n\n"
                f"Please make sure XAMPP MySQL is running.\n\n"
                f"Error: {result[1]}"
            )
            sys.exit(1)

        self.db_manager = DatabaseManager()

        self.resize(1100, 610)

        self.students_page = 1
        self.students_per_page = 20
        self.students_total_pages = 1
        self.all_students = []  
        self.current_search_text = "" 

        self.programs_page = 1
        self.programs_per_page = 20
        self.programs_total_pages = 1
        self.all_programs = []  
        self.current_programs_search_text = "" 

        self.colleges_page = 1
        self.colleges_per_page = 20
        self.colleges_total_pages = 1
        self.all_colleges = []  
        self.current_colleges_search_text = "" 
        
        self.connect_buttons()
        self.load_students_table()
        self.load_colleges_table()
        self.load_programs_table()
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        center_point = screen.center()
        window.moveCenter(center_point)
        self.move(window.topLeft())
    
    def connect_buttons(self):
        self.studentsButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.programsButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.collegesButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.addStudentButton.clicked.connect(self.open_add_student_dialog)
        self.addCollegeButton.clicked.connect(self.open_add_college_dialog)
        self.addProgramButton.clicked.connect(self.open_add_program_dialog)

        self.sortComboBox_2.currentTextChanged.connect(self.sort_students_by_dropdown)
        self.sortComboBox_3.currentTextChanged.connect(self.sort_programs_by_dropdown)

        self.searchLineEdit_2.textChanged.connect(self.search_students)
        self.searchLineEdit_3.textChanged.connect(self.search_programs)
        self.searchLineEdit_4.textChanged.connect(self.search_colleges)

        self.prevButtonStudents.clicked.connect(self.prev_students_page)
        self.nextButtonStudents.clicked.connect(self.next_students_page)
        self.jumpStartStudent.clicked.connect(self.jump_to_firststudent_page)
        self.jumpEndStudent.clicked.connect(self.jump_to_endstudent_page)
        
        
        self.prevButtonPrograms.clicked.connect(self.prev_programs_page)
        self.nextButtonPrograms.clicked.connect(self.next_programs_page)
        self.jumpStartProgram.clicked.connect(self.jump_to_firstprogram_page)
        self.jumpEndProgram.clicked.connect(self.jump_to_endprogram_page)
        
        self.prevButtonColleges.clicked.connect(self.prev_colleges_page)
        self.nextButtonColleges.clicked.connect(self.next_colleges_page)
        self.jumpStartCollege.clicked.connect(self.jump_to_firstcollege_page)
        self.jumpEndCollege.clicked.connect(self.jump_to_endcollege_page)
    
    def sort_students_by_dropdown(self, sort_by):
        sort_mapping = {
            'Program': 'program_name',   
            'Lastname': 'lastname', 
            'Firstname': 'firstname',     
            'ID': 'id',        
            'College': 'college_code',    
            'Year' : 'year'      
        }
    
        key = sort_mapping.get(sort_by)
        if key:
            self.all_students.sort(key=lambda s: s.get(key, '').lower())
            self.students_page = 1
            self.load_students_table(refresh=False)

    def search_students(self, search_text):
        self.current_search_text = search_text
        self.students_page = 1
        self.load_students_table()    
    
    def open_add_student_dialog(self):
        dialog = AddStudentDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_students_table()
    
    def open_edit_student_dialog(self, row):
        student_data = {
            'id': self.dataTableStudents.item(row, 0).text(),
            'firstname': self.dataTableStudents.item(row, 1).text(),
            'lastname': self.dataTableStudents.item(row, 2).text(),
            'program_name': self.dataTableStudents.item(row, 3).text(),
            'year': self.dataTableStudents.item(row, 5).text(),
            'gender': self.dataTableStudents.item(row, 6).text()
        }
        
        dialog = AddStudentDialog(self.db_manager, self, student_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_students_table()
    
    def delete_student(self, row):
        student_id = self.dataTableStudents.item(row, 0).text()
        firstname = self.dataTableStudents.item(row, 1).text()
        lastname = self.dataTableStudents.item(row, 2).text()
        student_name = f"{firstname} {lastname}"
        
        reply = QMessageBox.question(
            self,
            'Delete Student',
            f'Are you sure you want to delete student:\n\n'
            f'{student_name} (ID: {student_id})?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db_manager.delete_student(student_id)
            
            if success:
                self.load_students_table()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)
    
    def add_action_buttons(self, row):
        """Add Edit and Delete buttons to a table row"""
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(4, 2, 4, 2)
        button_layout.setSpacing(4)
        
        edit_btn = QPushButton("🖉 Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;  /* Emerald green */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
                
                /* Subtle shadow */
                box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
                
                /* Smooth transitions */
                transition: all 0.2s ease;
            }
            
            QPushButton:hover {
                background-color: #059669;  /* Darker emerald */
                transform: translateY(-1px);  /* Slight lift */
                box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
            }
            
            QPushButton:pressed {
                background-color: #047857;  /* Even darker */
                transform: translateY(0px);  /* Press down effect */
                box-shadow: 0 1px 2px rgba(16, 185, 129, 0.2);
            }
        """)

        edit_btn.clicked.connect(lambda checked, r=row: self.open_edit_student_dialog(r))
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.setStyleSheet("""
        QPushButton {
            background-color: #ef4444;  /* Bright red */
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 12px;
            
            /* Subtle shadow */
            box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
            
            /* Smooth transitions */
            transition: all 0.2s ease;
        }
        
        QPushButton:hover {
            background-color: #dc2626;  /* Darker red */
            transform: translateY(-1px);  /* Slight lift */
            box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
        }
        
        QPushButton:pressed {
            background-color: #b91c1c;  /* Even darker */
            transform: translateY(0px);  /* Press down effect */
            box-shadow: 0 1px 2px rgba(239, 68, 68, 0.2);
        }
    """)

        delete_btn.clicked.connect(lambda checked, r=row: self.delete_student(r))
        
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_widget.setLayout(button_layout)
        
        self.dataTableStudents.setCellWidget(row, 7, button_widget)

    def prev_students_page(self):
        if self.students_page > 1:
            self.students_page -= 1
            self.load_students_table(refresh=False)

    def next_students_page(self):
        if self.students_page < self.students_total_pages:
            self.students_page += 1
            self.load_students_table(refresh=False)

    def update_students_pagination(self):
        self.pageInfoLabelStudents.setText(
            f"Page {self.students_page} of {self.students_total_pages}"
        )
        self.prevButtonStudents.setEnabled(self.students_page > 1)
        self.jumpStartStudent.setEnabled(self.students_page > 1)

        self.nextButtonStudents.setEnabled(self.students_page < self.students_total_pages)
        self.jumpEndStudent.setEnabled(self.students_page < self.students_total_pages)
    
    def jump_to_firststudent_page(self):
        if self.students_page > 1:
            self.students_page = 1
            self.load_students_table(refresh=False)

    def jump_to_endstudent_page(self):
        if self.students_page != self.students_total_pages:
            self.students_page = self.students_total_pages
            self.load_students_table(refresh=False)
    
    def get_page_data(self, all_data, current_page, per_page):
        import math
        
        total_pages = math.ceil(len(all_data) / per_page)
        if total_pages == 0:
            total_pages = 1
        
        start_idx = (current_page - 1) * per_page
        end_idx = start_idx + per_page
        
        page_data = all_data[start_idx:end_idx]
        
        return page_data, total_pages

    def load_students_table(self, refresh=True):
        table = self.dataTableStudents
        table.setSortingEnabled(False)
        table.setRowCount(0)
        
        if refresh:
            self.all_students = self.db_manager.get_students_with_details()
    
        search_text = self.current_search_text.lower().strip()
        if search_text:
            filtered = [
                s for s in self.all_students
                if search_text in s['id'].lower()
                or search_text in s['firstname'].lower()
                or search_text in s['lastname'].lower()
                or search_text in s.get('program_name', s['program_code']).lower()
                or search_text in s.get('college_code', '').lower()
            ]
        else:
            filtered = self.all_students

        students, total_pages = self.get_page_data(filtered, self.students_page, self.students_per_page)
        self.students_total_pages = total_pages
        
        table.setRowCount(len(students))
        
        headers = ['ID', 'First Name', 'Last Name', 'Program', 'College', 'Year', 'Gender', 'Actions']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        for row, student in enumerate(students):
            table.setItem(row, 0, QTableWidgetItem(student['id']))
            table.setItem(row, 1, QTableWidgetItem(student['firstname']))
            table.setItem(row, 2, QTableWidgetItem(student['lastname']))
            table.setItem(row, 3, QTableWidgetItem(student.get('program_name', student['program_code'])))
            table.setItem(row, 4, QTableWidgetItem(student.get('college_code', 'N/A')))
            table.setItem(row, 5, QTableWidgetItem(student['year']))
            table.setItem(row, 6, QTableWidgetItem(student['gender']))
            
            self.add_action_buttons(row)
    
        table.resizeColumnsToContents()
        table.setColumnWidth(7, 200)

        header = table.horizontalHeader()
    
        header.setSectionResizeMode(0, header.ResizeMode.Fixed)   
        header.setSectionResizeMode(4, header.ResizeMode.Fixed)   
        header.setSectionResizeMode(5, header.ResizeMode.Fixed)   
        header.setSectionResizeMode(6, header.ResizeMode.Fixed)  
        header.setSectionResizeMode(7, header.ResizeMode.Fixed)   
        
        header.setSectionResizeMode(1, header.ResizeMode.Interactive)  
        header.setSectionResizeMode(2, header.ResizeMode.Interactive) 
        
        header.setSectionResizeMode(3, header.ResizeMode.Stretch)      
        
        table.setColumnWidth(1, 100) 
        table.setColumnWidth(2, 100) 

        self.update_students_pagination()

    # ============ College Operations ============
    def sort_colleges_by_dropdown(self, sort_by):
        print(f"COLLEGE SORT CALLED: {sort_by}")
        print(f"all_colleges count: {len(self.all_colleges)}")

        sort_mapping = { 
            'College': 'name',   
        }

        key = sort_mapping.get(sort_by)
        if key:
            self.all_colleges.sort(key=lambda s: s.get(key, '').lower())
            self.colleges_page = 1
            self.load_colleges_table(refresh=False)

    def search_colleges(self, search_text):
        self.current_colleges_search_text = search_text
        self.colleges_page = 1
        self.load_colleges_table()    

    def open_add_college_dialog(self):
        dialog = AddCollegeDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_colleges_table()

    def load_colleges_table(self, refresh=True):
        table = self.dataTableColleges
        table.setSortingEnabled(False)
        table.setRowCount(0)
        
        if refresh:
            self.all_colleges = self.db_manager.get_all_colleges()
        
        self.all_colleges.sort(key=lambda c: c.get('name', '').lower())

        search_text = self.current_colleges_search_text.lower().strip()
        if search_text:
            filtered = [
                c for c in self.all_colleges
                if search_text in c['name'].lower()
                or search_text in c['code'].lower()
            ]
        else:
            filtered = self.all_colleges

        colleges, total_pages = self.get_page_data(filtered, self.colleges_page, self.colleges_per_page)
        self.colleges_total_pages = total_pages

        table.setRowCount(len(colleges))
    
        for row, college in enumerate(colleges):
            table.setItem(row, 0, QTableWidgetItem(college['name']))
            table.setItem(row, 1, QTableWidgetItem(college['code']))
        
            self.add_action_buttons_college(row, college)

        table.resizeColumnsToContents()
        table.setColumnWidth(2, 200)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch) 
        header.setSectionResizeMode(1, header.ResizeMode.Fixed)   
        header.setSectionResizeMode(2, header.ResizeMode.Fixed)  
        
        self.update_colleges_pagination()

    def add_action_buttons_college(self, row, college):
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(4, 2, 4, 2)
        button_layout.setSpacing(4)
        

        edit_btn = QPushButton("🖉 Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;  /* Emerald green */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
                
                /* Subtle shadow */
                box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
                
                /* Smooth transitions */
                transition: all 0.2s ease;
            }
            
            QPushButton:hover {
                background-color: #059669;  /* Darker emerald */
                transform: translateY(-1px);  /* Slight lift */
                box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
            }
            
            QPushButton:pressed {
                background-color: #047857;  /* Even darker */
                transform: translateY(0px);  /* Press down effect */
                box-shadow: 0 1px 2px rgba(16, 185, 129, 0.2);
            }
        """)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda checked, c=college: self.edit_college(c))
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.setStyleSheet("""
        QPushButton {
            background-color: #ef4444;  /* Bright red */
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 12px;
            
            /* Subtle shadow */
            box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
            
            /* Smooth transitions */
            transition: all 0.2s ease;
        }
        
        QPushButton:hover {
            background-color: #dc2626;  /* Darker red */
            transform: translateY(-1px);  /* Slight lift */
            box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
        }
        
        QPushButton:pressed {
            background-color: #b91c1c;  /* Even darker */
            transform: translateY(0px);  /* Press down effect */
            box-shadow: 0 1px 2px rgba(239, 68, 68, 0.2);
        }
    """)
        
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda checked, c=college: self.delete_college(c))
        
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        
        self.dataTableColleges.setCellWidget(row, 2, button_widget)
    
    def update_colleges_pagination(self):
        self.pageInfoLabelColleges.setText(
            f"Page {self.colleges_page} of {self.colleges_total_pages}"
        )
        self.prevButtonColleges.setEnabled(self.colleges_page > 1)
        self.jumpStartCollege.setEnabled(self.colleges_page > 1)

        self.nextButtonColleges.setEnabled(self.colleges_page < self.colleges_total_pages)
        self.jumpEndCollege.setEnabled(self.colleges_page < self.colleges_total_pages)
    
    def jump_to_firstcollege_page(self):
        if self.colleges_page > 1:
            self.colleges_page = 1
            self.load_colleges_table(refresh=False)
    
    def jump_to_endcollege_page(self):
         if self.colleges_page != self.colleges_total_pages:
            self.colleges_page = self.colleges_total_pages
            self.load_colleges_table(refresh=False)

    def prev_colleges_page(self):
        if self.colleges_page > 1:
            self.colleges_page -= 1
            self.load_colleges_table(refresh=False)

    def next_colleges_page(self):
        if self.colleges_page < self.colleges_total_pages:
            self.colleges_page += 1
            self.load_colleges_table(refresh=False)

    def edit_college(self, college):
        dialog = AddCollegeDialog(self.db_manager, self, college_data=college)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_colleges_table()
            self.load_programs_table()
            self.load_students_table()

    def delete_college(self, college):
        try:
            programs = self.db_manager.get_all_programs()
            programs_under_college = [p for p in programs if p['college'] == college['code']]
            
            warning_msg = f"Are you sure you want to delete {college['name']} ({college['code']})?"
            
            if programs_under_college:
                program_list = '\n'.join([f"  • {p['name']} ({p['code']})" for p in programs_under_college[:5]])
                if len(programs_under_college) > 5:
                    program_list += f"\n  • ...and {len(programs_under_college) - 5} more"
                
                warning_msg += (
                    f"\n\n⚠️  WARNING: This college has {len(programs_under_college)} program(s):"
                    f"\n{program_list}"
                    f"\n\nThese programs will be updated to have 'N/A' as their college."
                    f"\nStudents in these programs will show 'N/A' for their college."
                )
            
            warning_msg += "\n\nDo you want to continue?"
            
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                warning_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success, message = self.db_manager.delete_college(college['code'])
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_colleges_table()
                    self.load_programs_table()  
                    self.load_students_table() 
                else:
                    QMessageBox.critical(self, "Error", message)
        except Exception as e:
            print(f"Error in delete_college: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    # ============= Program Operations ===================

    def sort_programs_by_dropdown(self, sort_by):
        sort_mapping = {
            'Program': 'name',   
            'College': 'college',   
        }

        key = sort_mapping.get(sort_by)
        if key:
            self.all_programs.sort(key=lambda s: s.get(key, '').lower())
            self.programs_page = 1
            self.load_programs_table(refresh=False)
    
    def search_programs(self, search_text):
        self.current_programs_search_text = search_text
        self.students_page = 1
        self.load_programs_table()    

    def open_add_program_dialog(self):
        dialog = AddProgramDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_programs_table()
    
    def load_programs_table(self, refresh=True):
        table = self.dataTablePrograms
        table.setSortingEnabled(False)
        table.setRowCount(0)
        
        if refresh:
            self.all_programs = self.db_manager.get_all_programs()

        search_text = self.current_programs_search_text.lower().strip()
        if search_text:
            filtered = [
                p for p in self.all_programs
                if search_text in p['name'].lower()
                or search_text in p['code'].lower()
                or search_text in p['college'].lower()
            ]
        else:
            filtered = self.all_programs

        programs, total_pages = self.get_page_data(filtered, self.programs_page, self.programs_per_page)
        self.programs_total_pages = total_pages

        table.setRowCount(len(programs))
    
        for row, program in enumerate(programs):
            table.setItem(row, 0, QTableWidgetItem(program['name']))
            table.setItem(row, 1, QTableWidgetItem(program['code']))
            table.setItem(row, 2, QTableWidgetItem(program['college']))
        
            self.add_action_buttons_program(row, program)
    

        table.resizeColumnsToContents()
        table.setColumnWidth(3, 200)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch) 
        header.setSectionResizeMode(1, header.ResizeMode.Fixed)   
        header.setSectionResizeMode(2, header.ResizeMode.Fixed)   
        header.setSectionResizeMode(3, header.ResizeMode.Fixed)  

        self.update_programs_pagination()
    
    def add_action_buttons_program(self, row, program):
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(4, 2, 4, 2)
        button_layout.setSpacing(4)
        
        edit_btn = QPushButton("🖉 Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;  /* Emerald green */
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
                
                /* Subtle shadow */
                box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
                
                /* Smooth transitions */
                transition: all 0.2s ease;
            }
            
            QPushButton:hover {
                background-color: #059669;  /* Darker emerald */
                transform: translateY(-1px);  /* Slight lift */
                box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
            }
            
            QPushButton:pressed {
                background-color: #047857;  /* Even darker */
                transform: translateY(0px);  /* Press down effect */
                box-shadow: 0 1px 2px rgba(16, 185, 129, 0.2);
            }
        """)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda checked, p=program: self.edit_program(p))
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.setStyleSheet("""
        QPushButton {
            background-color: #ef4444;  /* Bright red */
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 12px;
            
            /* Subtle shadow */
            box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
            
            /* Smooth transitions */
            transition: all 0.2s ease;
        }
        
        QPushButton:hover {
            background-color: #dc2626;  /* Darker red */
            transform: translateY(-1px);  /* Slight lift */
            box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
        }
        
        QPushButton:pressed {
            background-color: #b91c1c;  /* Even darker */
            transform: translateY(0px);  /* Press down effect */
            box-shadow: 0 1px 2px rgba(239, 68, 68, 0.2);
        }
    """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda checked, p=program: self.delete_program(p))
        
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        
        self.dataTablePrograms.setCellWidget(row, 3, button_widget)
    
    def update_programs_pagination(self):
        self.pageInfoLabelPrograms.setText(
            f"Page {self.programs_page} of {self.programs_total_pages}"
        )
        self.prevButtonPrograms.setEnabled(self.programs_page > 1)
        self.jumpStartProgram.setEnabled(self.programs_page > 1)

        self.nextButtonPrograms.setEnabled(self.programs_page < self.programs_total_pages)
        self.jumpEndProgram.setEnabled(self.programs_page < self.programs_total_pages)
    
    def jump_to_firstprogram_page(self):
        if self.programs_page > 1:
            self.programs_page = 1
            self.load_programs_table(refresh=False)

    def jump_to_endprogram_page(self):
        if self.programs_page != self.programs_total_pages:
            self.programs_page = self.programs_total_pages
            self.load_programs_table(refresh=False)

    def prev_programs_page(self):
        if self.programs_page > 1:
            self.programs_page -= 1
            self.load_programs_table(refresh=False)

    def next_programs_page(self):
        if self.programs_page < self.programs_total_pages:
            self.programs_page += 1
            self.load_programs_table(refresh=False)

    def edit_program(self, program):
        dialog = AddProgramDialog(self.db_manager, self, program_data=program)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_programs_table()
            self.load_students_table()

    def delete_program(self, program):
        try:
            students = self.db_manager.get_all_students()
            students_in_program = [s for s in students if s['program_code'] == program['code']]
            
            warning_msg = f"Are you sure you want to delete {program['name']} ({program['code']})?"
            
            if students_in_program:
                student_list = '\n'.join([f"  • {s['firstname']} {s['lastname']} ({s['id']})" 
                                        for s in students_in_program[:5]])
                if len(students_in_program) > 5:
                    student_list += f"\n  • ...and {len(students_in_program) - 5} more"
                
                warning_msg += (
                    f"\n\n⚠️  WARNING: This program has {len(students_in_program)} enrolled student(s):"
                    f"\n{student_list}"
                    f"\n\nThese students will be updated to have 'N/A' as their program."
                )
            
            warning_msg += "\n\nDo you want to continue?"
            
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                warning_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success, message = self.db_manager.delete_program(program['code'])
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_programs_table()
                    self.load_students_table() 
                else:
                    QMessageBox.critical(self, "Error", message)
        except Exception as e:
            print(f"Error in delete_program: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())