# Backend Utility Scripts

## Database Setup & Management

- **`populate_db.sh`** - Populates database with initial data
- **`reset_database.sh`** - Resets entire database to initial state
- **`reset_db_standalone.py`** - Standalone Python script to reset database
- **`setup.sh`** - Initial setup script for the backend

## Question Management

- **`insert_questions.py`** - Inserts questions into database
- **`load_practice_questions.py`** - Loads practice questions from JSON
- **`load_train_questions.py`** - Loads training questions from JSON
- **`seed_test_questions.py`** - Seeds database with test questions

## Achievement System

- **`insert_achievements.py`** - Inserts achievements/badges into database
- **`reset_achievements.py`** - Resets user achievements
- **`check_badges.py`** - Checks badge status for users
- **`display_badges.py`** - Displays badge information
- **`display_icons.py`** - Displays icon information for badges

## Usage

Most scripts can be run directly from the backend directory:

```bash
# From backend/ directory
python scripts/script_name.py
# or
bash scripts/script_name.sh
```

Make sure your virtual environment is activated and environment variables are set before running these scripts.
