from flask import Flask, request, render_template, redirect, url_for, make_response
from functools import wraps
import os
from datetime import datetime, timedelta
import jwt

import db_deepseek  

app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY')

# Custom decorator for protected routes
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip token check for login route
        if request.path == '/login':
            return f(*args, **kwargs)
        
        token = request.cookies.get('auth_token')
        if not token:
            print("No token cookie found")
            return redirect(url_for('login'))
            
        try:
            # Verify token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # If we get here, token is valid
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Token verification failed: {str(e)}")
            return redirect(url_for('login'))
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == os.environ.get('AUTH_USERNAME') and \
           password == os.environ.get('AUTH_PASSWORD'):
            
            # Create token
            payload = {
                'user': username,
                'exp': datetime.utcnow() + timedelta(days=30)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            
            # Create response with cookie
            response = make_response(redirect(url_for('index')))
            response.set_cookie('auth_token', token, httponly=True, max_age=30*24*60*60)  # 30 days
            
            return response
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/')
@login_required
def index():

    remaining = db_deepseek.GetSyringe()
    total=6.8

    # Render the HTML page current syringe status
    return render_template("tracker-deepseek.html", remaining=remaining, total=total)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)