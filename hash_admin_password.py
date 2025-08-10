from werkzeug.security import generate_password_hash
import mysql.connector

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "8423"
DB_NAME = "campusbites"

def hash_password_for_admin(username, new_password):
    """Hashes a password and updates it in the database for a given admin username."""
    hashed_password = generate_password_hash(new_password)
    
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE admin_users SET password = %s WHERE username = %s",
            (hashed_password, username)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Successfully updated password for admin: '{username}'.")
            print("You can now log in with the new password.")
        else:
            print(f"Error: Admin user '{username}' not found.")
            
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    admin_username = input("Enter the admin username to update: ")
    password_to_hash = input(f"Enter the new password for '{admin_username}': ")
    hash_password_for_admin(admin_username, password_to_hash)