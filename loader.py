import json
import os

import requests
from tqdm import trange

from connect import vk


def load_group(group_id):
    group_id = str(vk.groups.getById(group_id=group_id)[0]["id"])
    group_id = '-' + group_id
    group_path = "groups/{}".format(group_id)
    if os.path.isdir(group_path):
        return 200
    os.mkdir(group_path)
    albums = vk.photos.getAlbums(owner_id=group_id)
    album_ids = [album["id"] for album in albums["items"]]
    album_titles = [album["title"] for album in albums["items"]]
    albums = []
    for album_id, album_title in zip(album_ids, album_titles):
        photos = vk.photos.get(owner_id=group_id, album_id=album_id)
        photos_from_album = []
        for photo in photos["items"]:
            photos_from_album.append(photo["sizes"][-3]["url"])
        albums.append((photos_from_album, album_title.replace('/', '_')))
    for album in albums:
        if not os.path.isdir("{}/{}".format(group_path, album[1])):
            os.mkdir("{}/{}".format(group_path, album[1]))
        for idx in trange(len(album[0])):
            photo_request = requests.get(album[0][idx])
            if photo_request.status_code == 200:
                with open("{}/{}/{}.jpg".format(group_path, album[1], idx), 'wb') as f:
                    for chunk in photo_request.iter_content(1024):
                        f.write(chunk)
    return 200


def load_users(group_id):
    group_id = vk.groups.getById(group_id=group_id)[0]["id"]
    with open("users/loaded_groups.json", 'r') as fp:
        loaded = json.load(fp)
    if group_id in loaded:
        return 200
    loaded.append(group_id)
    with open("users/loaded_groups.json", 'w') as fp:
        json.dump(loaded, fp)
    users = []  # список словарей с инфой об участниках
    i = 0
    new_users = vk.groups.getMembers(group_id=group_id, count=1000, offset=0)["items"]
    while new_users:
        users.extend(vk.users.get(user_ids=",".join(map(str, new_users)), fields="photo_200_orig"))
        new_users = vk.groups.getMembers(group_id=group_id, count=1000, offset=i + 1000)["items"]  # 1000 id участников
        i += 1000

    user_2 = []
    for user in users:
        user_2.append(
            [user["photo_200_orig"], str(user["first_name"]) + "_" + str(user["last_name"]) + "@" + str(user["id"])])

    for user in user_2:
        photo_request = requests.get(user[0])
        if photo_request.status_code == 200:
            with open("{}/{}.jpg".format("users/", user[1]), 'wb') as f:
                for chunk in photo_request.iter_content(1024):
                    f.write(chunk)
    return 200
