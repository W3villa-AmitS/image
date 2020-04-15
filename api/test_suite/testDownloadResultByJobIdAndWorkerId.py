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

class TestDownloadResultByJobIdAndWorkerId(SimpleTestCase):
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

    def test_download_result_by_valid_job_id_and_worker_id(self):
        '''
             description= 'Send HTTP GET download result using manager login
             at the endpoint  with valid job_id and worker_id', \
             expected_output = '200',/test_id = MT_PT_DWK_GET_000
             "DWR = download worker result"
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

        manager = user.Manager(self.username_manager, self.password_manager)
        '''Downloading result by manager'''
        response_download_result = manager.mturk_download_result_by_job_id_and_worker_id(job_id,worker_id)
        try:
             if response_download_result is None:
                 print("Result is not available")
        except:
                print("Result is not defined")
                assert (False)
        expected_status_code = 200
        self.assertEqual(response_download_result.status_code,expected_status_code)

    def test_download_result_by_valid_user_with_invalid_worker_id(self):
        '''
             description= 'Send HTTP GET download result using manager login
             at the endpoint  with valid job_id and invalid worker_id', \
             expected_output = '400',/test_id = MT_NT_DWK_GET_000
             "DWR = download worker result"
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
        worker_id_first = "SAMPLEWORKERID"
        worker_id_second = "WORKERSAMPLEID"
        worker_id_third = "IDSAMPLEWORKER"

        '''generating access_token for get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id_first)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id_first)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        # task = user.MturkUser(hit_id, assignment_id, worker_id_first)
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
        x = ''.join(random.sample(random_string, stringLength))
        assignment_id_second = x
        mturk = user.MturkUser(hit_id, assignment_id_second, worker_id_second)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id_second, worker_id_second)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        # task = user.MturkUser(hit_id, assignment_id, worker_id_first)
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
        x = ''.join(random.sample(random_string, stringLength))
        assignment_id_third = x
        mturk = user.MturkUser(hit_id, assignment_id_third, worker_id_third)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id_third, worker_id_third)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        # task = user.MturkUser(hit_id, assignment_id, worker_id_first)
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
        manager = user.Manager(self.username_manager, self.password_manager)
        '''Downloading result by manager'''
        response_download_result = manager.mturk_download_result_by_job_id_and_worker_id(job_id,worker_id_second)
        expected_error = 400
        self.assertEqual(expected_error,response_download_result.status_code)

    def test_download_result_with_invalid_job_id(self):
        '''
             description= 'Send HTTP GET download result using manager login
             at the endpoint  with invalid job_id, \
             expected_output = '400',/test_id = MT_NT_DWR_GET_001 ,"DWR = download worker result"
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

        manager = user.Manager(self.username_manager, self.password_manager)
        '''Downloading result by manager'''
        job_id_invalid = job_id + 'qwerty'
        response_result_invalid_job_id = manager.mturk_download_result_by_job_id_and_worker_id(job_id_invalid,worker_id)
        expected_error = "Invalid or no job_id's specified."
        expected_status_code = 400
        self.assertEqual(expected_status_code,response_result_invalid_job_id.status_code)
        self.assertEqual(expected_error,response_result_invalid_job_id.json()['error'])

    def test_download_result_with_invalid_job_id_and_worker_id(self):
        '''
                    description= 'Send HTTP GET download result using manager login
                    at the endpoint  with invalid job_id and invalid worker_id, \
                    expected_output = '400',/test_id = MT_NT_DWR_GET_002 ,"DWR = download worker result"
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

        manager = user.Manager(self.username_manager, self.password_manager)
        '''Downloading result by manager'''
        job_id_invalid = job_id + 'qwerty'
        worker_id_invalid = "UNKNOWNWOKRER"
        response_result_invalid_job_and_worker_id = manager.mturk_download_result_by_job_id_and_worker_id(job_id_invalid,worker_id_invalid)
        expected_error = "Invalid or no job_id's specified."
        expected_status_code = 400
        self.assertEqual(expected_status_code, response_result_invalid_job_and_worker_id.status_code)
        self.assertEqual(expected_error, response_result_invalid_job_and_worker_id.json()['error'])


    def test_download_result_of_incomplete_job(self):
        '''
                    description= 'Send HTTP GET download result using manager login
                    at the endpoint  with job_id not performed  by worker, \
                    expected_output = '400',/test_id = MT_NT_DWR_GET_003 ,"DWR = download worker result"
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

        manager = user.Manager(self.username_manager, self.password_manager)
        '''Downloading result by manager'''
        response_result_incomplete_job = manager.mturk_download_result_by_job_id_and_worker_id(job_id,worker_id)
        expected_output = {}
        self.assertEqual(expected_output,response_result_incomplete_job.json()[job_id])

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
        user.Manager(self.username_manager, self.password_manager)
        '''Downloading result by manager'''
        download_result = userApisMturk.mturk_download_result_by_job_id_and_worker_id_testing(job_id,worker_id)
        expected_error = "Invalid or expired token."
        expected_status_code = 403
        self.assertEqual(expected_status_code, download_result.status_code)
        self.assertEqual(expected_error, download_result.json()['detail'])



