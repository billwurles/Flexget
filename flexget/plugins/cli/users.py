from __future__ import unicode_literals, division, absolute_import

from flexget import options, plugin
from flexget.event import event
from flexget.logger import console
from flexget.utils.database import with_session

try:
    from flexget.webserver import User, generate_key, get_users, user_exist, add_user, delete_user, change_password, \
        generate_token
except ImportError:
    raise plugin.DependencyError(issued_by='cli_series', missing='webserver',
                                 message='Users commandline interface not loaded')


@with_session
def do_cli(manager, options, session=None):
    if hasattr(options, 'user'):
        options.user = options.user.lower()

    if options.action == 'list':
        users = get_users(session=session)
        if users:
            max_width = len(max([user.name for user in users], key=len)) + 4
            console('_' * (max_width + 56 + 9))
            console('| %-*s | %-*s |' % (max_width, 'Username', 56, 'API Token'))
            if users:
                for user in users:
                    console('| %-*s | %-*s |' % (max_width, user.name, 56, user.token))
        else:
            console('No users found')

    if options.action == 'add':
        exists = user_exist(name=options.user, session=session)
        if exists:
            console('User %s already exists' % options.user)
            return
        user = add_user(name=options.user, password=options.password)
        console('Added %s to the database with generated API Token: %s' % (user.name, user.token))

    if options.action == 'delete':
        user = user_exist(name=options.user, session=session)
        if not user:
            console('User %s does not exist' % options.user)
            return
        delete_user(user=user, session=session)
        console('Deleted user %s' % options.user)

    if options.action == 'passwd':
        user = user_exist(name=options.user, session=session)
        if not user:
            console('User %s does not exist' % options.user)
            return
        change_password(user_name=user.name, password=options.password, session=session)
        console('Updated password for user %s' % options.user)

    if options.action == 'gentoken':
        user = user_exist(name=options.user, session=session)
        if not user:
            console('User %s does not exist' % options.user)
            return
        user = generate_token(user=user, session=session)
        console('Generated new token for user %s' % user.name)
        console('Token %s' % user.token)


@event('options.register')
def register_parser_arguments():
    parser = options.register_command('users', do_cli, help='Manage users providing access to the web server')
    subparsers = parser.add_subparsers(dest='action', metavar='<action>')

    subparsers.add_parser('list', help='List users')

    add_parser = subparsers.add_parser('add', help='add a new user')
    add_parser.add_argument('user', metavar='<username>', help='Users login')
    add_parser.add_argument('password', metavar='<password>', help='Users password')

    del_parser = subparsers.add_parser('delete', help='delete a new user')
    del_parser.add_argument('user', metavar='<username>', help='Login to delete')

    pwd_parser = subparsers.add_parser('passwd', help='change password for user')
    pwd_parser.add_argument('user', metavar='<username>', help='User to change password')
    pwd_parser.add_argument('password', metavar='<new password>', help='New Password')

    gentoken_parser = subparsers.add_parser('gentoken', help='Generate a new api token for a user')
    gentoken_parser.add_argument('user', metavar='<username>', help='User to regenerate api token')
