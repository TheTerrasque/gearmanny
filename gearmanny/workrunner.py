#from .worker import JsonWorker
from multiprocessing import Process
import time
import logging
from collections import defaultdict

GL = logging.getLogger("gearmanny.workrunner")

def run_worker(workers, verbosity, workclass, hosts):
    WorkerInstance = workclass(hosts)
    for worker in workers:
        worker(verbosity=verbosity, gearman_worker = WorkerInstance)
    WorkerInstance.work()

class WorkRunner(object):
    def __init__(self, workers=[], hosts=["localhost:4730"], verbosity=0):
        self.hosts = hosts
        self.verbosity = verbosity
        
        self.workerclasses = defaultdict(list)
        for worker in workers:
            self.workerclasses[worker.work_class].append(worker)
        
    def start_process(self, workers, workerclass):
        p = Process(target=run_worker, args=(workers, self.verbosity, workerclass, self.hosts))
        p.daemon = True
        p.start()
        return p
        
    def start(self, threads=1, keepAlive=True):
        threadlist = []
        for workclass, workerlist in self.workerclasses.items():
            for x in range(threads):
                GL.debug("Started thread %s for workclass %s" % (x+1, workclass))
                p = self.start_process(workerlist, workclass)
                D = {
                    "process" : p
                }
                threadlist.append(D)
        
        while keepAlive:
            time.sleep(0.1)
            for entry in threadlist:
                if not entry["process"].is_alive():
                    GL.error("Process terminated! Restarting!")
                    entry["process"] = self.start_process()
        
        for entry in threadlist:
            entry["process"].join()