import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import urllib.request
import os




def to_image_name(user_info):
    return f'{user_info["name"]}_({user_info["updatedAt"]}).jpg'


def get_local_user_from_image_name(image_name):
    image_name_without_ext = os.path.splitext(image_name)[0]
    name_parts = image_name_without_ext.split('_')

    name = '_'.join(name_parts[:-1])
    timestamp = float(name_parts[-1][1:-1])

    return {
        'name': name,
        'updatedAt': timestamp
    }


def read_data():
    cred = credentials.Certificate("serviceAccount.json")
    app = firebase_admin.initialize_app(cred)
    db = firestore.client(app)
    user_collection = db.collection('users').stream()

    path = "images_dicts"
    dir_list = os.listdir(path)
    local_users = list(map(get_local_user_from_image_name, dir_list))

    for document in user_collection:
        user = document.to_dict()
        user['updatedAt'] = user['updatedAt'].timestamp()

        matched_local_users = [local_user for local_user in local_users if local_user['name'] == user['name']]

        if len(matched_local_users) > 0:
            if matched_local_users[-1]['updatedAt']< user['updatedAt']:
                for matched_local_user in matched_local_users:
                    os.remove(f'images_dicts/{to_image_name(matched_local_user)}')
                    urllib.request.urlretrieve(user['image'], f'images_dicts/{to_image_name(user)}')
        else:
            urllib.request.urlretrieve(user['image'], f'images_dicts/{to_image_name(user)}')

# read_data(db)
