# Sports Tournament Management System

This is a web-based Sports Tournament Management System built using **Flask** and **SQLite**. It allows tournament administrators to manage tournaments, teams, players, and matches effectively.

---

## 🧠 Features

✅ Admin Login  
✅ Create and View Tournaments  
✅ Add Teams and Players  
✅ Schedule Matches  
✅ Update Match Scores  
✅ View Team Rankings  
✅ Secure Login System with Password Hashing  
✅ REST API for Rankings (JSON format)  

---

## 🧰 Technologies Used

**Frontend:**  
- HTML  
- CSS  
- Jinja2 (Flask templating)

**Backend:**  
- Python (Flask)  
- SQLite Database  
- Werkzeug (for password hashing)

---

## 📁 Folder Structure

tournament_app/
├── app.py  
├── requirements.txt  
├── README.txt  
├── templates/  
│   ├── login.html  
│   ├── index.html  
│   ├── create_tournament.html  
│   ├── tournament_details.html  
│   ├── add_team.html  
│   ├── add_player.html  
│   └── schedule_match.html  
└── static/  
    └── style.css  

---

## 🚀 How to Run the Project

1. **Install Python and Flask**  
   Make sure you have Python installed. Then open terminal and run:

   pip install -r requirements.txt

2. **Start the Flask Application**  
   Run the app using:

   python app.py

3. **Access the App in Browser**  
   Open your browser and go to:

   http://127.0.0.1:5000

4. **Login with Admin Credentials**  
   Username: admin  
   Password: admin123  
   User Type: admin

---

## 📂 Database Info

On first run, the SQLite database `tournament.db` is automatically created with these tables:

- `users` – stores admin credentials  
- `tournaments` – stores tournament data  
- `teams` – stores team info per tournament  
- `players` – stores player info linked to teams  
- `matches` – stores scheduled match info and scores  

---

## 🧪 Testing the Features

- Create a tournament from the home page (admin only)  
- Add teams and players  
- Schedule matches between any two teams  
- Update match scores after games  
- Rankings API can be accessed at:

  /api/rankings/<tournament_id>

---

## 🔐 Default Admin Credentials

Use these to log in initially:

- Username: admin  
- Password: admin123  
- User Type: admin

You can add more users manually in the database.

---

## 📌 Note

- This is a basic version. You can add more features like live updates, player statistics, user registration, and mobile responsiveness.
- Change the `secret_key` in `app.py` before using in production.

---

## 🙌 Credits

Developed as part of the **DBMS Mini Project** for academic review.  
Technologies: Flask, SQLite, Python, HTML/CSS

---
