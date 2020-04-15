from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import time


class TestGetRandomTaskFromJob(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    count = 0
    gender = '"M","F"'

    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'

    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    '''
           description= 'Send HTTP POST job request using searcher login
           at the endpoint  with valid username and password', \
           expected_output = '201',
           '''
    result = {
        "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                 {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                     "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                     "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

    searcher = user.Searcher(username_searcher, password_searcher)

    response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                         job_description='test2 job',
                                         job_instructions='test2 job', task_max_occurrence='5',
                                         job_criteria_age_min='18',
                                         job_criteria_age_max='60', job_criteria_location='India', job_initial_qats='2',
                                         job_qat_frequency='5', job_criteria_gender=gender, job_criteria_grade='D',
                                         job_boxing_type='Rectangle')
    #Fetching job_id
    job_id = response_post_job.json()['job_id']
    #Adding wots
    searcher.add_wots(job_id)
    searcher.add_qats(job_id,result)
    time.sleep(10)
    # manager approves job
    manager = user.Manager(username_manager, password_manager)
    response_approval = manager.approve_job(job_id)

    def test_random_task_from_job_worker(self):
        '''
        description= 'Send HTTP Get random task request using worker login
        at the endpoint  with valid username and password', \
        expected_output = '200',/test_id = PT_GT_GET_000
        '''

        # Get a random task from the job specified as {job_id} using worker credentials
        worker = user.Worker(self.username_worker,self.password_worker)
        response_get_random_task = worker.get_random_task(self.job_id)
        # if worker is already engaged on other job then first disengaged worker form current job then proceed.
        if response_get_random_task.status_code == 400 and response_get_random_task.json()['error'] == "Worker already active on another job.":
            worker.post_disengage_job(response_get_random_task.json()['job_id'])
            response_after_dis_get_random_task = worker.get_random_task(self.job_id)

            expected_status_code = 200
            self.assertEqual(response_after_dis_get_random_task.status_code, expected_status_code)
    def test_random_task_by_another_user(self):
        '''
                description= 'Send HTTP GET random task request using other user login
                at the endpoint  with valid username and password', \
                expected_output = '403',& "You do not have permission to perform this action."
                test_id = NT_GT_GET_000'''
        # Get a random task from the job specified as {job_id} using manager credentials.
        manager = user.Manager(self.username_manager, self.password_manager)
        response_manager = manager.get_random_task(self.job_id)
        error = response_manager.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code =  403
        self.assertEqual(error,expected_error)
        self.assertEqual(expected_status_code,response_manager.status_code)

        # Get a random task from the job specified as {job_id} using searcher credentials.
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_searcher = searcher.get_random_task(self.job_id)
        error = response_searcher.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code = 403
        self.assertEqual(error, expected_error)
        self.assertEqual(expected_status_code, response_searcher.status_code)

        # Get a random task from the job specified as {job_id} using admin credentials.
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_admin = admin.get_random_task(self.job_id)
        error = response_admin.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code = 403
        self.assertEqual(error, expected_error)
        self.assertEqual(expected_status_code, response_admin.status_code)

    def test_get_task_by_unapproved_job(self):
        '''
                        description= 'Send HTTP GET random task request using worker login
                        at the endpoint  with valid username and password passing unapproved_job_id', \
                        expected_output = '403',& 'Job is not yet approved.test_id = NT_GT_GET_001'
                        '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
        searcher = user.Searcher(self.username_searcher, self.password_searcher)

        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender = self.gender, job_criteria_grade='D',
                                             job_boxing_type='Rectangle')
        # Fetching job_id
        job_id = response_post_job.json()['job_id']
        # Adding wots
        searcher.add_wots(job_id)

        searcher.add_qats(job_id, result)
        worker = user.Worker(self.username_worker, self.password_worker)
        response_get_random_task = worker.get_random_task(self.job_id)
        if response_get_random_task.status_code == 400 and response_get_random_task.json()['error'] == "Worker already active on another job.":
            worker.post_disengage_job(response_get_random_task.json()['job_id'])
            response_after_dis_get_random_task = worker.get_random_task(job_id)
            expected_error = 'Job is not yet approved.'
            expected_status_code = 403
            self.assertEqual(expected_status_code,response_after_dis_get_random_task.status_code)
            self.assertEqual(expected_error,response_after_dis_get_random_task.json()['error'])

    def test_get_task_by_null_job_id(self):

        '''
           description= 'Send HTTP GET random task request using worker login
             at the endpoint  with valid username and password passing null_job_id', \
            expected_output = '400',& "job_id is not provided/test_id = NT_GT_GET_002"
                               '''
        worker = user.Worker(self.username_worker, self.password_worker)
        job_id = ""
        response_after_dis_get_random_task = worker.get_random_task(job_id)
        expected_error = "job_id is not provided"
        expected_status_code = 400
        self.assertEqual(expected_status_code, response_after_dis_get_random_task.status_code)
        self.assertEqual(expected_error, response_after_dis_get_random_task.json()['error'])

    def test_get_random_task_on_not_active_job_id(self):

        '''
           description= 'Send HTTP GET random task request using worker login
             at the endpoint  with valid username and password passing not active_job_id', \
            expected_output = '400',& "Worker already active on another job/test_id = NT_GT_GET_003."
                               '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)

        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender = self.gender, job_criteria_grade='D',
                                             job_boxing_type='Rectangle')
        # Fetching job_id
        job_id_new = response_post_job.json()['job_id']
        # Adding wots
        searcher.add_wots(job_id_new)

        searcher.add_qats(job_id_new,result)
            # manager approves job
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id_new)
        time.sleep(10)
        worker = user.Worker(self.username_worker, self.password_worker)
        response_get_random_task = worker.get_random_task(job_id_new)
        error = response_get_random_task.json()['error']
        expected_error =  'Worker already active on another job.'
        self.assertEqual(expected_error,error)
        expected_status_code = 400
        self.assertEqual(expected_status_code,response_get_random_task.status_code)

obj1 = TestGetRandomTaskFromJob()



