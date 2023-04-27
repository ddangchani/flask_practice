from flask import Blueprint, url_for, render_template, request, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from pybo import db
from pybo.models import User
from pybo.forms import UserCreateForm, UserLoginForm
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        # User db에 username이 있는지 확인
        user = User.query.filter_by(username=form.username.data).first()
        email = User.query.filter_by(email=form.email.data).first()
        if not user and not email:
            user = User(username=form.username.data, 
                        password=generate_password_hash(form.password1.data), 
                        email=form.email.data, create_date = datetime.now())
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index')) # 가입 후 메인페이지로 이동
        else:
            flash('이미 존재하는 사용자입니다.') # 별도 템플릿 필요
    return render_template('auth/signup.html', form=form)

@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = User.query.filter_by(id=user_id).first() if user_id else None


@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))