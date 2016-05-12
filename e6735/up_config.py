import os

resources = {
    'videos': 'resources/videos',
    'audios': 'resources/audios',
    'root': 'resources'
}

resources['videos-g'] = os.path.join(os.getcwd(), resources['videos'])
resources['audios-g'] = os.path.join(os.getcwd(), resources['audios'])
resources['root-g'] = os.path.join(os.getcwd(), resources['root'])
