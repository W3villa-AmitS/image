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

class TestMturkPostTaskResult(SimpleTestCase):
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

    def test_post_task_result_by_valid_token(self):
        '''
           description= 'Send HTTP POST task result request using worker login
           at the endpoint  with valid username and password', \
           expected_output = '201',/test_id = MT_PT_PTR_POST_000
           '''
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
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
        searcher.mturk_add_qats(job_id,self.result)

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
        result_new = json.dumps(result)
        post_result = user.MturkUser(hit_id,assignment_id,worker_id)
        response_post_result = post_result.mturk_post_task_result(task_id,result_new,token)
        status = 'submitted'
        self.assertEqual(status,response_post_result.json()['status'])
        expected_status_code = 200
        self.assertEqual(expected_status_code,response_post_result.status_code)

    def test_post_task_result_by_invalid_token(self):

        '''
                 description= 'Send HTTP POST task result request using searcher login
                 at the endpoint  with valid username and password', \
                 expected_output = '401',/test_id = MT_NT_PTR_POST_000
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
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}

        result = json.dumps(result)
        time.sleep(10)
        searcher.mturk_add_qats(job_id, self.result)

        '''generating random string for assignment_id'''
        random_string = string.ascii_uppercase + string.digits
        i = 0
        stringLength = 10
        x = ''.join(random.sample(random_string, stringLength))

        '''
           description= 'Send HTTP POST job approve request using manager login
           at the endpoint  with valid username and password', \,
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
                  description= 'Send HTTP POST post_task_result =request using invalid access_token
                  at the endpoint  with valid task_id, \expected_output = 401,
                  '''

        post_result_invalid = user.MturkUser(hit_id,assignment_id, worker_id)
        response_post_result_invalid = post_result_invalid.mturk_post_task_result(task_id,result,token + '1')
        error = response_post_result_invalid.json()['error']
        expected_status_code = 401
        self.assertEqual(expected_status_code,response_post_result_invalid.status_code)
        expected_error = 'Signature verification failed'
        self.assertEqual(expected_error,error)

    def test_post_task_result_without_token(self):

        '''
                 description= 'Send HTTP POST task result request without bearer token
                 at the endpoint  with valid username and password', \
                 expected_output = '400'/test_id = MT_NT_PTR_POST_001,
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
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}

        result = json.dumps(result)
        searcher.mturk_add_qats(job_id,self.result)
        time.sleep(10)
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
                   description= 'Send HTTP POST job approve request without access token
                   at the endpoint  with task_id', \
                   expected_output = '400',
                   '''

        response_without_token = userApisMturk.mturk_post_task_result(task_id,result,"")
        expected_status_code = 401
        self.assertEqual(expected_status_code,response_without_token.status_code)
        expected_error =  'Invalid token header. No credentials provided.'
        error = response_without_token.json()['error']
        self.assertEqual(expected_error,error)

    def test_post_result_by_invalid_task_id(self):

        '''
                 description= 'Send HTTP POST task result request using worker login
                 at the endpoint  with invalid task id, \
                 expected_output = '404',/test_id = MT_NT_PTR_POST_002
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
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}

        result = json.dumps(result)

        searcher.mturk_add_qats(job_id,self.result)
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
            description= 'Send HTTP POST post_task_result =request using valid access_token
            at the endpoint  with invalid task_id, \expected_output = 404,
                         '''

        post_result_invalid_task_id = user.MturkUser(hit_id,assignment_id,worker_id)
        response_post_result_invalid_task_id = post_result_invalid_task_id.mturk_post_task_result(task_id + 'ad1w2',result,token)
        expected_status_code = 404
        expected_error = "Invalid task"
        self.assertEqual(expected_status_code,response_post_result_invalid_task_id.status_code)
        self.assertEqual(expected_error,response_post_result_invalid_task_id.json()['error'])

    def test_post_result_by_multiple_worker(self):

        '''
                    description= 'Send HTTP POST post_task_result request using valid access_token
                    at the endpoint  with valid task_id,
                     same task post by multiple worker  \expected_output = 406,/test_id = MT_NT_PTR_POST_003        '''

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
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}

        result = json.dumps(result)

        response_qat = searcher.mturk_add_qats(job_id, self.result)

        '''generating random string for assignment_id'''
        random_string = string.ascii_uppercase + string.digits
        i = 0
        stringLength = 10
        x = ''.join(random.sample(random_string, stringLength))

        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_manager = manager.mturk_approve_job(job_id)

        hit_id = response_manager.json()['hits_created']
        assignment_id = x
        worker_id = "SAMPLEWORKERID"
        worker_id_new = "SAMPLEWORKERID19"

        '''generating access_token for get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        task = user.MturkUser(hit_id, assignment_id, worker_id)
        response_task = task.mturk_get_task(token)
        task_id = response_task.json()['task_id']

        post_result_multiple_worker = user.MturkUser(hit_id,assignment_id,worker_id)
        post_result_multiple_worker.mturk_post_task_result(task_id,result,token)

        '''
                    description= 'Send HTTP POST post_task_result request using valid access_token
                    at the endpoint  with valid task_id,
                     same task post by multiple worker  \expected_output = 406,        '''

        post_result_multiple_worker = user.MturkUser(hit_id, assignment_id, worker_id_new)
        response_post_result_multiple_worker = post_result_multiple_worker.mturk_post_task_result(task_id,result,token)
        error = response_post_result_multiple_worker.json()['error']
        expected_error = "Submission against non-allocation is not allowed"
        self.assertEqual(expected_error,error)
        expected_status_code = 406
        self.assertEqual(expected_status_code,response_post_result_multiple_worker.status_code)

    def test_post_result_unallocated_task_id(self):

        '''         description= 'Send HTTP POST post_task_result request using valid access_token
                           at the endpoint  with valid task_id, and unallocated task_id
                            \expected_output = 406,test_id = MT_NT_PTR_POST_004         '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        job_id = response_post_job.json()['job_id']
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        time.sleep(10)
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}

        result = json.dumps(result)

        searcher.mturk_add_qats(job_id,self.result)

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
        post_result_unallocated = user.MturkUser(hit_id,assignment_id,worker_id)
        response_post_result_unallocated = post_result_unallocated.mturk_post_task_result(task_id,result,token)
        response_post_result_unallocated_task_id = post_result_unallocated.mturk_post_task_result(task_id, result, token)
        error = response_post_result_unallocated_task_id.json()['error']
        expected_error = "Submission against non-allocation is not allowed"
        expected_status_code = 406
        self.assertEqual(expected_status_code,response_post_result_unallocated_task_id.status_code)
        self.assertEqual(expected_error,error)



    def test_post_result_without_job_attributes(self):

        '''         description= 'Send HTTP POST post_task_result request using valid access_token
                                         at the endpoint  with valid task_id, and without job attributes
                                         \expected_output = 400, test_id = MT_NT_PTR_POST_005  '''

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
        searcher.mturk_add_qats(job_id,self.result)
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


        # result_new = {"cars": [{}],
        #           "bikes": [{}]}
        result_new = {
            "  ": [{"x1": "5", "y1": "0", "x3": "10"}, {"x1": "5", "y1": "0", "x3": "10"}],
            " ": [{"x1": "5", "y1": "0", "x2": "10"}, {"x1": "5", "y1": "0", "x3": "10"}]}
        result_new = json.dumps(result_new)



        post_result_without_job_attributes = user.MturkUser(hit_id,assignment_id,worker_id)
        response_without_job_attributes = post_result_without_job_attributes.mturk_post_task_result(task_id,result_new,token)
        error = response_without_job_attributes.json()['result']
        expected_error =  ["Invalid/Unknown Json object for attribute '  '"]
        expected_status_code = 400
        self.assertEqual(expected_error,error)
        self.assertEqual(expected_status_code,response_without_job_attributes.status_code)

    def test_post_result_with_different_job_attributes(self):

        '''         description= 'Send HTTP POST post_task_result request using valid access_token
                                                 at the endpoint  with valid task_id, and with diff job attributes
                                                 \expected_output = 400, test_id = MT_NT_PTR_POST_006  '''

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

        result = {"car": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bike": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}

        result = json.dumps(result)

        searcher.mturk_add_qats(job_id, self.result)
        time.sleep(10)
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

        post_result_with_diff_attributes = user.MturkUser(hit_id, assignment_id, worker_id)
        response_with_diff_job_attributes = post_result_with_diff_attributes.mturk_post_task_result(task_id,result,token)
        expected_error = 'Attributes in result mismatched with job attributes.'
        error = response_with_diff_job_attributes.json()['error']
        expected_status_code = 406
        self.assertEqual(expected_error, error)
        self.assertEqual(expected_status_code, response_with_diff_job_attributes.status_code)

    def test_post_task_result_by500_expired_token(self):

        '''
                 description= 'Send HTTP POST task result request using searcher login
                 at the endpoint  with valid username and password', \
                 expected_output = '401',/test_id = MT_NT_PTR_POST_007
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

        '''generating random string for assignment_id'''
        random_string = string.ascii_uppercase + string.digits
        i = 0
        stringLength = 10
        x = ''.join(random.sample(random_string, stringLength))

        '''
           description= 'Send HTTP POST job approve request using manager login
           at the endpoint  with valid username and password', \,
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
        token_old = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        response_task = mturk.mturk_get_task(token_old)
        task_id = response_task.json()['task_id']
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}

        result = json.dumps(result)
        mturk.mturk_post_task_result(task_id,result,token_old)

        '''In this part searcher creates new job and wokrer post result on new hit_id,assignement_id,worker_id using expired token'''

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
        time.sleep(10)
        searcher.mturk_add_wots_new(job_id, file)
        searcher.mturk_add_qats(job_id, self.result)

        '''generating random string for assignment_id'''
        random_string = string.ascii_uppercase + string.digits
        i = 0
        stringLength = 10
        x = ''.join(random.sample(random_string, stringLength))

        '''
           description= 'Send HTTP POST job approve request using manager login
           at the endpoint  with valid username and password', \,
           '''
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_manager = manager.mturk_approve_job(job_id)
        hit_id = response_manager.json()['hits_created']
        assignment_id = x
        worker_id = "SAMPLEWORKERID"
        mturk = user.MturkUser(hit_id, assignment_id, worker_id)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id)
        token_new = response_mturk.json()['token']
        '''getting task_id by passing access_token'''
        response_task = mturk.mturk_get_task(token_new)
        task_id_new = response_task.json()['task_id']
        time.sleep(10)
        response_xyz = mturk.mturk_post_task_result(task_id, result, token_new)
        error = response_xyz.json()['error']
        expected_status_code = 406
        self.assertEqual(expected_status_code,response_xyz.status_code)
        expected_error = 'Submission against non-allocation is not allowed'
        self.assertEqual(expected_error,error)


    def test_post_task_result_by_null_task_id(self):
        '''
           description= 'Send HTTP POST task result request using worker login
           at the endpoint  with null hit_id', \
           expected_output = '201',/test_id = MT_NT_PTR_POST_008'''

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
        result = {
            "cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
            "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                      {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        post_result = user.MturkUser(hit_id, assignment_id, worker_id)
        post_result_null_task_id = post_result.mturk_post_task_result(" ", result, token)
        expected_status_code = 400
        self.assertEqual(expected_status_code,post_result_null_task_id.status_code)

    def test_post_task_result_by_less_attributes(self):
        '''
           description= 'Send HTTP POST task result request using worker login
           at the endpoint  with valid username and password', \
           expected_output = '201',/test_id = MT_NT_PTR_POST_009
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

        '''generating access_token to get_task and post_task_result'''
        mturk = user.MturkUser(hit_id, assignment_id, worker_id)
        response_mturk = mturk.mturk_get_token(hit_id, assignment_id, worker_id)
        token = response_mturk.json()['token']

        '''getting task_id by passing access_token'''
        # task = user.MturkUser(hit_id, assignment_id, worker_id)
        response_task = mturk.mturk_get_task(token)
        task_id = response_task.json()['task_id']

        '''
                  description= 'Send HTTP POST post_task_result request using access_token and task_id
                  at the endpoint \
                  expected_output = '200',
                  '''
        result = {
            "cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}]}
        result_new = json.dumps(result)
        response_less_attributes = mturk.mturk_post_task_result(task_id, result_new, token)
        expected_status_code = 406
        self.assertEqual(expected_status_code,response_less_attributes.status_code)
        error = 'Attributes in result mismatched with job attributes.'
        self.assertEqual(error,response_less_attributes.json()['error'])

    def test_post_task_result_by_more_attributes(self):
        '''
           description= 'Send HTTP POST task result request using worker login
           at the endpoint  with valid username and password', \
           expected_output = '201',/test_id = MT_NT_PTR_POST_010
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
            "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},{"x1": "7", "y1": "9", "x2": "8", "y2": "10"}],
            "cycles": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},{"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        result = json.dumps(result)

        post_result = user.MturkUser(hit_id, assignment_id, worker_id)
        response_more_attributes = post_result.mturk_post_task_result(task_id, result, token)
        expected_status_code = 406
        self.assertEqual(expected_status_code,response_more_attributes.status_code)
        error = 'Attributes in result mismatched with job attributes.'
        self.assertEqual(error,response_more_attributes.json()['error'])

    def test_post_task_result_by_sqaure_coordinates(self):
        '''
           description= 'Send HTTP POST task result request using worker login
           at the endpoint  with square coordinates', \
           expected_output = '201',/test_id = MT_NT_PTR_POST_011
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
            "cars": [{"x1": "5", "y1": "0", "x3": "10"}, {"x1": "5", "y1": "0", "x3": "10"}],
            "bikes": [{"x1": "5", "y1": "0", "x2": "10"},{"x1": "5", "y1": "0", "x3": "10"}]}
        result = json.dumps(result)
        post_result = user.MturkUser(hit_id, assignment_id, worker_id)
        response_sqaure_coordinates = post_result.mturk_post_task_result(task_id, result, token)
        error =["Invalid/Unknown Json object for attribute 'cars'"]
        expected_status_code = 400
        self.assertEqual(error,response_sqaure_coordinates.json()['result'])
        self.assertEqual(expected_status_code,response_sqaure_coordinates.status_code)

    def test_post_task_result_on_attributes_job(self):
        '''
           description= 'Send HTTP POST task result request using worker login
           at the endpoint on attributes type job', \
           expected_output = '201',/test_id = MT_NT_PTR_POST_012
           '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='A', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3'
                                                   ,job_boxing_type='Rectangle')
        job_id = response_post_job.json()['job_id']
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        time.sleep(10)
        searcher.mturk_add_qats(job_id, self.result)
        time.sleep(10)
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
        response_attribute_job = post_result.mturk_post_task_result(task_id, result, token)
        expected_status_code = 406
        self.assertEqual(expected_status_code,response_attribute_job.status_code)

    def test_post_task_result_on_null_result(self):
        '''description= 'Send HTTP POST task result request using worker login
                   at the endpoint with null result', \
                   expected_output = '201',/test_id = MT_NT_PTR_POST_013
                   '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3'
                                                   ,job_boxing_type='Rectangle')
        job_id = response_post_job.json()['job_id']
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        time.sleep(10)
        searcher.mturk_add_qats(job_id, self.result)
        time.sleep(10)
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
            "cars": [],
            "bikes": []
        }
        result = json.dumps(result)
        post_result = user.MturkUser(hit_id, assignment_id, worker_id)
        response_null_result = post_result.mturk_post_task_result(task_id, result, token)
        status = "submitted"
        expected_status_code = 200
        self.assertEqual(response_null_result.json()['status'],status)
        self.assertEqual(expected_status_code,response_null_result.status_code)

    def test_post_task_result_using_string_type_result(self):
        '''
           description= 'Send HTTP POST task result request using worker login
           at the endpoint  with string type result', \
           expected_output = '201',/test_id = MT_NT_PTR_POST_014
           '''
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
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
        searcher.mturk_add_qats(job_id,self.result)
        time.sleep(10)
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
            "cars": [{"x1": "one", "y1": "one", "x2": "three", "y2": "four"}, {"x1": "one", "y1": "six", "x2": "eight", "y2": "twelve"}],
            "bikes": [{"x1": "five", "y1": "two", "x2": "six", "y2": "three"},{"x1": "seven", "y1": "nine", "x2": "eight", "y2": "ten"}]}

        result = json.dumps(result)
        post_result = user.MturkUser(hit_id,assignment_id,worker_id)
        response_string_type = post_result.mturk_post_task_result(task_id,result,token)
        expected_status_code = 406
        self.assertEqual(response_string_type.status_code,expected_status_code)


obj = TestMturkPostTaskResult()