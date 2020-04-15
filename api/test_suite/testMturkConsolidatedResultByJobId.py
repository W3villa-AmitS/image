import random
import string
import uuid
from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
import urllib3
import random, string
urllib3.disable_warnings()
import json,time

class TestMturkConsolidatedResultByJobId(SimpleTestCase):
    count = 0
    dynamo = dynamoDatabase.Database()

    #usernames
    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'

    #passwords
    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    result = {
        "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                 {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                     "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                     "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

    def test_consolidate_result_by_job_id(self):
        '''
                    description= 'Send HTTP GET consolidated result using manager login
                    at the endpoint  with valid job_id and valid worker_id's', \
                    expected_output = '200',/test_id = MT_PT_CRJ_GET_000
                    "CRJ = consolidated result Job_id"
               '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='3', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='1', job_tasks_per_hit='2',
                                                   job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        print(job_id)
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        time.sleep(10)
        searcher.mturk_add_qats(job_id, self.result)
        '''generating random string for assignment_id'''
        random_string = string.ascii_uppercase + string.digits
        i = 0
        stringLength = 10
        x = ''.join(random.sample(random_string, stringLength))

        '''
           description= 'Send HTTP POST job approve request using manager login
           at the endpoint  with valid username and password', \
           expected_output = '201',
           '''
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_manager = manager.mturk_approve_job(job_id)
        hit_id = response_manager.json()['hits_created']
        assignment_id = x
        worker_id_first = "SAMPLEWORKERQA"
        worker_id_second ="SAMPLEWORKERAZ"
        worker_id_third = "SAMPLEWORKERZW"

        '''generating access_token for get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id_first)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id_first)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        response_task = mturk.mturk_get_task(token)
        task_id = response_task.json()['task_id']
        '''
                  description= 'Send HTTP POST post_task_result request using access_token and task_id
                  at the endpoint \
                  expected_output = '200',
                  '''
        result = {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}
        result = json.dumps(result)
        mturk.mturk_post_task_result(task_id, result, token)

        response_task_second = mturk.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        status = 'submitted'
        self.assertEqual(status, response_post_result.json()['status'])

        stringLength = 10
        assignment_id_second = ''.join(random.sample(random_string, stringLength))
        mturk = user.MturkUser(hit_id, assignment_id_second, worker_id_second)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id_second, worker_id_second)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        response_task = mturk.mturk_get_task(token)
        task_id = response_task.json()['task_id']
        '''
                  description= 'Send HTTP POST post_task_result request using access_token and task_id
                  at the endpoint \
                  expected_output = '200',
                  '''
        result = {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}
        result = json.dumps(result)
        mturk.mturk_post_task_result(task_id, result, token)
        status = 'submitted'
        response_task_second = mturk.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        self.assertEqual(status, response_post_result.json()['status'])

        stringLength = 10
        assignment_id_third = ''.join(random.sample(random_string, stringLength))
        mturk = user.MturkUser(hit_id, assignment_id_third, worker_id_third)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id_third, worker_id_third)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        response_task = mturk.mturk_get_task(token)
        task_id = response_task.json()['task_id']
        '''
                  description= 'Send HTTP POST post_task_result request using access_token and task_id
                  at the endpoint \
                  expected_output = '200',
                  '''
        result = {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}
        result = json.dumps(result)
        mturk.mturk_post_task_result(task_id, result, token)
        status = 'submitted'
        response_task_second = mturk.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        self.assertEqual(status, response_post_result.json()['status'])
        manager = user.Manager(self.username_manager,self.password_manager)
        time.sleep(10)
        consolidate_result = manager.mturk_consolidate_result_of_job_id(job_id)
        expected_status_code = 200

        try:
            if consolidate_result is None:
                print("consolidates_result is not availabl")
        except:
                print("job is not completed yet")
                assert (False)

        self.assertEqual(expected_status_code,consolidate_result.status_code)

    def test_consolidate_result_by_unauthorised_user(self):
        '''
                         description= 'Send HTTP GET consolidated result using worker login
                         at the endpoint  with valid job_id and valid worker_id's', \
                         expected_output = '401',/test_id = MT_NT_CRJ_GET_000
                         "CRJ = consolidated result Job_id"
                    '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='3', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='1', job_tasks_per_hit='2',
                                                   job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        time.sleep(10)
        searcher.mturk_add_qats(job_id, self.result)
        '''generating random string for assignment_id'''
        random_string = string.ascii_uppercase + string.digits
        i = 0
        stringLength = 10
        x = ''.join(random.sample(random_string, stringLength))

        '''
           description= 'Send HTTP POST job approve request using manager login
           at the endpoint  with valid username and password', \
           expected_output = '201',
           '''
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_manager = manager.mturk_approve_job(job_id)
        hit_id = response_manager.json()['hits_created']
        assignment_id = x
        worker_id_first = "SAMPLEWORKERQA"
        worker_id_second ="SAMPLEWORKERAZ"
        worker_id_third = "SAMPLEWORKERZW"

        '''generating access_token for get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id_first)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id_first)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        response_task = mturk.mturk_get_task(token)
        task_id = response_task.json()['task_id']
        '''
                  description= 'Send HTTP POST post_task_result request using access_token and task_id
                  at the endpoint \
                  expected_output = '200',
                  '''
        result = {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}
        result = json.dumps(result)
        mturk.mturk_post_task_result(task_id, result, token)

        response_task_second = mturk.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        status = 'submitted'
        self.assertEqual(status, response_post_result.json()['status'])

        stringLength = 10
        assignment_id_second = ''.join(random.sample(random_string, stringLength))
        mturk = user.MturkUser(hit_id, assignment_id_second, worker_id_second)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id_second, worker_id_second)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        response_task = mturk.mturk_get_task(token)
        task_id = response_task.json()['task_id']
        '''
                  description= 'Send HTTP POST post_task_result request using access_token and task_id
                  at the endpoint \
                  expected_output = '200',
                  '''
        result = {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}
        result = json.dumps(result)
        mturk.mturk_post_task_result(task_id, result, token)
        status = 'submitted'
        response_task_second = mturk.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        self.assertEqual(status, response_post_result.json()['status'])

        stringLength = 10
        assignment_id_third = ''.join(random.sample(random_string, stringLength))
        mturk = user.MturkUser(hit_id, assignment_id_third, worker_id_third)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id_third, worker_id_third)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        response_task = mturk.mturk_get_task(token)
        task_id = response_task.json()['task_id']
        '''
                  description= 'Send HTTP POST post_task_result request using access_token and task_id
                  at the endpoint \
                  expected_output = '200',
                  '''
        result = {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}
        result = json.dumps(result)
        mturk.mturk_post_task_result(task_id, result, token)
        status = 'submitted'
        response_task_second = mturk.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        self.assertEqual(status, response_post_result.json()['status'])
        worker = user.Worker(self.username_worker,self.password_worker)
        time.sleep(10)
        consolidate_result = worker.mturk_consolidate_result_of_job_id(job_id)
        expected_status_code = 401
        self.assertEqual(expected_status_code,consolidate_result.status_code)
        expected_error = "User is not authorized for this call."
        self.assertEqual(expected_error,consolidate_result.json()['error'])