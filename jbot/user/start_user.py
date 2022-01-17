from .. import mybot
from .login import client
if mybot['开启user'].lower() == 'true':
    client.start()
    
