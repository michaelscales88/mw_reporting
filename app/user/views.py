from flask import render_template, flash, redirect, url_for, request, g, Blueprint
from flask_login import login_user, logout_user, login_required

from app.core import redirect_back
from app.core import get_redirect_target
from app.forms import LoginForm
from app.database import db_session

from .model import User
from app.report.core import add_client, remove_client, delete_client


bp = Blueprint('user', __name__, template_folder='templates', static_folder='static', static_url_path='/user/static')


@bp.route('/settings', methods=['GET', 'POST'])
@bp.route('/settings/', methods=['GET', 'POST'])
@login_required
def settings():
    next = get_redirect_target()
    if not g.user:
        redirect_back(
            url_for('index')
        )

    # Parser section
    g.parser.add_argument('client_name', type=str, location='form')
    g.parser.add_argument('client_id', type=str, location='form')
    g.parser.add_argument('full_service', type=bool, location='form')
    g.parser.add_argument('remove', type=str, location='form')
    g.parser.add_argument('delete', type=str, location='form')

    args = g.parser.parse_args()

    if request.method == 'POST' and args['remove']:

        user = remove_client(args['remove'])
        # Save change to session
        g.session.add(user)

    elif request.method == 'POST' and args['delete']:

        # Delete needs to be committed to be saved
        delete_client(g.session, args['delete'])

    elif request.method == 'POST':

        user = add_client(args['client_name'], args['client_id'], args['full_service'])
        # Save change to session
        g.session.add(user)

    return render_template(
        'settings_template.html',
        title='Settings',
        next=next,
        user=g.user
    )


@bp.route('/login', methods=['GET', 'POST'])
def login():

    next = get_redirect_target()
    form = LoginForm()

    if request.method == 'POST':
        if g.user and g.user.is_authenticated:
            pass
        elif form.validate_on_submit():
            email = form.login.data
            password = form.password.data
            remember = form.remember_me.data
            user = g.session.query(User).filter(User.email == email).first()

            if user:
                if user.verify_password(password):
                    # Not confident this is working as advertised
                    print('logging in remember me is', remember)
                    success = login_user(user, remember=remember)
                    flash('Login {s}.'.format(s='success!' if success else 'failed!'))

                    if next == url_for('user.login') and success:
                        next = ''

                    if not success:
                        flash('Invalid username or password.')
                else:
                    flash('Invalid username or password.')
            else:
                nickname = email.split('@')[0]
                nickname = User.make_unique_display_name(nickname)
                new_user = User(alias=nickname, email=email, password=password)
                db_session.add(new_user)
                db_session.commit()
                flash('Successfully created login for', new_user.alias)
            return redirect(next)
    return render_template(
        'login_template.html',
        title='Sign In',
        next=next,
        form=form
    )


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Successfully logged out.')
    return redirect_back(url_for('index'))
