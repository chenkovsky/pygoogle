__author__ = 'chenkovsky'
import time
from bs4 import BeautifulSoup
import requests
from pygoogle.utils import RandString, user_agents, domains
from urllib.parse import quote_plus, urlparse, parse_qs
from http.cookiejar import LWPCookieJar
from pygoogle.cookie_cheat import chrome_cookies
import os,sys,re
class GSearch:
    DOMAIN = "www.google.com.hk"
    NUM_RE = re.compile(r"([\d,]+)")

    def __init__(self, lang="en", domain=None, result_per_page = 10, agents = None, pause=2.0, safe="off", use_browser_cookie=None):
        if domain is None:
            domain = GSearch.DOMAIN
        if not isinstance(domain, str):
            #it's array
            domain = RandString(domain)#randomsly select domain
        if agents is None:
            agents = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
        self._results_per_page = result_per_page
        self._lang = lang
        self._domain = str(domain)
        self._ori_domain = domain
        self._agent = agents
        self._pause = pause # Lapse to wait between HTTP requests
        self._safe = safe
        self._use_browser_cookie = use_browser_cookie
        self._session = requests.Session()
        if not use_browser_cookie:
            home_folder = os.getenv('HOME')
            if not home_folder:
                home_folder = os.getenv('USERHOME')
                if not home_folder:
                    home_folder = '.'   # Use the current folder on error.
            self._cookie_jar = LWPCookieJar(os.path.join(home_folder, '.google-cookie'))
            self._session.cookies = self._cookie_jar
            try:
                self._cookie_jar.load()
            except Exception:
                pass
        else:
            self._cookie_jar = None

    def reset_domain(self):
        self._domain = str(self._ori_domain)

    def __call__(self, query, tbs='0', start=0, stop=None, pause=2.0, extra_params={}, tpe='', debug=False):
        """
        :param query: str, query string
        :param tbs: str, time limits, i.e. "qdr:h" => last hour, "qdr:d" => last 24 hours, "qdr:m" => last month
        :param start: int, First result to retrieve.
        :param stop: int, Last result to retrieve.
        :param extra_params: For example if you don't want google to filter similar results you can set the extra_params to
        {'filter': '0'} which will append '&filter=0' to every query.
        :param tpe: Search type (images, videos, news, shopping, books, apps)
            Use the following values {videos: 'vid', images: 'isch', news: 'nws',
                                      shopping: 'shop', books: 'bks', applications: 'app'}
        :return: generator, the first element in generator is total num in google.
                and the second element is relative words
        """
        query = quote_plus(query)
        # Check extra_params for overlapping
        for builtin_param in ('hl', 'q', 'btnG', 'tbs', 'safe', 'tbm'):
            if builtin_param in extra_params.keys():
                raise ValueError(
                    'GET parameter "%s" is overlapping with \
                    the built-in GET parameter',
                    builtin_param
                )
        # Grab the cookie from the home page.
        self.page(self.home_url(), debug)
        havent_yield = True
        url = self.gurl(query, tbs, tpe, start)
        while not stop or start < stop:
            iter_extra_params = extra_params.items()
            # Append extra GET_parameters to URL
            for k, v in iter_extra_params:
                url += url + ('&%s=%s' % (k, v))

            # Sleep between requests.
            time.sleep(float(pause))

            # Request the Google Search results page.
            html,code = self.page(url, debug)
            if debug:
                print("page:%s is crawled" % url, file=sys.stderr)
            if code != 200:
                if debug:
                    print("status code is %d" % code)
                    print("content:%s" % html)
                return []

            # Parse the response and process every anchored URL.
            soup = BeautifulSoup(html)
            total_num = int(self.NUM_RE.findall(soup.select("#resultStats")[0].text)[0].replace(",",""))
            if havent_yield:
                yield total_num
                yield [x.text for x in soup.select(".brs_col a")]
                havent_yield = False

            for res in soup.select(".g .rc"):
                e = res.select(".r a")[0]
                #print(e)
                res_title = e.text
                res_url = e["href"]
                res_body = res.select(".st")[0]
                yield (res_title, res_url, res_body)

            # End if there are no more results.
            if not soup.find(id='nav'):
                break

            # Prepare the URL for the next request.
            start += self._results_per_page
            url = self.gurl(query, tbs, tpe, start)

    def home_url(self):
        return "http://%s/" % (str(self._domain))

    def gurl(self, query, tbs, tpe, start):
        if start: return self.next_page_url(query, start, tbs, tpe)
        return self.search_url(query, tbs, tpe)

    def search_url(self, query, tbs, tpe):
        if self._results_per_page == 10:
            return self.search_no_num_url(query, tbs, tpe)
        else:
            return self.search_num_url(query, tbs, tpe)

    def search_no_num_url(self, query, tbs, tpe):
        return "http://%s/search?hl=%s&q=%s&btnG=Google+Search&tbs=%s&safe=%s&tbm=%s" % (str(self._domain),self._lang, query, tbs, self._safe, tpe)

    def search_num_url(self, query, tbs, tpe):
        return "http://%s/search?hl=%s&q=%s&num=%d&btnG=Google+Search&tbs=%s&safe=%s&tbm=%s" % (str(self._domain), self._lang, query, self._results_per_page, tbs, self._safe, tpe)

    def next_page_url(self, query, start, tbs, tpe):
        if self._results_per_page == 10:
            return self.next_page_no_num_url(query, start, tbs, tpe)
        else:
            return self.next_page_num_url(query, start, tbs, tpe)

    def next_page_no_num_url(self, query, start, tbs, tpe):
        return "http://%s/search?hl=%s&q=%s&start=%d&tbs=%s&safe=%s&tbm=%s" % (str(self._domain), self._lang, query, start, tbs, self._safe, tpe)

    def next_page_num_url(self, query, start, tbs, tpe):
        return "http://%s/search?hl=%s&q=%s&num=%d&start=%d&tbs=%s&safe=%s&tbm=%s" % (str(self._domain), self._lang, query, self._results_per_page, start, tbs, self._safe, tpe)

    def page(self, url, debug =False):
        #print(url)
        agent = str(self._agent)
        if debug:
            print("user-agent:%s" % agent)
        if self._use_browser_cookie:
            res = self._session.get(url, headers = {'User-Agent': agent}, cookies = chrome_cookies(url),verify=False)
        else:
            res = self._session.get(url, headers = {'User-Agent': agent},verify=False)
        #self._cookie_jar.save()
        return res.text, res.status_code

    def filter_result(self, link):
        try:

            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urlparse(link, 'http')
            if o.netloc and 'google' not in o.netloc:
                return link
            # Decode hidden URLs.
            if link.startswith('/url?'):
                link = parse_qs(o.query)['q'][0]
                # Valid results are absolute URLs not pointing to a Google domain
                # like images.google.com or googleusercontent.com
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link
        # Otherwise, or on error, return None.
        except Exception:
            pass
        return None

if __name__ == '__main__':
    gs = GSearch(domain="s.bt.gg")
    #print(gs.page("https://s.bt.gg/search?newwindow=1&site=&source=hp&q=%E8%A7%A6%E5%AE%9D%E8%BE%93%E5%85%A5%E6%B3%95&btnG=Google+%E6%90%9C%E7%B4%A2"))
    for x in gs("china site:.cn", debug=True, stop=100):
        print(x)