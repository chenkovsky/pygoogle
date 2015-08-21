__author__ = 'chenkovsky'
import requests
import re
from ast import literal_eval
from pygoogle.utils import user_agents
class GNgram:
    corpora = dict(eng_us_2012=17, eng_us_2009=5, eng_gb_2012=18, eng_gb_2009=6,
               chi_sim_2012=23, chi_sim_2009=11, eng_2012=15, eng_2009=0,
               eng_fiction_2012=16, eng_fiction_2009=4, eng_1m_2009=1,
               fre_2012=19, fre_2009=7, ger_2012=20, ger_2009=8, heb_2012=24,
               heb_2009=9, spa_2012=21, spa_2009=10, rus_2012=25, rus_2009=12,
               ita_2012=22)
    URL = 'http://%s/ngrams/graph'
    find_re = re.compile('var data = (.*?);\\n')
    DOMAIN = "books.google.com"

    def __init__(self, domain = None, agents = None):
        if domain is None:
            domain = GNgram.DOMAIN
        if agents is None:
            agents = user_agents
        self._agent = agents
        self._domain = domain

    def __call__(self, query, corpus="eng_2012", start_year=1800, end_year=2012, smoothing=3, case_insensitive=False):
        params = dict(content=query, year_start=start_year, year_end=end_year,
                  corpus=self.corpora[corpus], smoothing=smoothing,
                  case_insensitive=case_insensitive)
        if params['case_insensitive'] is False:
            params.pop('case_insensitive')
        if '?' in params['content']:
            params['content'] = params['content'].replace('?', '*')
        if '@' in params['content']:
            params['content'] = params['content'].replace('@', '=>')
        req = requests.get(self.URL % self._domain, params=params, headers={'User-Agent': str(self._agent)})
        res = self.find_re.findall(req.text)
        if res:
            data = {qry['ngram']: qry['timeseries'] for qry in literal_eval(res[0])}
            return data
        return None

if __name__ == '__main__':
    ngram = GNgram()
    print(ngram("Java"))