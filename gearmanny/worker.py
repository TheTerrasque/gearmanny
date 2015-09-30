from base import JSONDataEncoder, HOSTS, gearman
import os
import logging
import time
import inspect

GL = logging.getLogger("gearmanny.worker")

class JsonWorker(gearman.GearmanWorker):
    data_encoder = JSONDataEncoder   

class BaseWorker(object):
    work_class = JsonWorker
    verbosity = False
    
    def setUp(self):
        "Can be overwritten to create custom setup"
        pass
    
    def __init__(self, verbosity=False, hosts=HOSTS, gearman_worker=None):
        self._verbosity = verbosity
        
        self._helptext = {}
        
        self._id = "%s-%s@%s" % (self.name, os.getpid(), os.uname()[1])
        
        if gearman_worker == None:
            self._worker = self.work_class(HOSTS)
            self._worker.set_client_id( self._id )
        else:    
            self._worker = worker
        
        self._L = logging.getLogger("gearman.worker.%s" % self.name)
        self._L.debug("Starting client with name %s", self._id)
        self.setUp()
        self._setup_tasks(self.name)

    def start(self):
        """
        Start listening for work assignments
        """
        if self._verbosity > 0:
            print ("Starting worker %s.." % self._id)
        self._worker.work()

    def _helper(self):
        """
        """
        return self._helptext

    def _wrapper(self, wrappedFunction):
        """
        Function wrapper
        """
        parent = self
        def inner(worker, data):
            try:
                parent._L.info("Handling task %s", data.task)
                if parent._verbosity >= 1:
                    print (" Processing task %s" % data.task)
                parent._current_work = data
                time_before = time.time()
                
                if parent._verbosity >= 2:
                    print ("  Arguments: %s" % data.data)
                
                R = wrappedFunction(**data.data)
                
                time_after = time.time()
                ms = (time_after-time_before)*1000.0
                
                if parent._verbosity >= 2:
                    print ("  Task took %sms" % ms)
                return R
            except:
                print ("Request for %s: Failed. Data : %s" % (wrappedFunction.__name__, data))
                parent._L.exception("Function failed")
                raise
        return inner
        
    def _create_help_entry(self, taskname, function):
        description = function.__doc__ and function.__doc__.strip() or "<No description>"
        inp = inspect.getargspec(function)[0][1:] or []
        inp.reverse()
        inp_default = list(inspect.getargspec(function)[3] or [])
        inp_default.reverse()
        d = {}
        
        for i, x in enumerate(inp):
            try:
                temp = {
                    "default": inp_default[i],
                    "required": False,
                }
            except:
                temp = {
                    "default": None,
                    "required": True,
                }
            d[x] = temp
        self._helptext[taskname] = {
            "description": description,
            "input": d,
        }
        
    def _setup_tasks(self, name, worker = None):
        for entry in dir(self):
            if entry.startswith("task_"):
                taskname = "%s_%s" % ( name, entry[5:])
                func = getattr(self, entry)
                self._L.debug("Added task %s", taskname)
                self._create_help_entry(taskname, func)
                
                self._worker.register_task(taskname, self._wrapper(func))
                
        self._worker.register_task("%s_help" % name, self._wrapper(self._helper))
        
    