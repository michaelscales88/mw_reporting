from flask_login import current_user
from .model import User, ClientTable, ManagerClientLink


def existing_user(session, args):
    return session.query(User).filter(User.email == args['user_name']).first()


def new_user(args):
    nickname = args['user_name'].split('@')[0]
    nickname = User.make_unique_display_name(nickname)
    return User(alias=nickname, email=args['user_name'], password=args['password'])


def add_client(client_name, client_id, full_service):
    new_client = ClientTable(client_name=client_name, client_id=client_id, full_service=full_service)
    current_user.add_client(new_client)
    return current_user


def remove_client(row_id):
    client = ClientTable.query.get(row_id)
    current_user.remove_client(client)
    return current_user


def delete_client(session, row_id):
    client = ClientTable.query.get(row_id)
    manager_count = session.query(ManagerClientLink).with_parent(client, 'users').count()
    print(manager_count)
    if manager_count == 0:
        # ClientTable.query.filter(ClientTable.id == row_id).delete()
        client.delete()
    else:
        print('Managers exist')
        # Check if they want to proceed
        # Remove all the relationships
        # ClientTable.query.filter(ClientTable.id == row_id).delete()
