# 💰 Expense Tracker Web Application

A simple and intuitive web application to track your daily expenses, manage your budget, and gain insights into your spending habits.

## 📝 Features

- ✅ User Authentication (Login/Logout)
- 💳 Add & Categorize Expenses
- 📅 View Expense History by Date or Category
- 📊 Budget Planning Tools
- 🧱 Built with Flask, SQLite, and SQLAlchemy
- 🎨 Clean and Responsive User Interface

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS (custom + Bootstrap)
- **Database**: SQLite (default), PostgreSQL-compatible (via psycopg2-binary)
- **ORM**: SQLAlchemy
- **Form Handling**: Flask-WTF
- **User Management**: Flask-Login

## 📦 Requirements

Install the following Python packages:

```bash
pip install -r requirements.txt
```

**requirements.txt**
```
Flask
Flask-Login
Flask-SQLAlchemy
Flask-WTF
email-validator
psycopg2-binary
```

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker
```

### 2. Set Up Virtual Environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python main.py
```

Then open your browser and navigate to `http://127.0.0.1:5000`.

## 🗃️ Folder Structure

```
ExpenseTracker/
├── app.py
├── main.py
├── models.py
├── routes.py
├── forms.py
├── utils.py
├── templates/
│   └── *.html
├── static/
│   └── css/
│       └── custom.css
│   └── js/
│       └── charts.js
│       └── main.js
├── requirements.txt
```

## 📷 Screenshots

![image](https://github.com/user-attachments/assets/bfaaf3cd-c0ac-4544-8377-7ef30e79a2f1)
![image](https://github.com/user-attachments/assets/fb7fb5b3-9164-4465-a14a-804e2396c1cd)
![image](https://github.com/user-attachments/assets/3e00bef8-44f2-4fe8-a7dc-d37b32741d9b)
![image](https://github.com/user-attachments/assets/eca5915b-8746-47a9-bab7-fb7daebc3a55)


## 📬 Contact

**Developer:** Faizan Manazir  
📧 Email: faizanmanazir075@gmail.com

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
