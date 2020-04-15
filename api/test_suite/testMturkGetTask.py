import random
import string

from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
import urllib3,time,json
urllib3.disable_warnings()

class TestMturkGetTask(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    count = 0

    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'

    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    def id_generator(self,size=8, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


    def test_mturk_get_task_by_valid_parameters(self):
        '''
      description= 'Send HTTP GET get task using worker login with valid parameters', \
      expected_output = '200',test_id = MT_PT_GT_GET_000
      '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                         job_description='Testing',
                                         job_max_occurrence='10', job_assignment_duration='10',
                                         job_lifetime_duration='365',
                                         job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                         job_boxing_type='Rectangle')


        expected_status_code = 201
        self.assertEqual(response_post_job.status_code, expected_status_code)
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        searcher.mturk_add_qats(self.job_id,result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']

        assignment_id = self.id_generator()
        mturk_worker = user.MturkWorker(self.hit_id, assignment_id, 'SAMPLEWORKER')
        session_token_found = mturk_worker.export_session_token()
        expected_status_code = 200
        response_get_token = mturk_worker.export_response()
        self.assertEqual(response_get_token.status_code, expected_status_code)
        response_get_task = mturk_worker.mturk_get_task(session_token_found)
        self.assertEqual(response_get_task.status_code, expected_status_code)
        self.task_id = response_get_task.json()['task_id']
        self.tasks_completed = response_get_task.json()['tasks_completed']
        self.image_url = response_get_task.json()['image_url']

        try:
            if self.task_id is None:
                print('self.task_id has no value')
        except NameError:
            print('self.task_id is not defined')
            assert (False)
        # else:
        #     print('self.task_id ' + str(self.task_id))
        try:
            if self.tasks_completed is None:
                print('self.tasks_completed has no value')
        except NameError:
            print('self.tasks_completed is not defined')
            assert (False)
        # else:
        #     print('self.tasks_completed ' + str(self.tasks_completed))
        try:
            if self.image_url is None:
                print('self.image_url has no value')
        except NameError:
            print('self.image_url is not defined')
            assert (False)
        # else:
        #     print('self.image_url ' + str(self.image_url))
        try:
            if response_get_task.json()['job_type'] is None:
                print('self.job_type has no value')
        except NameError:
            print('self.job_type is not defined')
            assert (False)
        else:
            self.assertEqual(response_get_task.json()['job_type'], 'P')

        try:
            if response_get_task.json()['job_attributes'] is None:
                print('self.job_attributes has no value')
        except NameError:
            print('self.job_attributesis not defined')
            assert (False)
        else:
            self.assertEqual(response_get_task.json()['job_attributes'], 'cars,bikes')

        try:
            if response_get_task.json()['job_boxing_type'] is None:
                print('self.job_boxing_type has no value')
        except NameError:
            print('self.job_boxing_type not defined')
            assert (False)
        else:
            self.assertEqual(response_get_task.json()['job_boxing_type'], 'Rectangle')
        try:
            if response_get_task.json()['total_tasks'] is None:
                print('self.total_tasks has no value')
        except NameError:
            print('self.total_tasks not defined')
            assert (False)
        else:
            self.assertEqual(response_get_task.json()['total_tasks'], '3')


    def test_mturk_get_task_by_invalid_token(self):
        '''
      description= 'Send HTTP GET get task using worker login with invalid_token', \
      expected_output = '401',test_id = MT_NT_GT_GET_000
      '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                         job_description='Testing',
                                         job_max_occurrence='10', job_assignment_duration='10',
                                         job_lifetime_duration='365',
                                         job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                         job_boxing_type='Rectangle')


        expected_status_code = 201
        self.assertEqual(response_post_job.status_code, expected_status_code)
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id,result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']

        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id, 'SAMPLEWORKER')
        session_token_found = mturk_worker.mturk_get_token(self.hit_id, assignment_id, 'SAMPLEWORKER')
        token = session_token_found.json()['token']
        invalid_session_token_found = token + 'Qw2exx3'
        expected_status_code = 401
        response_get_task = mturk_worker.mturk_get_task(invalid_session_token_found)
        expected_error = 'Signature verification failed'
        self.assertEqual(expected_error,response_get_task.json()['error'])
        self.assertEqual(response_get_task.status_code, expected_status_code)


    def test_mturk_get_task_by_null_token(self):
        '''
      description= 'Send HTTP GET get task using worke login with null_token', \
      expected_output = '401',test_id = MT_NT_GT_GET_001
      '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201
        self.assertEqual(response_post_job.status_code, expected_status_code)
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id, 'SAMPLEWORKER')
        mturk_worker.mturk_get_token(self.hit_id, assignment_id, 'SAMPLEWORKER')
        null_token = " "
        expected_status_code = 401
        response_get_task = mturk_worker.mturk_get_task(null_token)
        expected_error = response_get_task.json()['error']
        self.assertEqual(expected_error,response_get_task.json()['error'])
        self.assertEqual(response_get_task.status_code, expected_status_code)


    def test_mturk_get_task_by_list_of_token(self):
        '''
      description= 'Send HTTP GET get task using worke login with list of token', \
      expected_output = '400',test_id = MT_NT_GT_GET_002
      '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201
        self.assertEqual(response_post_job.status_code, expected_status_code)
        self.job_id = response_post_job.json()['job_id']
        re = searcher.mturk_add_wots(self.job_id)
        res = searcher.mturk_add_qats(self.job_id, result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']

        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id, 'SAMPLEWORKER')
        session_token_found = mturk_worker.mturk_get_token(self.hit_id, assignment_id, 'SAMPLEWORKER')
        token_list = []
        token_list.append(session_token_found)
        expected_status_code = 401
        response_get_task = mturk_worker.mturk_get_task(token_list)
        expected_error = 'Invalid token header'
        self.assertEqual(expected_error,response_get_task.json()['error'])
        self.assertEqual(response_get_task.status_code, expected_status_code)

    def test_mturk_get_task_by_used_token(self):
        '''
      description= 'Send HTTP GET get task with used jwt token', \
      expected_output = '204',test_id = MT_NT_GT_GET_004
      '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='1', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='1', job_tasks_per_hit='2',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201
        self.assertEqual(response_post_job.status_code, expected_status_code)
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        hit_id = response_approval.json()['hits_created']

        assignment_id = self.id_generator()
        worker_id_first = "SAMPLEWORKERQA"

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
        response_task_third = mturk.mturk_get_task(token)
        expected_status_code = 204
        self.assertEqual(response_task_third.status_code, expected_status_code)

    def test_mturk_get_task_by_invalid_url(self):
        '''
            description= 'Send HTTP GET get task with invalid url', \
            expected_output = '200',test_id = MT_NT_GT_GET_005
            '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201
        self.assertEqual(response_post_job.status_code, expected_status_code)
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']

        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id, 'SAMPLEWORKER')
        session_token_found = mturk_worker.mturk_get_token(self.hit_id, assignment_id, 'SAMPLEWORKER')
        #For testing with wrong URL
        response_get_task = mturk_worker.mturk_get_task_testing(session_token_found)
        expected_status_code = 404
        self.assertEqual(response_get_task.status_code, expected_status_code)

obj1 = TestMturkGetTask()

#obj1.test_post_job_by_searcher_login()



