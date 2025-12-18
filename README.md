# FlexiBrain 🧠

FlexiBrain is an AI-powered Django web application that analyzes user input to detect **intent** (command, question, statement) and **tone** (positive, neutral, negative) using Hugging Face NLP models.

The project is designed with clean architecture, safe API handling, and beginner-friendly implementation, making it suitable for academic projects and learning purposes.

---

## 🚀 Features

- Zero-shot intent detection (command / question / statement)
- Sentiment (tone) analysis (positive / neutral / negative)
- User authentication (signup, login, logout)
- Prediction history stored in database
- Graph-based analytics
- CSV export of predictions
- Secure handling of API keys using environment variables

---

## 🛠️ Tech Stack

- Python
- Django
- Hugging Face Inference API
- HTML, CSS, Bootstrap
- SQLite

---

## ▶️ How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/FlexiBrain.git
   
2. Go to project folder:
   
cd FlexiBrain/frontend/flexibrain

4. Install dependencies:
   
pip install -r requirements.txt

4.Create and add in views.py:

HUGGINGFACE_API_KEY=your_api_key_here


Run the project:

python manage.py migrate

python manage.py runserver


Open browser:

http://127.0.0.1:8000/

🧪 Sample Inputs

How are you?
Turn off the fan
I am very happy today
