from django.shortcuts import render, redirect
from .models import PredictionLog
from .forms import LogEntryForm
import requests
import csv
from django.http import HttpResponse
from dotenv import load_dotenv
import os
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
import json



HUGGINGFACE_API_KEY = "hf_xxxxxxxxxxxxxxxxxxxxxxxxx"


def get_intent_from_huggingface(text):
    url = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
        "X-Task": "zero-shot-classification"
    }

    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": ["command", "question", "statement"]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200 or not response.text.strip():
            return "unknown"

        output = response.json()

        # ✅ HF gives list of {label, score}
        if isinstance(output, list):
            top = max(output, key=lambda x: x["score"])
            return top["label"]

    except Exception as e:
        print("Intent Exception:", e)

    return "unknown"


  


def get_tone_from_huggingface(text):
    url = "https://router.huggingface.co/hf-inference/models/cardiffnlp/twitter-roberta-base-sentiment"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

    label_map = {
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive"
    }

    try:
        response = requests.post(url, headers=headers, json={"inputs": text}, timeout=20)

        if response.status_code != 200:
            print("HF Tone HTTP Error:", response.status_code, response.text)
            return "Unknown"

        if not response.text.strip():
            print("HF Tone Empty Response")
            return "Unknown"

        result = response.json()
        print("HF Tone Response:", result)

        if isinstance(result, list) and len(result) > 0:
            top = max(result[0], key=lambda x: x["score"])
            return label_map.get(top["label"], "Unknown")

    except Exception as e:
        print("HF Tone Exception:", e)

    return "Unknown"



# Home View
def home(request):
    form = LogEntryForm() # It's used to accept text input from the user.

    # For storing/showing Django’s session framework(session)
    session_logs = request.session.get('temp_logs', [])  # Checks if there's a temp_logs list already in session (for non-logged-in users). If not found, returns an empty list.

    if request.method == 'POST':
        form = LogEntryForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            intent = get_intent_from_huggingface(text)
            tone = get_tone_from_huggingface(text)

            if request.user.is_authenticated:
                #  Save in DB for logged-in users
                PredictionLog.objects.create(text=text, intent=intent, tone=tone, user=request.user)
                return redirect('home')
            else:
                #  Store in session for guest user
                entry = {
                    'text': text,
                    'intent': intent,
                    'tone': tone
                }
                session_logs.insert(0, entry)  # first
                request.session['temp_logs'] = session_logs[:5]  # only keep 5 latest
                request.session.modified = True
                return redirect('home')

    # save history
    if request.user.is_authenticated:
        logs = PredictionLog.objects.filter(user=request.user).order_by('-timestamp') # Fetches all predictions saved in the database for the current user
    else:
        # Show session-stored logs (not saved in DB)
        logs = session_logs

    return render(request, 'home.html', {
        'form': form,
        'logs': logs
    })



# Signup Page

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created and logged in successfully.')
            return redirect('login')
    else:
        form = SignUpForm() # It's a form that allows users to create a new account by entering their username, email, and password.
    return render(request, 'signup.html', {'form': form}) # Renders the signup page with the signup form.

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv') # Sets the content type to 'text/csv' so the browser knows it's a CSV file.
    response['Content-Disposition'] = 'attachment; filename="your_predictions.csv"' # Sets the filename for the downloaded file.
    # This is an HTTP header. (Content-Disposition) It tells the browser how to handle the response.
    # The content is a file, not a page. So, the browser should open a download dialog box. (attachment) and the filename is set to "your_predictions.csv".

    writer = csv.writer(response) # Creates a CSV writer object that will write to the response object.
    writer.writerow(['Text', 'Intent', 'Tone', 'Timestamp']) # Writes the header row to the CSV file.

    user_logs = PredictionLog.objects.filter(user=request.user).order_by('-timestamp') # Fetches all logs for the logged-in user, ordered by timestamp (most recent first).
    for log in user_logs:
        writer.writerow([log.text, log.intent, log.tone, log.timestamp]) # Writes each log entry as a row in the CSV file.

    return response

# History Page
@login_required
def history(request):
    user_logs = PredictionLog.objects.filter(user=request.user).order_by('-timestamp') # Fetches all logs for the logged-in user, ordered by timestamp (most recent first).
    return render(request, 'history.html', {'history': user_logs})

# Graph Page
@login_required(login_url='login')
def graph(request):
    from django.db.models import Count

    # Only use current user's data
    data = PredictionLog.objects.filter(user=request.user).values('tone').annotate(total=Count('tone')) # Groups the logs by tone and counts how many times each tone appears.

    # used together to perform group by and aggregation operations (values,annotate)

    labels = [entry['tone'] for entry in data] # Extracts the tone labels from the data.
    values = [entry['total'] for entry in data] # Extracts the counts for each tone.

    return render(request, 'graph.html', { 
        'labels': json.dumps(labels), # Converts the labels to a JSON string for use in JavaScript.
        'values': json.dumps(values) 
    })


# About Page
def about(request):
    return render(request, 'about.html')


#Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')

def terms(request):
    return render(request, 'terms.html')
