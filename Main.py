import csv
import json
import urllib.request
import hashlib  

file_path = 'regno.csv'

def store_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored_password, entered_password):
    return stored_password == hashlib.sha256(entered_password.encode()).hexdigest()

def load_users(file_path):
    users = {}
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users[row['email']] = {
                    'password': row['password'],
                    'security_question': row['security_question'],
                    'answer': row['answer'].lower()
                }
    except FileNotFoundError:
        print("User data file not found. Creating a new one...")
    return users

def update_csv(file_path, users):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['email', 'password', 'security_question', 'answer'])
        for email, details in users.items():
            writer.writerow([email, details['password'], details['security_question'], details['answer']])

def register(users):
    email = input("Enter your email: ")
    if email in users:
        print("User already exists.")
        return
    password = input("Enter your password (at least 8 characters with uppercase, lowercase, digit, and special character): ")
    if not validate_password(password):
        print("Password does not meet security requirements.")
        return
    stored_password = store_password(password)
    security_question = input("Enter a security question: ")
    answer = input("Enter the answer to your security question: ")
    users[email] = {
        'password': stored_password,
        'security_question': security_question,
        'answer': answer.lower()
    }
    update_csv(file_path, users)
    print("Registration successful!")

def validate_password(password):
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return has_upper and has_lower and has_digit and has_special

def login(users):
    attempts = 0
    MAX_ATTEMPTS = 5

    while attempts < MAX_ATTEMPTS:
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        
        if email in users and check_password(users[email]['password'], password):
            print("Login successful!")
            return True
        
        attempts += 1
        print(f"Invalid credentials. {MAX_ATTEMPTS - attempts} attempts left.")
    
    print("Too many failed login attempts.")
    return False    

def forgot_password(users):
    email = input("Enter your registered email: ")
    if email in users:
        answer = input(f"Security question: {users[email]['security_question']}\nAnswer: ")
        if answer.lower() == users[email]['answer']:
            new_password = input("Enter your new password: ")
            if not validate_password(new_password):
                print("Password does not meet security requirements.")
                return
            users[email]['password'] = store_password(new_password)
            update_csv(file_path, users)
            print("Password reset successful!")
        else:
            print("Incorrect answer.")
    else:
        print("Email not found.")

def search_books(query, search_type='title'):
    base_url = "https://openlibrary.org/search.json?"

    encoded_query = urllib.parse.quote(query)

    if search_type == 'title':
        url = base_url + f"title={encoded_query}"
    elif search_type == 'author':
        url = base_url + f"author={encoded_query}"
    elif search_type == 'isbn':
        url = base_url + f"isbn={encoded_query}"
    else:
        print("Invalid search type.")
        return

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            books = json.loads(data)

            if 'docs' in books and books['docs']:
                for book in books['docs'][:5]: 
                    title = book.get('title', 'Unknown Title')
                    authors = ", ".join(book.get('author_name', ['Unknown Author']))
                    first_publish_year = book.get('first_publish_year', 'Unknown Year')
                    isbn_list = book.get('isbn', ['Unknown ISBN'])
                    isbn = isbn_list[0] if isbn_list else 'Unknown ISBN'

                    print(f"Title: {title}")
                    print(f"Author(s): {authors}")
                    print(f"First Published: {first_publish_year}")
                    print(f"ISBN: {isbn}")
                    print("-" * 40)
            else:
                print("No books found.")
    except Exception as e:
        print("Error fetching data from OpenLibrary:", e)

def main():
    users = load_users(file_path)
    
    while True:
        print("1. Register")
        print("2. Login")
        print("3. Forgot Password")
        print("4. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            register(users)
        elif choice == '2':
            if login(users):
                query = input("Enter the book title/author/ISBN: ")
                search_type = input("Search by (title/author/isbn): ").lower()
                search_books(query, search_type)
        elif choice == '3':
            forgot_password(users)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
