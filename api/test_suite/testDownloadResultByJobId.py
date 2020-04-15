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

class TestDownloadResultByJobId(SimpleTestCase):
    gender = '"M","F"'

    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'

    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    result = {
        "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

    def test_download_result_by_valid_user(self):
        '''
           description= 'Send HTTP GET download result using manager login
           at the endpoint  with valid job_id', \
           expected_output = '200',/test_id = MT_PT_DR_GET_000,DR = download result
           '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
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
        worker_id = "SAMPLEWORKERID"

        '''generating access_token for get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        task = user.MturkUser(hit_id, assignment_id, worker_id)
        response_task = task.mturk_get_task(token)
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
        response_task_second = task.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        self.assertEqual(status, response_post_result.json()['status'])

        manager = user.Manager(self.username_manager,self.password_manager)
        '''Downloading result by manager'''
        response_download_result = manager.mturk_download_result_by_job_id(job_id)

        try:
            if response_download_result is None:
                print("Result is not available")
        except:
            print("Result is not defined")
            assert (False)

        expected_status_code = 200
        self.assertEqual(response_download_result.status_code, expected_status_code)

    def test_download_result_by_invalid_user(self):
        '''
                  description= 'Send HTTP GET download result using unauthorised user login
                  at the endpoint  with valid job_id', \
                  expected_output = '403',"Authentication credentials were not provided."
                  /test_id = MT_NT_DR_GET_000,DR = download result
                  '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='1', job_tasks_per_hit='2',
                                                   job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        time.sleep(10)
        re = searcher.mturk_add_qats(job_id, self.result)
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
        worker_id = "SAMPLEWORKERID"

        '''generating access_token for get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        task = user.MturkUser(hit_id, assignment_id, worker_id)
        response_task = task.mturk_get_task(token)
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
        response_task_second = task.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        self.assertEqual(status, response_post_result.json()['status'])

        worker = user.Worker(self.username_worker, self.password_worker)
        '''Downloading result by searcher'''
        download_result = worker.mturk_download_result_by_job_id(job_id)
        error = "Authentication credentials were not provided."
        self.assertEqual(error,download_result.json()['detail'])
        expected_status_code = 403
        self.assertEqual(expected_status_code,download_result.status_code)

    def test_download_result_with_only_wots_added(self):
        '''
                  description= 'Send HTTP GET download result using manager login
                  at the endpoint  with valid job_id', \
                  expected_output = '400',"Result from a job in state 'being_created' can't be fetched."
                  /test_id = MT_NT_DR_GET_001,DR = download result
                  '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        download_result_with_wot = manager.mturk_download_result_by_job_id(job_id)
        error = "Result from a job in state 'being_created' can't be fetched."
        self.assertEqual(error,download_result_with_wot.json()['error'])
        expected_status_code = 400
        self.assertEqual(expected_status_code,download_result_with_wot.status_code)

    def test_download_result_of_unapproved_job(self):
        '''description= 'Send HTTP GET download result using manager login
           at the endpoint  with valid job_id which is not approved by manager ', \
            expected_output = '400',"Result from a job in state 'being_created' can't be fetched."
             /test_id = MT_NT_DR_GET_002,DR = download result
                          '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        time.sleep(10)
        searcher.mturk_add_qats(job_id, self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        download_result_being_created = manager.mturk_download_result_by_job_id(job_id)
        error = "Result from a job in state 'being_created' can't be fetched."
        self.assertEqual(error, download_result_being_created.json()['error'])
        expected_status_code = 400
        self.assertEqual(expected_status_code,download_result_being_created.status_code)


    def test_download_result_without_user_login(self):
        '''description= 'Send HTTP GET download result without user login
           at the endpoint  with valid job_id ', \
            expected_output = '400', "Invalid or expired token."
             /test_id = MT_NT_DR_GET_003,DR = download result
                          '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
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
        worker_id = "SAMPLEWORKERID"

        '''generating access_token for get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        task = user.MturkUser(hit_id, assignment_id, worker_id)
        response_task = task.mturk_get_task(token)
        task_id = response_task.json()['task_id']
        '''
                  description= 'Send HTTP POST post_task_result request using access_token and task_id
                  at the endpoint \
                  expected_output = '200',
                  '''
        result = {
            "cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
            "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                      {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        result = json.dumps(result)
        post_result = user.MturkUser(hit_id, assignment_id, worker_id)
        response_post_result = post_result.mturk_post_task_result(task_id, result, token)
        status = 'submitted'
        self.assertEqual(status, response_post_result.json()['status'])
        manager = user.Manager(self.username_manager, self.password_manager)
        '''Downloading result by manager'''
        download_result = userApisMturk.mturk_download_result_by_job_id_testing(job_id)
        expected_error = "Invalid or expired token."
        expected_status_code = 403
        self.assertEqual(expected_status_code,download_result.status_code)
        self.assertEqual(expected_error,download_result.json()['detail'])

    def test_download_result_with_invalid_job_id(self):
        '''
           description= 'Send HTTP GET download result using manager login
           at the endpoint  with invalid job_id', \
           expected_output = '200',/test_id = MT_PT_DR_GET_000,DR = download result
           '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
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
        worker_id = "SAMPLEWORKERID"

        '''generating access_token for get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        task = user.MturkUser(hit_id, assignment_id, worker_id)
        response_task = task.mturk_get_task(token)
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
        response_task_second = task.mturk_get_task(token)
        task_id_second = response_task_second.json()['task_id']
        response_post_result = mturk.mturk_post_task_result(task_id_second, result, token)
        self.assertEqual(status, response_post_result.json()['status'])

        manager = user.Manager(self.username_manager,self.password_manager)
        '''Downloading result by manager'''
        job_id = job_id+"hello"
        response_download_result = manager.mturk_download_result_by_job_id(job_id)
        expected_error = "Invalid or no job_id's specified."
        self.assertEqual(expected_error, response_download_result.json()['error'])