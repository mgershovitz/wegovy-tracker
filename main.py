from flask import Flask, request, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request
from functools import wraps
import os
from datetime import timedelta
import db_deepseek, db_chatgpt
from db_claude import NotionSyringeManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

# Custom decorator for protected routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip token check for login route
        if request.path == '/login':
            return f(*args, **kwargs)
            
        try:
            # Try to verify JWT token
            verify_jwt_in_request()
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
        
        # Validate credentials (use a secure method in production)
        if username == os.environ.get('AUTH_USERNAME') and \
           password == os.environ.get('AUTH_PASSWORD'):
            # Create access token
            access_token = create_access_token(identity=username)
            
            # Return a page that sets the token in localStorage and redirects
            return render_template('auth_success.html', token=access_token)
        else:
            return render_template('login.html', error="Invalid credentials")
    
    # GET request - show login form
    return render_template('login.html')

app.route('/')
@token_required
def deepseek():
    print("Successfully authenticated, rendering index page")

    remaining = db_deepseek.GetSyringe()
    total=6.8

    # Render the HTML page current syringe status
    return render_template("tracker-deepseek.html", remaining=remaining, total=total)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)