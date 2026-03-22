# Expiry Tracker

Expiry Tracker is a web application that helps users track and manage the expiry dates of items such as food, medicines, cosmetics, and important documents. It provides timely reminders and a clear overview to prevent waste and improve organization.


## Features

-  User Authentication (Register & Login)
-  Add items with expiry date and reminder
-  Dashboard with item statistics
-  View items with status (Safe, Due Soon, Expiring Soon, Expired)
-  Calendar view for expiry tracking
-  Email notifications before expiry
-  Search and filter functionality
-  Delete items with confirmation
  

## Technologies Used

### Backend
- Python
- Flask
- SQLite

### Frontend
- HTML5
- Bootstrap 5
- JavaScript
- jQuery

### Libraries & Tools
- SweetAlert2 (alerts)
- FullCalendar.js (calendar UI)
- SMTP (email notifications)



## Project Structure

```
expiry-tracker/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── items.html
│   ├── calendar.html
│   ├── login.html
│   └── register.html
├── app.py
├── database.db
└── README.md
```



## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/expiry-tracker.git
cd expiry-tracker
```

### 2. (Optional) Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install flask
```

### 4. Run the Application
```bash
python app.py
```

### 5. Open in Browser
```
http://127.0.0.1:5000
```





## Email Configuration

To enable email alerts:

1. Enable **2-Step Verification** in your Gmail account  
2. Generate a **Google App Password**  
3. Replace credentials in `app.py`:

```python
sender = "your-email@gmail.com"
password = "your-app-password"
```


## Future Improvements

- Mobile app version  
- Advanced analytics dashboard  
- AI-based expiry prediction  




## Author

Tanusha Musunuru

---

