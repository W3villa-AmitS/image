from .PynamoOps import Database
# from . DynamoOps import Databases
from .id_generator import generate_job_id, generate_task_id
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, ListAttribute, BooleanAttribute, JSONAttribute
from django.conf import settings

#
# Establish Database Connection

db = Database()
#db.connect()


# object for dynamodb
# pb=Databases()
# pb.connect()


# create job model and task model

#
# Configurations and methods corresponding to 'Job'
#


class Job(object):
    table = "jobs"

    fields = (
        'job_id',  # internal
        'job_status',  # internal
        'job_qat_status',  # internal (initialized, being_added, qats_added)
        'job_wot_status',  # internal (initialized, being_added, wots_added)
        'job_owner',  # internal
        'job_number_of_wots',  # internal
        'job_number_of_qats',  # internal
        'job_boxing_type',  # internal

        'job_wots',  # internal
        'job_qats',  # internal

        'job_name',  # user defined
        'job_type',  # user defined
        'job_attributes',  # user defined
        'job_description',  # user defined
        'job_instructions',  # user defined
        'job_max_occurrence',  # user defined
        'job_criteria_age_min',  # user defined
        'job_criteria_age_max',  # user defined
        'job_criteria_gender',  # user defined
        'job_criteria_location',  # user defined
        'job_criteria_grade',  # user defined
        'job_initial_qats',  # user defined
        'job_qat_frequency',  # user defined
    )

    '''
    class Meta:
        table = "jobs"





    '''

    def __init__(self, **kwargs):
        for field in Job.fields:
            setattr(self, field, kwargs.get(field, None))

        # attributes need to set internally
        setattr(self, 'job_id', Job._get_next_job_id())
        setattr(self, 'job_number_of_wots', 0)
        setattr(self, 'job_number_of_qats', 0)

        setattr(self, 'job_wot_status', 'initialized')
        setattr(self, 'job_qat_status', 'initialized')

        setattr(self, 'job_wots', [])
        setattr(self, 'job_qats', [])

    def _validate(self):
        #
        # all validation checks here
        #
        content = {}
        for field in Job.fields:
            content[field] = getattr(self, field, '')
        return content

    def save(self):

        content = self._validate()
        #import pdb;pdb.set_trace()
        db.insert(Job_Model, self.job_id, content)
        # db.insert(Job.table, content)

    @classmethod
    def _get_next_job_id(cls):
        return generate_job_id()

    @classmethod
    def fetch_job(cls, job_id):
        return db.read_item(Job_Model, job_id)
        # return db.read_item(cls.table, {'job_id': job_id})

    @classmethod
    def fetch_all_jobs(cls):
        return db.read_Table(Job_Model)
        # return pb.read_Table(cls.table)

    @classmethod
    def update_status(cls, job_id, new_status):
        allowed_states = ("being_created",  # Celery is scheduled to add the multiple WOTS
                          "finalized",  # QAT condition met
                          "approving",  # job under approval
                          "approved",  # job approved by a manager
                          "disapproved",  # job disapproved by a manager
                          "in_progress",  # job is in-progress
                          "completed",  # job is completed by workers
                          "validated",  # job is validated by searcher
                          "rejected"  # job results are discarded by searcher
                          )
        assert new_status in allowed_states
        db.update_item(Job_Model, job_id, Job_Model.job_status, new_status)
        # db.update_item(cls.table, {'job_id': job_id}, 'job_status', new_status)

    @classmethod
    def update_wots_status(cls, job_id, new_status):
        allowed_states = ("being_added", "wots_added")
        assert new_status in allowed_states
        db.update_item(Job_Model, job_id, Job_Model.job_wot_status, new_status)
        # db.update_item(cls.table, {'job_id': job_id}, 'job_wot_status', new_status)

    @classmethod
    def update_qats_status(cls, job_id, new_status):
        allowed_states = ("being_added", "qats_added")
        assert new_status in allowed_states
        db.update_item(Job_Model, job_id, Job_Model.job_qat_status, new_status)
        # db.update_item(cls.table, {'job_id': job_id}, 'job_qat_status', new_status)

    @classmethod
    def update_wot_count(cls, job_id, count):
        # job = db.read_item(cls.table, {'job_id': job_id})
        job = db.read_item(Job_Model, job_id)
        db.update_item(Job_Model, job_id, Job_Model.job_number_of_wots, job['job_number_of_wots'] + count)
        # db.update_item(cls.table, {'job_id': job_id}, 'job_number_of_wots', job['job_number_of_wots'] + count)

    @classmethod
    def update_exact_wot_count(cls, job_id, count):
        db.update_item(Job_Model, job_id, Job_Model.job_number_of_wots, count)
        # db.update_item(cls.table, {'job_id': job_id}, 'job_number_of_wots',count)

    @classmethod
    def update_qat_count(cls, job_id, count):
        # job = db.read_item(cls.table, {'job_id': job_id})
        job = db.read_item(Job_Model, job_id)
        db.update_item(Job_Model, job_id, Job_Model.job_number_of_qats, job['job_number_of_qats'] + count)
        # db.update_item(cls.table, {'job_id': job_id}, 'job_number_of_qats',job['job_number_of_qats'] + count)

    @classmethod
    def qats_required(cls, job_id):
        # job = db.read_item(cls.table, {'job_id': job_id})
        job = db.read_item(Job_Model, job_id)
        if job['job_qat_frequency'] > 0:
            return job['job_initial_qats'] + int(job['job_number_of_wots'] / job['job_qat_frequency'])
        return job['job_initial_qats']

    @classmethod
    def add_qat(cls, job_id, qat_id):
          job = db.read_item(Job_Model, job_id)
          db.update_item(Job_Model, job_id, Job_Model.job_qats, job['job_qats'] + [qat_id])
        #job = db.read_item(cls.table, {'job_id': job_id})
        #db.update_item(cls.table, {'job_id': job_id}, 'job_qats', job['job_qats'] + [qat_id])
 
    @classmethod
    def add_wot(cls, job_id, wot_id):
        job = db.read_item(Job_Model, job_id)
        db.update_item(Job_Model, job_id, Job_Model.job_wots, job['job_wots'] + [wot_id])
        #job = db.read_item(cls.table, {'job_id': job_id})
        #db.update_item(cls.table, {'job_id': job_id}, 'job_wots', job['job_wots'] + [wot_id])

    @classmethod
    def update_qats_and_wots(cls, job_id, wots, qats):
        db.update_item(Job_Model, job_id, Job_Model.job_wots, wots)
        db.update_item(Job_Model, job_id, Job_Model.job_qats, qats)
        # db.update_item(cls.table, {'job_id': job_id}, 'job_wots', wots)
        # db.update_item(cls.table, {'job_id': job_id}, 'job_qats', qats)

    @staticmethod
    def completed(job_id):
        completed = True
        job = Job.fetch_job(job_id)
        for task in job['job_wots']:
            completed &= Task.completed(Task.fetch_task(task))
        return completed


class Job_Model(Model):
    class Meta:
        table_name = 'jobs'
        region = settings.DYNAMO['REGION']
        host = settings.DYNAMO['URL']
        aws_access_key_id = settings.DYNAMO_AWS_ACCESS['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = settings.DYNAMO_AWS_ACCESS['AWS_SECRET_ACCESS_KEY']

    # internal fields
    job_id = UnicodeAttribute(hash_key=True)
    job_status = UnicodeAttribute(default='initialized')
    job_qat_status = UnicodeAttribute(default='initialized')
    job_wot_status = UnicodeAttribute(default='initialized')
    job_owner = NumberAttribute(default=0)
    job_number_of_wots = NumberAttribute(default=0)
    job_number_of_qats = NumberAttribute(default=0)
    job_wots = ListAttribute(default=[])
    job_qats = ListAttribute(default=[])

    # user defined fields

    job_name = UnicodeAttribute()
    job_type = UnicodeAttribute()
    job_attributes = UnicodeAttribute()
    job_description = UnicodeAttribute()
    job_instructions = UnicodeAttribute()
    job_max_occurrence = NumberAttribute()
    job_criteria_age_min = NumberAttribute()
    job_criteria_age_max = NumberAttribute()
    job_criteria_gender = ListAttribute()
    job_criteria_location = UnicodeAttribute()
    job_criteria_grade = UnicodeAttribute()
    job_initial_qats = NumberAttribute()
    job_qat_frequency = NumberAttribute()
    job_boxing_type = UnicodeAttribute(null=True)


#
# Configurations and methods corresponding to 'Task'
#
class Task(object):
    table = "tasks"

    fields = ('task_id',  # internal
              'results',  # internal
              'is_qat',  # internal
              'result',  # internal

              'job_id',  # user defined
              'max_occurrence',  # user defined
              'image_url',  # user defined
              )

    def __init__(self, **kwargs):
        for field in Task.fields:
            setattr(self, field, kwargs.get(field, None))

        # attributes need to set internally
        setattr(self, 'task_id', Task._get_next_task_id(getattr(self, 'job_id', '')))

    def _validate(self):
        #
        # all validation checks here
        #
        content = {}
        for field in Task.fields:
            content[field] = getattr(self, field, '')
        return content

    def save(self):
        content = self._validate()
        db.insert(Task_Model, self.task_id, content)
        # db.insert(Task.table, content)

    @classmethod
    def _get_next_task_id(cls, job_id):
        return str(job_id) + generate_task_id()

    @classmethod
    def fetch_task(cls, task_id):
        return db.read_item(Task_Model, task_id)
        # return db.read_item(Task.table,{'task_id': task_id})

    @classmethod
    def fetch_all_tasks_from_job(cls, job_id):
        return db.read_Table_by_attribute(Task_Model, Task_Model.job_id, job_id)
        # allTasks = db.read_Table(Task_Model)
        # return [task for task in allTasks if task['job_id'] == job_id]

    @classmethod
    def fetch_all_tasks(cls):
        return db.read_Table(Task_Model)

    @classmethod
    def update_results(cls, task_id, updated_results):
        db.update_item(Task_Model, task_id, Task_Model.results, updated_results)
        # db.update_item(cls.table, {'task_id': task_id}, 'results', updated_results)

    @classmethod
    def rollback_result(cls, task_id, user_id):
        # results = db.read_item(cls.table, {'task_id': task_id})['results']
        results = db.read_item(Task_Model, task_id)['results']
        results.pop(str(user_id))
        db.update_item(Task_Model, task_id, Task_Model.results, results)
        # db.update_item(cls.table, {'task_id': task_id}, 'results', results)

    @staticmethod
    def completed(task):
        return len(task['results']) >= int(task['max_occurrence'])


class Task_Model(Model):
    class Meta:
        # aws_access_key_id = 'my_access_key_id'
        # aws_secret_access_key = 'my_secret_access_key'
        table_name = 'tasks'
        region = settings.DYNAMO['REGION']
        host = settings.DYNAMO['URL']
        aws_access_key_id = settings.DYNAMO_AWS_ACCESS['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = settings.DYNAMO_AWS_ACCESS['AWS_SECRET_ACCESS_KEY']

    # internal fields
    task_id = UnicodeAttribute(hash_key=True)
    results = JSONAttribute(default={})
    is_qat = BooleanAttribute(default=False)
    result = JSONAttribute(default={}, null=True)

    # user defined fields
    job_id = UnicodeAttribute(default='')
    max_occurrence = NumberAttribute(default=0)
    image_url = UnicodeAttribute(default='')