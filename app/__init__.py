import requests
from flask import Flask, render_template, redirect, url_for, flash, request, session, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Playlist
from app.forms import LoginForm, RegisterForm, PlaylistForm
from app.managers import PlaylistManager

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1/'
SPOTIFY_CLIENT_ID = '127c5312a7b643e0878768ac7c353cbc'
SPOTIFY_CLIENT_SECRET = 'f04cb897ab354e2aa31b2a79665894a8'
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/spotify-auth')
def spotify_auth():
    scope = 'playlist-modify-public playlist-modify-private'
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={SPOTIFY_CLIENT_ID}&scope={scope}&redirect_uri={SPOTIFY_REDIRECT_URI}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    auth_response = requests.post(SPOTIFY_TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    })

    auth_response.raise_for_status()
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    refresh_token = auth_response_data['refresh_token']

    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user_response.raise_for_status()
    spotify_user_id = user_response.json()['id']

    session['access_token'] = access_token
    session['refresh_token'] = refresh_token

    pl_manager = PlaylistManager(access_token)
    name, playlist_url = pl_manager.curate_playlist(spotify_user_id, session['mood'], session['goal'])
    new_playlist = Playlist(name=name, url=playlist_url, user_id=current_user.id)
    db.session.add(new_playlist)
    db.session.commit()
    return redirect(url_for('playlist_loader'))


#region Login Req. Routes
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', playlists=playlists)


@app.route('/playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()
    if form.validate_on_submit():
        mood = form.mood.data
        goal = form.goal.data

        session['goal'] = goal
        session['mood'] = mood

        return redirect(url_for('spotify_auth'))
    return render_template('playlist.html', form=form)


@app.route('/playlist_loader')
@login_required
def playlist_loader():
    return render_template('loader.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


#endregion Login Req. Routes


#region Error Handlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

#endregion
