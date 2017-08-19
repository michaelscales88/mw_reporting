from collections import OrderedDict


def menu():
    manager = DbManager()
    manager.from_object(default_config.Config)
    manager.base = Base
    commands = OrderedDict(
        [
            ('Create DB', manager.create),
            ('Upgrade DB', manager.upgrade),
            ('Downgrade DB', manager.downgrade),
            ('Migrate DB', manager.migrate),
            ('Quit', '')
        ]
    )
    idx_choices = list(enumerate(commands.keys()))
    while True:
        idx_choice = int(input(idx_choices))
        cmd = idx_choices[idx_choice][1]
        exc_cmd = commands[cmd]
        if exc_cmd:
            exc_cmd()
        else:
            break

if __name__ == '__main__':
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    from app import default_config
    from app.database import Base
    from .db_manager import DbManager
    menu()
