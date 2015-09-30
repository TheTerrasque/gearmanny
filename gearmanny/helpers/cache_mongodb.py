from pymongo import Connection, ASCENDING
import datetime
from functools import wraps

def cacheBuilder(host="mongodb://localhost:27017/", dbname="GEARMANCACHE", collection="gearman_cache_table", DEBUG=0, returnvalue_washer=None):
    dbc = Connection(host)[dbname]
    cacher = dbc[collection]
    cacher.ensure_index([("type", ASCENDING), ("query.kwargs", ASCENDING)])
    
    def cache_function(cachetype, days_age=1):
        
        def decorator_function(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if DEBUG: print "CACHE KWARGS:",kwargs
                
                Q = {
                    "type": cachetype,
                    "query.kwargs": kwargs,
                }
                if DEBUG: print " + QUERYDOC:", Q
                
                R = cacher.find_one(Q)
                
                if R:
                    if R.get("purge_at") > datetime.datetime.now():
                        if DEBUG: print " + CACHE FOUND"
                        return R["data"]
                    else:
                        if DEBUG: print " + CACHE OLD", R.get("purge_at")
                if DEBUG: print " + CACHE MISSED"
                
                r = func(*args, **kwargs)
                
                if returnvalue_washer:
                    r = returnvalue_washer(r)
    
                if R: #If we found a cache entry and didn't return it because of age
                    if r:
                        if DEBUG: print " + Removing old cache"
                        #Got a result, remove old entry
                        cacher.remove(Q)
                    else:
                        #Got no result, use cached data as bandaid?
                        if DEBUG: print " + RE-USING old cache"
                        return R["data"]
                
                x = {
                    "type": cachetype,
                    "data": r,
                    "query": {
                        "kwargs": kwargs,
                    },
                    "added": datetime.datetime.now(),
                    "purge_at": datetime.datetime.now() + datetime.timedelta(days=days_age),
                }
                if DEBUG: print " + SAVING NEW ENTRY"
                cacher.save(x)
                
                return r
            return wrapper
        return decorator_function
    return cache_function