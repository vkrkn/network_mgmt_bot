import argparse
from app.models.base_model import User, Role

parser = argparse.ArgumentParser(description='Интерфейс управления flink_mgmt_bot')
parser.add_argument('-s', '--show', choices=['users'])
parser.add_argument('-m', '--modify', choices=['users'])
parser.add_argument('-r', '--roles')
parser.add_argument('-u', '--user')

args = parser.parse_args()

if vars(args).get('show'):
    if vars(args).get('user'):
        user = User.get_or_none(telegram_id=args.user)
        if user is None:
            print("Неудалось найти пользователя")
            exit()

        print(f"{user.id}\t{user.name}\t{user.telegram_id}\t{user.role}")
    else:
        users = User.select()
        print("id\tusername\ttelegram_id\troles")
        print("----------------------------------------------------------")
        for user in users:
            print(f"{user.id}\t{user.name}\t{user.telegram_id}\t{user.role}")
elif vars(args).get('modify'):
    if not vars(args).get('user'):
        print('укажите пользователя: --user 123456789')
        exit()

    if not vars(args).get('roles'):
        print('укажите роль: --roles')
        exit()

    user = User.get_or_none(telegram_id=args.user)
    if user is None:
        print("Не удалось найти пользователя")
        exit()

    role = Role.get_or_none(id=args.roles)
    if role is None:
        print('Не удалось найти роль')
        exit()

    user.role = role
    user.save()
    print('Успешно!')

else:
    parser.print_help()
