# pygoogle
useful google apis for language processing, support multi cookies to anti CAPTCHA!!!

usage:

    from pygoogle.ngram import GNgram
    ngram = GNram()
    print(ngram("java"))
    
    from pygoogle.search import GSearch
    s = GSearch()
    print(s("Python"))
    
    from pygoogle.translate import GTranslate
    t = GTranslate()
    print(t("who"))

for GSearch, if it successed, return generater. the first element in generator is total num of results on google, the second is relative words. the rest are results.
if it failed, return dict, {"start": start, "query": query, "status": code}

advanced usage:

    from pygoogle.search import GSearch
    from pygoogle.utils import user_agents, RandFloat
    from pygoogle.cookie_cheat import chrome_cookies, firefox_cookies
    with open("test.txt") as fi:
        words = [l.strip() for l in fi]
    words = [w for w in words if len(w) > 4]
    url = "http://s.bt.gg"
    s = GSearch(domain="s.bt.gg", pause=RandFloat(10.0,15.0), use_cookie= [chrome_cookies(url), firefox_cookies(url)])
    counts = []
    for w in words:
        success = False
        while not success:
            try:
                counts.append(next(s(w, stop = 10, debug=True)))
                success = True
            except Exception as e:
                s.reset_domain()
        print("success num:%d" % len(counts))
