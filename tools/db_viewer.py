import sqlite3
from datetime import datetime
import os
from pathlib import Path

def connect_to_db():
    """Connect to the database"""
    db_path = Path("data/bot.db")
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return None
    return sqlite3.connect(db_path)

def format_date(date_str):
    """Format date string for better readability"""
    try:
        date = datetime.fromisoformat(date_str)
        return date.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str

def view_users():
    """View all users in the database"""
    conn = connect_to_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        # Сначала получим информацию о структуре таблицы
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print("\n=== Users ===")
        print(f"Table columns: {columns}")
        
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("\nNo users found in database")
            return
        
        print(f"\nTotal users: {len(users)}")
        print("\n" + " | ".join(columns))
        print("-" * (len(columns) * 15))
        
        for user in users:
            print(" | ".join(str(value) if value is not None else 'None' for value in user))
            
    except sqlite3.Error as e:
        print(f"Error reading users: {e}")
    finally:
        conn.close()

def view_subscriptions():
    """View all subscriptions in the database"""
    conn = connect_to_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        # Получаем структуру таблицы
        cursor.execute("PRAGMA table_info(subscriptions)")
        columns = [column[1] for column in cursor.fetchall()]
        all_columns = columns + ["username"]  # Добавляем столбец username
        
        print("\n=== Subscriptions ===")
        print(f"Table columns: {all_columns}")
        
        cursor.execute("""
            SELECT s.*, u.username 
            FROM subscriptions s
            LEFT JOIN users u ON s.user_id = u.user_id
            ORDER BY s.start_date DESC
        """)
        subscriptions = cursor.fetchall()
        
        if not subscriptions:
            print("\nNo subscriptions found in database")
            return
        
        print(f"\nTotal subscriptions: {len(subscriptions)}")
        print("\n" + " | ".join(all_columns))
        print("-" * (len(all_columns) * 15))
        
        for sub in subscriptions:
            formatted_values = []
            for i, value in enumerate(sub):
                # Проверяем, является ли поле датой (только для столбцов из основной таблицы)
                if i < len(columns) and 'date' in columns[i].lower() and value:
                    value = format_date(value)
                formatted_values.append(str(value) if value is not None else 'None')
            print(" | ".join(formatted_values))
            
    except sqlite3.Error as e:
        print(f"Error reading subscriptions: {e}")
    finally:
        conn.close()

def view_active_subscriptions():
    """View only active subscriptions"""
    conn = connect_to_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        # Получаем структуру таблицы
        cursor.execute("PRAGMA table_info(subscriptions)")
        columns = [column[1] for column in cursor.fetchall()]
        all_columns = columns + ["username"]  # Добавляем столбец username
        
        cursor.execute("""
            SELECT s.*, u.username
            FROM subscriptions s
            LEFT JOIN users u ON s.user_id = u.user_id
            WHERE s.is_active = 1
            AND s.end_date > datetime('now')
            ORDER BY s.end_date ASC
        """)
        subscriptions = cursor.fetchall()
        
        if not subscriptions:
            print("\nNo active subscriptions found")
            return
        
        print("\n=== Active Subscriptions ===")
        print(f"Total active: {len(subscriptions)}")
        print("\n" + " | ".join(all_columns))
        print("-" * (len(all_columns) * 15))
        
        for sub in subscriptions:
            formatted_values = []
            for i, value in enumerate(sub):
                # Проверяем, является ли поле датой (только для столбцов из основной таблицы)
                if i < len(columns) and 'date' in columns[i].lower() and value:
                    value = format_date(value)
                formatted_values.append(str(value) if value is not None else 'None')
            print(" | ".join(formatted_values))
            
    except sqlite3.Error as e:
        print(f"Error reading active subscriptions: {e}")
    finally:
        conn.close()

def main():
    """Main menu for database viewer"""
    while True:
        print("\n=== Database Viewer ===")
        print("1. View all users")
        print("2. View all subscriptions")
        print("3. View active subscriptions")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            view_users()
        elif choice == "2":
            view_subscriptions()
        elif choice == "3":
            view_active_subscriptions()
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()