import os
import random

import requests as requests
from dotenv import load_dotenv


def get_random_comics_url():
    xkcd_url = 'https://xkcd.com/info.0.json'
    response = requests.get(xkcd_url)
    response.raise_for_status()
    total_photos = response.json().get('num')
    rand_num = random.randint(1, total_photos)
    return f'https://xkcd.com/{rand_num}/info.0.json'


def download_comics():
    url = get_random_comics_url()
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    comic_comment = response.get('alt')
    comic_img_url = response.get('img')
    response = requests.get(comic_img_url)
    response.raise_for_status()
    with open('comic_img.png', 'wb') as file:
        file.write(response.content)
    # raise ValueError
    return comic_comment


def handle_http_error(response):
    if 'error' in response:
        raise requests.HTTPError(
            response.get('error').get('error_code'),
            response.get('error').get('error_msg'),
        )


def get_wall_upload_server_vk(vk_token):
    wall_upload_server_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
       'access_token': vk_token,
       'v': 5.131,
    }
    response = requests.get(wall_upload_server_url, params=params)
    response.raise_for_status()
    response = response.json()
    handle_http_error(response)
    upload_url = response.get('response').get('upload_url')
    return upload_url


def upload_photo_to_server_vk(upload_url):
    with open('comic_img.png', 'rb') as file:
        url = upload_url
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    response = response.json()
    handle_http_error(response)
    photo = response.get('photo')
    photo_hash = response.get('hash')
    server = response.get('server')
    return photo, photo_hash, server


def save_wall_photo_vk(vk_token, photo, photo_hash, server):
    save_wall_photo_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': vk_token,
        'photo': photo,
        'hash': photo_hash,
        'server': server,
        'v': 5.131,
    }
    response = requests.post(save_wall_photo_url, params=params)
    response.raise_for_status()
    response = response.json()
    handle_http_error(response)
    owner_id = response.get('response')[0].get('owner_id')
    media_id = response.get('response')[0].get('id')
    return owner_id, media_id


def post_wall_photo_vk(vk_token, group_id, owner_id, media_id, comment):
    post_wall_photo_url = 'https://api.vk.com/method/wall.post'
    params = {
        'access_token': vk_token,
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'attachments': f'photo{owner_id}_{media_id}',
        'message': comment,
        'v': 5.131,
    }
    response = requests.post(post_wall_photo_url, params=params)
    response.raise_for_status()
    response = response.json()
    handle_http_error(response)


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.environ.get('VK_TOKEN')
    group_id = os.environ.get('VK_GROUP_ID')
    try:
        comment = download_comics()
        upload_server = get_wall_upload_server_vk(vk_token)
        photo, photo_hash, server = upload_photo_to_server_vk(upload_server)
        owner_id, media_id = save_wall_photo_vk(vk_token, photo, photo_hash, server)
        post_wall_photo_vk(vk_token, group_id, owner_id, media_id, comment)
    finally:
        os.remove('comic_img.png')

