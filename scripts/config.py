#! python3.6

import json
from os.path import join
from typing import List, Dict


__all__ = ['VERSION', 'HOST_NAME', 'CREDENTIALS', 'IGNORED_USERS', 'LOG_FILE', 'BUFFER_FILE']

BASE_DIR = ''
with open(join(BASE_DIR, 'VERSION')) as file:
    VERSION: str = file.read()

with open(join(BASE_DIR, VERSION, 'config.json')) as file:
    config = json.load(file)
HOST_NAME: str = config['HOST_NAME']
CREDENTIALS: Dict[str, str] = config['CREDENTIALS']
IGNORED_USERS: List[str] = config['IGNORED_USERS']
LOG_FILE: str = config['LOG_FILE']
BUFFER_FILE: str = config['BUFFER_FILE']
