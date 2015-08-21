# pygoogle
useful google apis for language processing

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
