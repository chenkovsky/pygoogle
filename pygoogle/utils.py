__author__ = 'chenkovsky'
from pkg_resources import resource_filename
import random
class RandString:
    def __init__(self, arr):
        self._arr = arr

    def __str__(self):
        return random.choice(self._arr)

    def __len__(self):
        return len(self._arr)

    def __getitem__(self, idx):
        return self._arr[idx]

    __repr__ = __str__

class RandFloat:
    def __init__(self, min_second, max_second):
        assert(max_second > min_second)
        self._min = min_second
        self._max = max_second

    def __float__(self):
        return random.random()*(self._max - self._min) + self._min

#user_agents = RandString(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'])
#with open('user-agents.txt') as fi:
with open(resource_filename('pygoogle', 'user-agents.txt')) as fi:
    user_agents = RandString([l.strip() for l in fi])

with open(resource_filename('pygoogle','domains.txt')) as fi:
    domains = RandString([l.strip() for l in fi])