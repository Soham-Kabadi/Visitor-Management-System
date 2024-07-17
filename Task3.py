import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import re

# Global variable to store user information
user_info = {}

# New database names
user_db_name = 'users.db'
visitor_db_name = 'visitors.db'

# Database initialization for users
conn_users = sqlite3.connect(user_db_name)
c_users = conn_users.cursor()
c_users.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY,
              name TEXT,
              mobile TEXT,
              username TEXT,
              password TEXT)''')
conn_users.commit()

# Database initialization for visitors
conn_visitors = sqlite3.connect(visitor_db_name)
c_visitors = conn_visitors.cursor()
c_visitors.execute('''CREATE TABLE IF NOT EXISTS visitors
             (id INTEGER PRIMARY KEY,
              user_id INTEGER,
              name TEXT,
              phone TEXT,
              visited_text TEXT,
              date TEXT,
              time TEXT,
              office TEXT)''')
conn_visitors.commit()

# Admin credentials (can also be fetched from the database)
admin_username = "admin"
admin_password = "adminpass"

# Function to validate user credentials
def validate_login(username, password):
    # Check if username exists in the database
    c_users.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c_users.fetchone()

    if user:
        stored_password = user[4]
        # Hash the provided password and compare with stored hash
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_password == stored_password:
            if username == admin_username and password == admin_password:
                open_admin_dashboard()
            else:
                messagebox.showinfo("Success", "Login successful")
                user_info['name'] = user[1]
                user_info['mobile'] = user[2]
                open_user_dashboard()
        else:
            messagebox.showerror("Error", "Incorrect password")
    else:
        messagebox.showerror("Error", "Username not found")

# Function to open user login GUI
def open_user_login_gui():
    user_login_window = tk.Toplevel(main_window)
    user_login_window.title("User Login")

    # Username
    tk.Label(user_login_window, text="Username:").pack()
    username_entry = tk.Entry(user_login_window)
    username_entry.pack()

    # Password
    tk.Label(user_login_window, text="Password:").pack()
    password_entry = tk.Entry(user_login_window, show="*")
    password_entry.pack()

    # Validation function for user login
    def validate_and_login():
        # Retrieve values from input fields
        username = username_entry.get()
        password = password_entry.get()

        validate_login(username, password)

    # Login button
    login_button = tk.Button(user_login_window, text="Login", command=validate_and_login)
    login_button.pack(pady=10)

# Function to open user sign-in GUI
def open_user_signin_gui():
    user_signin_window = tk.Toplevel(main_window)
    user_signin_window.title("User Sign In")

    # Name
    tk.Label(user_signin_window, text="Name:").pack()
    name_entry = tk.Entry(user_signin_window)
    name_entry.pack()

    # Mobile Number
    tk.Label(user_signin_window, text="Mobile Number:").pack()
    mobile_entry = tk.Entry(user_signin_window)
    mobile_entry.pack()

    # Username
    tk.Label(user_signin_window, text="Username:").pack()
    username_entry = tk.Entry(user_signin_window)
    username_entry.pack()

    # Password
    tk.Label(user_signin_window, text="Password:").pack()
    password_entry = tk.Entry(user_signin_window, show="*")
    password_entry.pack()

    # Validation function for user sign-up
    def validate_and_signup():
        # Retrieve values from input fields
        name = name_entry.get()
        mobile = mobile_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        # Validate input fields
        if not (name and mobile and username and password):
            messagebox.showerror("Error", "All fields are required")
            return

        # Add user to database
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c_users.execute("INSERT INTO users (name, mobile, username, password) VALUES (?, ?, ?, ?)",
                        (name, mobile, username, hashed_password))
        conn_users.commit()
        messagebox.showinfo("Success", "User added successfully")

        # Close the sign-in window
        user_signin_window.destroy()

        # Open user login GUI after adding user
        open_user_login_gui()

    # Add user button
    add_user_button = tk.Button(user_signin_window, text="Add User", command=validate_and_signup)
    add_user_button.pack(pady=10)

def open_user_dashboard():
    # Create a new window for the user dashboard
    user_dashboard_window = tk.Toplevel(main_window)
    user_dashboard_window.title("User Dashboard")

    # Labels and Entries for user information
    tk.Label(user_dashboard_window, text="User ID No:").pack()
    user_id_entry = tk.Entry(user_dashboard_window)
    user_id_entry.pack()

    tk.Label(user_dashboard_window, text="Name:").pack()
    name_entry = tk.Entry(user_dashboard_window)
    name_entry.pack()

    tk.Label(user_dashboard_window, text="Phone Number:").pack()
    phone_entry = tk.Entry(user_dashboard_window)
    phone_entry.pack()

    tk.Label(user_dashboard_window, text="Visited Text:").pack()
    visited_text_entry = tk.Text(user_dashboard_window, wrap=tk.WORD, width=30, height=5)
    visited_text_entry.pack()

    # Date Entry
    tk.Label(user_dashboard_window, text="Date:").pack()
    date_entry = tk.Entry(user_dashboard_window)
    date_entry.pack()

    # Time Entry
    tk.Label(user_dashboard_window, text="Time:").pack()
    time_entry = tk.Entry(user_dashboard_window)
    time_entry.pack()

    # Office Name Entry
    tk.Label(user_dashboard_window, text="Office Name(s):").pack()
    office_options = ["Office 1", "Office 2", "Office 3"]  # Example options, you can modify this list as needed
    selected_offices = []
    for office in office_options:
        var = tk.IntVar()
        tk.Checkbutton(user_dashboard_window, text=office, variable=var).pack()
        selected_offices.append(var)

    # Button to submit user information
    submit_button = tk.Button(user_dashboard_window, text="Submit", command=lambda: submit_user_info(user_id_entry.get(), name_entry.get(), phone_entry.get(), visited_text_entry.get("1.0", tk.END), date_entry.get(), time_entry.get(), selected_offices, office_options))
    submit_button.pack()

def submit_user_info(user_id, name, phone, visited_text, date, time, selected_offices, office_options):
    # Convert selected offices to a comma-separated string
    selected_office_names = ','.join([office_options[i] for i, var in enumerate(selected_offices) if var.get() == 1])

    # Insert visitor information into the database
    c_visitors.execute("INSERT INTO visitors (user_id, name, phone, visited_text, date, time, office) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (user_id, name, phone, visited_text, date, time, selected_office_names))
    conn_visitors.commit()

    # Provide feedback to the user
    messagebox.showinfo("Success", "Visitor information submitted successfully.")

# Function to open admin dashboard
def open_admin_dashboard():
    admin_dashboard_window = tk.Toplevel(main_window)
    admin_dashboard_window.title("Admin Dashboard")

    # Function to fetch and display visitors
    def display_visitors():
        c_visitors.execute("SELECT * FROM visitors")
        rows = c_visitors.fetchall()
        for row in rows:
            tk.Label(admin_dashboard_window, text=row).pack()

    # Display visitors button
    display_button = tk.Button(admin_dashboard_window, text="Display Visitor", command=display_visitors)
    display_button.pack(pady=10)

    # Function to delete selected visitor
    def delete_visitor():
        selected_id = int(entry_id.get())
        c_visitors.execute("DELETE FROM visitors WHERE id=?", (selected_id,))
        conn_visitors.commit()
        messagebox.showinfo("Success", "visitor deleted successfully.")

    # Delete visitor entry
    tk.Label(admin_dashboard_window, text="Enter ID of visitor to delete:").pack()
    entry_id = tk.Entry(admin_dashboard_window)
    entry_id.pack()
    delete_button = tk.Button(admin_dashboard_window, text="Delete Visitors", command=delete_visitor)
    delete_button.pack(pady=10)

    # Back button to return to main GUI
    back_button = tk.Button(admin_dashboard_window, text="Back", command=admin_dashboard_window.destroy)
    back_button.pack(pady=10)

# Main window initialization
main_window = tk.Tk()
main_window.title("Visitor Management System")

# Admin Login button
def open_admin_login_gui():
    admin_login_window = tk.Toplevel(main_window)
    admin_login_window.title("Admin Login")

    # Username
    tk.Label(admin_login_window, text="Username:").pack()
    username_entry = tk.Entry(admin_login_window)
    username_entry.pack()

    # Password
    tk.Label(admin_login_window, text="Password:").pack()
    password_entry = tk.Entry(admin_login_window, show="*")
    password_entry.pack()

    # Validation function for admin login
    def validate_and_login():
        # Retrieve values from input fields
        username = username_entry.get()
        password = password_entry.get()

        # Placeholder validation for admin login
        if username == admin_username and password == admin_password:
            messagebox.showinfo("Success", "Admin login successful")
            open_admin_dashboard()
        else:
            messagebox.showerror("Error", "Incorrect admin credentials")

    # Login button
    login_button = tk.Button(admin_login_window, text="Login", command=validate_and_login)
    login_button.pack(pady=10)

admin_login_button = tk.Button(main_window, text="Admin Login", command=open_admin_login_gui)
admin_login_button.pack(pady=10)

# User Sign In button
user_signin_button = tk.Button(main_window, text="User Sign In", command=open_user_signin_gui)
user_signin_button.pack(pady=10)

main_window.mainloop()

# Close database connections
conn_users.close()
conn_visitors.close()