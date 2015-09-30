from base import JSONDataEncoder, HOSTS, gearman, GearmanException
import logging

GL = logging.getLogger("gearmanny.client")

class JsonClient(gearman.GearmanClient):
    data_encoder = JSONDataEncoder

class SimpleClient(object):
    last_job = None
    
    def __init__(self, hosts=HOSTS):
        self._client = JsonClient(HOSTS)
    
    def _clientWrapper(self, taskname):
        def inner(**data):
            try:
                work = self._client.submit_job(taskname, data, background=False)
            except (gearman.errors.InvalidClientState, KeyError):
                #Often if it fails, resubmitting job works
                GL.info("Task failed. Re-submitting task")
                work = self._client.submit_job(taskname, data, background=False)
            self._last_job = work
            return work.result
        return inner
    
    def __getattr__(self, name):
        return self._clientWrapper(name)

class AsyncClient(object):
    
    def __init__(self, hosts=HOSTS):
        self.client = JsonClient(HOSTS)
        
    def __getattr__(self, name):
        return self._clientWrapper(name)

    def _clientWrapper(self, taskname):
        class WorkResult(object):
            
            def __init__(self, job,client):
                self.job = job
                self.client = client
        
            def is_done(self):
                return self.job.complete
        
            def get_result(self, timeout=60):
                self.job = self.client.wait_until_jobs_completed([self.job], timeout)[0]
                if self.is_done():
                    return self.job.result
                raise GearmanException("Work not done!")
        
        def inner(**data):
            d = {
                "background": False,
                "wait_until_complete": False
            }
            try:
                work = self.client.submit_job(taskname, data, **d)
            except (gearman.errors.InvalidClientState, KeyError):
                #Often if it fails, resubmitting job works
                GL.info("Task failed. Re-submitting task")
                work = self.client.submit_job(taskname, data, **d)
            return WorkResult(work, self.client)
        return inner    