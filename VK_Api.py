import argparse
import os
import pathlib
import sys
from getpass import getpass
import requests

request_pattern = "https://api.vk.com/method/{0}?{1}&access_token={2}&v=5.131"


def info_about_user(user, vk_token):
    try:
        user_info = requests.get(request_pattern.format("users.get",
                                                        f"user_ids={user}&fields=city,education,bdate,is_friend,online",
                                                        vk_token)).json()['response'][0]
        print("Имя: ", user_info['first_name'])
        print("Фамилия: ", user_info['last_name'])
        bdate = user_info.get('bdate')
        if not bdate:
            bdate = '-'
        university = user_info.get('university_name')
        if not university:
            university = '-'
        city = user_info.get("city")
        if city:
            city = city.get("title")
        else:
            city = '-'
        is_friend = user_info.get("is_friend")
        if is_friend:
            is_friend = "является вашим другом"
        else:
            is_friend = "не является вашим другом"
        status_online = user_info.get("online")
        if status_online:
            status_online = "онлайн"
        else:
            status_online = "оффлайн"
        print("Дата рождения: ", bdate)
        print("Город: ", city)
        print("Образование: ", university)
        print("Статус дружбы: ", is_friend)
        print("Онлайн/оффлайн: ", status_online)
    except requests.exceptions.ConnectionError:
        sys.exit("Проверьте подключение к интернету.")
    except KeyError:
        sys.exit("Проверьте правильность введенных параметров.")


def get_user_photos(user, vk_token):
    try:
        user_info = requests.get(request_pattern.format("users.get",
                                                        f"user_ids={user}&fields=city", vk_token)).json()['response'][0]
        path = user_info['first_name'] + ' ' + user_info['last_name']
        if not os.path.exists(path):
            p = pathlib.Path(path)
            p.mkdir(parents=True)
        request = requests.get(request_pattern.format("photos.get", f"owner_id={user}&album_id=profile", vk_token))
        response = request.json()['response']
        count = 1
        for item in response['items']:
            photos = item['sizes']
            photo = photos[len(photos) - 1]
            image_link = photo['url']
            try:
                filename = user_info['first_name'] + "(" + str(count) + ")" + ".jpeg"
                img = requests.get(image_link).content
                with(open(path + '/' + filename, 'wb')) as file:
                    file.write(img)
                count += 1
            except():
                print("Не удалось скачать изображение: ", image_link)
    except requests.exceptions.ConnectionError:
        sys.exit("Проверьте подключение к интернету.")
    except KeyError:
        sys.exit("Проверьте правильность введенных параметров.")


def get_user_friends(user, vk_token):
    try:
        request = requests.get(request_pattern.format("friends.get", f"user_id={user}&order=hints", vk_token))
        response = request.json()['response']
        friend_request = requests.get(
            request_pattern.format("users.get", f"user_ids={response['items']}&fields=city", vk_token))
        friend_response = friend_request.json()['response']
        print("-" * 59)
        print_raw("Имя", "Фамилия", "Город")
        for friend_info in friend_response:
            first_name = friend_info['first_name']
            last_name = friend_info['last_name']
            city = friend_info.get("city")
            if city:
                city = city.get("title")
            else:
                city = '-'
            print_raw(first_name, last_name, city)
    except requests.exceptions.ConnectionError:
        sys.exit("Проверьте подключение к интернету.")
    except KeyError:
        sys.exit("Проверьте правильность введенных параметров.")


def print_raw(first_name, last_name, city):
    print(
        f"| {first_name}{' ' * (14 - len(first_name))}| {last_name}{' ' * (19 - len(last_name))}"
        f"| {city}{' ' * (19 - len(city))}|")
    print("-" * 59)


def main():
    script_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        usage=f'{script_name} [OPTIONS] USER_ID',
        description='using the vk api',
    )
    parser.add_argument(
        '-f', "--friends", dest="friends", action='store_true', help="Displays a list of the user's friends"
    )
    parser.add_argument(
        '-p', "--photos", dest="photos", action='store_true', help="Downloads user profile photos"
    )
    parser.add_argument(
        '-i', "--info", dest="info", action='store_true', help="Displays brief information about the user"
    )
    parser.add_argument('user_id',
                        help='The digital id of the user with whom the action is performed')
    args = parser.parse_args()

    if not (args.friends or args.photos or args.info):
        sys.exit("Не все параметры введены. Используйте help, чтобы уточнить список параметров.")

    token = getpass("Введите access token vk: ")
    if not token:
        sys.exit("Access token vk не был введен.")
    try:
        if args.friends:
            get_user_friends(args.user_id, token)
        if args.photos:
            get_user_photos(args.user_id, token)
        if args.info:
            info_about_user(args.user_id, token)
    except Exception as e:
        sys.exit(e)


if __name__ == '__main__':
    main()
