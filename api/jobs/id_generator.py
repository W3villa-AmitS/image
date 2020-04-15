import random
from .PynamoOps import Dynamo_with_boto
import re
# Here  getID() is used. It wirtten using boto3 because restrinction of import of models in
#this file, because id_generator.py was imported in models.
class DatabaseOperations:
    """
    Class to hold database operations required for verifying if id is already present.
    """
    #object for dynamoOps
    db = Dynamo_with_boto()
    db.connect()

    @classmethod
    def fetch_job(cls, job_id):
        # return cls.db.read_item('jobs', {'job_id': job_id})
       pattern = re.compile("^[0-9a-zA-z]{8}$")
       if not bool(pattern.match(job_id)):
           raise ValueError
       return cls.db.getID('jobs', {'job_id': job_id})

    @classmethod
    def fetch_task(cls, task_id):
        # return cls.db.read_item('tasks', {'task_id': task_id})
        task_id_pattern = re.compile("^[0-9a-zA-z]{16}$")
        if not bool(task_id_pattern.match(task_id)):
            raise ValueError
        return cls.db.getID('tasks', {'task_id': task_id})

def _id_generator(length=8):
    while True:
        random_string = ''
        random_str_seq = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        for i in range(0, length):
            random_string += str(random_str_seq[random.randint(0, len(random_str_seq) - 1)])
        yield random_string

TASK_ID_16 = _id_generator(length=16)
JOB_ID_8 = _id_generator(length=8)

def generate_task_id():
    """
    Returns an 16 character long task_id.
    :return: 16 character long task_id.
    """
    while True:
        new_task_id = next(TASK_ID_16)
        try:
            DatabaseOperations.fetch_task(new_task_id)
        except KeyError:
            return new_task_id
        continue

def generate_job_id():
    """
    Returns an 8 character long job_id.
    :return: 8 character long job_id.
    """
    while True:
        new_job_id = next(JOB_ID_8)
        try:
            DatabaseOperations.fetch_job(new_job_id)
        except KeyError:
            return new_job_id
        continue