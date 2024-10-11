import requests
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Now you can access the variables like this:
token = os.getenv('TOKEN')


from schemas import CommandPlayer, ViewPlayer

host = 'https://games-test.datsteam.dev/'


def move(data: list[CommandPlayer]) -> ViewPlayer:
    response = requests.post(host + 'play/magcarp/player/move', headers={
        'X-Auth-Token': token
    }, json={
        'transports': [t.model_dump() for t in data]
    })

    return ViewPlayer.model_validate(response.json())
