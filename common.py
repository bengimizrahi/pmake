# Author: Bengi Mizrahi
# Date: 12.06.2012

COLORS = {
    "blue": "\033[1;34m",
    "default": "\x1B[m",
    "yellow": "\033[1;33m",
    "magenda": "\033[1;31m",
    "white": "\033[1;37m",
    "green": "\033[1;32m",
    "red": "\033[1;31m",
}

def cache(f):
    cachedData = dict()
    def newf(key):
        value = cachedData.get(key)
        if not value:
            value = f(key)
            cachedData[key] = value
        return value
    return newf

def log(f):
    print "---- Entered %s ----" % f.__name__
    f()
    print "---- Exited %s ----" % f.__name__
