from .model import User


def existing_user(session, args):
    return session.query(User).filter(User.email == args['user_name']).first()


def new_user(args):
    nickname = args['user_name'].split('@')[0]
    nickname = User.make_unique_display_name(nickname)
    return User(alias=nickname, email=args['user_name'], password=args['password'])

