import re
import smtplib
import dns.resolver
from email_validator import validate_email, EmailNotValidError
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Function to check email syntax
def is_valid_syntax(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Function to get MX record of the domain
def get_mx_record(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        return mx_record
    except Exception as e:
        print(f"Failed to get MX record for domain {domain}: {e}")
        return None

# Function to verify email using SMTP without sending a message
def verify_email_via_smtp(email):
    domain = email.split('@')[1]
    mx_record = get_mx_record(domain)
    if not mx_record:
        return False

    # SMTP setup
    try:
        with smtplib.SMTP(mx_record) as server:
            server.set_debuglevel(0)
            server.helo()
            server.mail('test@example.com')
            code, message = server.rcpt(email)
            server.quit()  # Disconnect from the server
            if code == 250:
                return True
            else:
                return False
    except Exception as e:
        print(f"SMTP verification failed for {email}: {e}")
        return False

# Function to validate and verify email
def validate_and_verify_email(email):
    if not is_valid_syntax(email):
        return False, "Invalid email syntax"

    try:
        # Syntax validation using email-validator library
        v = validate_email(email, check_deliverability=False)  # Disable DNS verification for now
        print(v)
        # if not v.is_valid:
        #     return False, "Invalid email syntax"
    except EmailNotValidError as e:
        return False, str(e)

    # SMTP check
    if not verify_email_via_smtp(email):
        return False, "Email failed SMTP verification"

    return True, "Email is valid and can receive messages"


# Function to process email list and save valid emails to file
def process_email_list(file_path, text_area):
    valid_emails = []
    with open(file_path, 'r') as file:
        emails = file.readlines()
    
    for email in emails:
        email = email.strip()
        if email:  # Skip empty lines
            is_valid, message = validate_and_verify_email(email)
            # result = f"Email: {email}, Valid: {is_valid}, Message: {message}\n"
            result = f"Email: {email}, Valid: {is_valid}\n\n"
            text_area.insert(tk.END, result)
            if is_valid:
                valid_emails.append(email)
    
    # Save valid emails to valid.txt
    with open('valid.txt', 'w') as valid_file:
        for valid_email in valid_emails:
            valid_file.write(valid_email + '\n')
    
    messagebox.showinfo("Process Completed", "Email verification process is completed. Valid emails saved to valid.txt.")

# Function to open file dialog and start processing
def open_file_and_process():
    file_path = filedialog.askopenfilename(title="Select Email List File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if file_path:
        text_area.delete(1.0, tk.END)  # Clear previous text
        process_email_list(file_path, text_area)
    else:
        messagebox.showwarning("No File Selected", "Please select a file to process.")

# Set up the GUI
root = tk.Tk()
root.title("Email Verifier")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

btn_open_file = tk.Button(frame, text="Select Email List File..",bg='#dcdcdc', command=open_file_and_process)
btn_open_file.pack(pady=10)

text_area = ScrolledText(frame, width=60, height=20)
text_area.pack(pady=10)

root.mainloop()
