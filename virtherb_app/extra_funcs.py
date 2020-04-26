import requests
from flask import session
# from imgurkeys import client_id


def clear_specimen_session():
    """Clears the session of all specimen form information"""

    specimen_info = [
        "link",
        "common_name",
        "species",
        "genus",
        "family",
        "order",
        "phylum",
        "kingdom",
        "authorship",
        "date",
        "location",
        "county",
        "state",
        "habitat",
        "notes",
    ]

    for info in specimen_info:
        session.pop(info, None)


#############################
# Imgur uploader function


def upload_img(img):
    url = "https://api.imgur.com/3/image"

    data = {"image": img}

    headers = {"Authorization": "Client-ID d5abbfd23ff9199"}

    resp = requests.post(url, headers=headers, data=data)

    return resp.json()
