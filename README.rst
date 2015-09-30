Gearmanny
=========

This is a wrapper to the Gearman python API to more easily create simple workers and clients for the Gearman Job Server.

The serializer used is JSON. Worker expects a JSON formatted string with the keys for the called function, and that the return value is json serializable.


Worker
------
Worker example::

    from gearmanny.worker import BaseWorker
    
    class MyWorker(BaseWorker):
        name="myworker"                             # This name will replace "task" part of function name
        work_class = JsonWorker                     # Default is JsonWorker, but can be changed if you need other serialization
        
        def task_echo(self, text, double=False):    # Each function starting with "task_" will be exported
            "Echoes the text"
            if double:
                return text+text
            return text                             # Returned data must be JSON serializable
    
        def task_add(self, a, b):
            "Adds A and B together"
            return a + b
            
    if __name__ == "__main__":
        worker = MyWorker() 						# Default arguments: hosts=["localhost:4730"], verbosity=0, gearman_worker=None
        worker.start()
        

WorkRunner
----------

Workrunner will run the given worker classes in subprocesses, and if keepAlive is true, it will restart the
subprocess if it stops for whatever reason. Accepts a list of BaseWorker subclasses. It will start a set of threads
for each work_class type found.

With worker from previous example::
    
    from gearmanny.workrunner import WorkRunner
    
    worker = WorkRunner([MyWorker])         # Defaults: hosts=["localhost:4730"], verbosity=0 
    worker.start()                          # Defaults: threads=1, keepAlive=True
        
Client
------

Synchronous client::
    
    from gearmanny.client import SimpleClient
    
    client = SimpleClient()                         # Defaults: hosts=["localhost:4730"]
    
    print client.myworker_echo(text="This is text") # Arguments must be JSON serializable
    print client.myworker_add(a=10, b=15)			# Only keyword based arguments, no positional
    
    import pprint
    pprint.pprint(client.myworker_help())           # Auto generated help info for the worker
    

Asynchronious client::

    from gearmanny.client import AsyncClient
    
    aclient = AsyncClient()                         # Defaults: hosts=["localhost:4730"]
    
    r = client.myworker_echo(text="This is text")   # Returns a work object tracking the internal task state
    print r.is_done()                               # Returns True if task is done, False otherwise
    print r.get_result()                            # Wait for the result, then return it. Default argument: timeout=60
    
    
Helpers
=======

MongoDB cache
-------------

This can use a MongoDB server for caching of answers, thus avoiding re-doing costly queries.
This matches incoming queries by unique_name and the arguments sent.

Example::

    from gearmanny.helpers.cache_mongodb import cacheBuilder
    cachewrap = cacheBuilder() # Defaults  : host="mongodb://localhost:27017/", dbname="GEARMANCACHE", collection="gearman_cache_table", DEBUG=0, returnvalue_washer=None
    
    class MyWorker(BaseWorker):
        name="myworker"
        
        @cachewrap("unique_name", max_days_age=1)
        def task_echo(self, text, double=False):
            "Echoes the text"
            if double:
                return text+text
            return text     