from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# API details
API_URL = "https://jsearch.p.rapidapi.com/search"
HEADERS = {
    'X-RapidAPI-Host': 'jsearch.p.rapidapi.com',
    'X-RapidAPI-Key': '252254af6bmsh8a4e6b440d08486p165dcdjsn4f30ef75bbdc'  # Replace with your actual RapidAPI key
}

# Preset credentials
PRESET_USERNAME = 'farhana'
PRESET_PASSWORD = 'password'

# Temporary in-memory storage for applications
applications = {}

# ✅ Route: Index (Login Page)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == PRESET_USERNAME and password == PRESET_PASSWORD:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('job_board'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('index.html')

# ✅ Route: Sign Up Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        flash('This app has preset credentials. Please use username: farhana and password: password to log in.', 'info')
        return redirect(url_for('index'))
    return render_template('signup.html')

# ✅ Route: Job Board (with API Integration)
@app.route('/job_board', methods=['GET', 'POST'])
def job_board():
    if request.method == 'POST':
        query = request.form.get('query', 'developer')
        location = request.form.get('location', 'US')
    else:
        query = 'developer'
        location = 'US'

    # API call to fetch job listings
    response = requests.get(
        API_URL,
        headers=HEADERS,
        params={"query": query, "location": location, "num_pages": 3}
    )

        # Check if the response is successful and extract job listings
    if response.status_code == 200:
        jobs = response.json().get('data', [])
        for job in jobs:
            # Extract location
            job['location'] = f"{job.get('job_city', '')}, {job.get('job_state', '')}, {job.get('job_country', '')}"
            # Handle missing location
            if job['location'].strip(', ') == ", , ":
                job['location'] = "Not specified"

            # Extract salary
            if job.get('job_min_salary') and job.get('job_max_salary'):
                job['salary'] = f"${job['job_min_salary']} - ${job['job_max_salary']}"
            else:
                job['salary'] = "Not specified"
    else:
        jobs = []

    return render_template('job_board.html', jobs=jobs)

# ✅ Route: Application Tracker
@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    username = session.get('username')
    if not username:
        flash('Please log in to access your application tracker.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        job_title = request.form.get('job_title')
        company_name = request.form.get('company_name')
        status = request.form.get('status')
        notes = request.form.get('notes')

        if username not in applications:
            applications[username] = []

        applications[username].append({
            'job_title': job_title,
            'company_name': company_name,
            'status': status,
            'notes': notes
        })
        flash('Job application added!', 'success')

    user_applications = applications.get(username, [])
    return render_template('tracker.html', applications=user_applications)

# ✅ Route: Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)





