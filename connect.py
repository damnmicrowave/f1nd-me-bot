import json

from vk_api import VkApi

with open("secret.json", 'r') as fp_secret:
    secret = json.load(fp_secret)
    app_id = secret.get('app_id')
    login = secret.get('login')
    password = secret.get('password')

vk_session = VkApi(login, password)
vk_session.auth()

vk = vk_session.get_api()
