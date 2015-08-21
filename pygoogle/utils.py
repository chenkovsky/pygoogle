__author__ = 'chenkovsky'
from pkg_resources import resource_filename
import random
class RandString:
    def __init__(self, arr):
        self._arr = arr

    def __str__(self):
        return random.choice(self._arr)

    __repr__ = __str__

user_agents = RandString(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'])
#with open('user-agents.txt') as fi:
with open(resource_filename('pygoogle', 'user-agents.txt')) as fi:
    user_agents = RandString([l.strip() for l in fi])

