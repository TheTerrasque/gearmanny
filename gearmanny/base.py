import gearman
import json

HOSTS = ['localhost:4730']

class GearmanException(Exception):
    pass

class JSONDataEncoder(gearman.DataEncoder):
    @classmethod
    def encode(cls, encodable_object):
        return json.dumps(encodable_object)

    @classmethod
    def decode(cls, decodable_string):
        return json.loads(decodable_string)