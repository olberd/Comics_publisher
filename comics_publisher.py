import os
import random
import requests as requests
from dotenv import load_dotenv


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/104.0.0.0 Safari/537.36'}


def get_random_img_url():
    xkcd_url = 'https://xkcd.com/info.0.json'
    response = requests.get(xkcd_url, headers=HEADERS)
    total_photos = response.json().get('num')
    rand_num = random.randint(1, total_photos)
    return f'https://xkcd.com/{rand_num}/info.0.json'


def load_image_and_comment():
    url = get_random_img_url()
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    comment = response.json().get('alt')
    comic_img_url = response.json().get('img')
    response = requests.get(comic_img_url, headers=HEADERS)
    response.raise_for_status()
    with open('comic_img.png', 'wb') as file:
        file.write(response.content)
    return comment


def get_wall_upload_server_vk(vk_token):
    wall_upload_server_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
       'access_token': vk_token,
       'v': 5.131,
    }
    response = requests.get(wall_upload_server_url, headers=HEADERS, params=params)
    response.raise_for_status()
    upload_url = response.json().get('response').get('upload_url')
    return upload_url


def load_photo_to_server_vk(upload_url):
    with open('comic_img.png', 'rb') as file:
        url = upload_url
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    photo = response.json().get('photo')
    hash = response.json().get('hash')
    server = response.json().get('server')
    return photo, hash, server


def save_wall_photo_vk(vk_token, photo, hash, server):
    save_wall_photo_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': vk_token,
        'photo': photo,
        'hash': hash,
        'server': server,
        'v': 5.131,
    }
    response = requests.post(save_wall_photo_url, headers=HEADERS, params=params)
    owner_id = response.json().get('response')[0].get('owner_id')
    media_id = response.json().get('response')[0].get('id')
    return owner_id, media_id


def post_wall_photo_vk(vk_token, owner_id, media_id, comment):
    post_wall_photo_url = 'https://api.vk.com/method/wall.post'
    params = {
        'access_token': vk_token,
        'owner_id': '-216897029',
        'from_group': '216897029',
        'attachments': f'photo{owner_id}_{media_id}',
        'message': comment,
        'v': 5.131,
    }
    response = requests.post(post_wall_photo_url, headers=HEADERS, params=params)


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.environ.get('VK_TOKEN')
    comment = load_image_and_comment()
    upload_server = get_wall_upload_server_vk(vk_token)
    photo, hash, server = load_photo_to_server_vk(upload_server)
    owner_id, media_id = save_wall_photo_vk(vk_token, photo, hash, server)
    post_wall_photo_vk(vk_token, owner_id, media_id, comment)


