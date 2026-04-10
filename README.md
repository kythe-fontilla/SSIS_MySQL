# Student Information System (SIS)

A robust, desktop-based management application built with Python, PyQt6, and MySQL. This system provides a comprehensive interface for managing student records, academic programs, and college departments with full CRUD capabilities and relational data integrity.

## Features

* Student Management: Full CRUD operations for student records.
* Academic Hierarchy: Manage Colleges and Programs with automatic cascading logic.
* Dynamic Search & Filtering: Real-time search across all tables and dropdown sorting.
* Custom Pagination: Handles 5,000+ records with "Jump to Start/End" functionality.
* Modern UI: Clean interface built with custom CSS and a `QStackedWidget` navigation.

## Tech Stack

* Frontend: PyQt6
* Backend: Python 3.x
* Database: MySQL (via XAMPP)
* UI Design: Qt Designer (`.ui` files)

## Project Structure
SSIS_MySQL/
├── .env.example          # Template for environment variables
├── .gitignore            # Excludes local config and venv from Git
├── config.py             # Database connection credentials (Ignored)
├── database_manager.py   # SQL query execution logic
├── main_window.ui        # UI layout file
├── main.py               # Application entry point & UI logic
├── models.py             # Data validators and lookups
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
└── ssis_backup.sql       # Database schema and 5,000 student records

## Installation & Setup

### 1. Clone the Repository
git clone https://github.com/kythe-fontilla/SSIS_MySQL.git
cd SSIS_MySQL

### 2. Install Dependencies
pip install PyQt6 mysql-connector-python


### 3. Database Configuration
1. Open MySQL Workbench and create a database named `ssis_db`.
2. Go to **Server > Data Import** and import the `ssis_backup.sql` file.

### 4. Environment Setup
Since `config.py` and `.env` are git-ignored for security:
1. Locate `.env.example`.
2. Create a new file named `.env` and copy the contents over, updating them with your local MySQL credentials.
3. Ensure your `config.py` (if used for `DB_CONFIG`) matches your local environment settings.

### 5. Run the Application
python main.py