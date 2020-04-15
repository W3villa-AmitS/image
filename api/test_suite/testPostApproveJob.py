from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import random
import string
import time


class TestPostApproveJob(SimpleTestCase):
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

    result = {
        "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                 {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                     "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                     "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

    def test_post_approve_job(self):
        '''
        description= 'Send HTTP POST job approve request using manager login
        at the endpoint  with valid username and password', \
        expected_output = '202',test_id = PT_AJ_POST_000
        '''

         #Creating a job using searcher credentials

        #Creating new job
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        #Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes', job_description='test2 job',
                         job_instructions='test2 job', task_max_occurrence='5', job_criteria_age_min='18',
                         job_criteria_age_max='60', job_criteria_location='India', job_initial_qats='2',
                         job_qat_frequency='5', job_criteria_gender= self.gender, job_criteria_grade='D',job_boxing_type='Rectangle')

        #Fetching job_id
        job_id = response_post_job.json()['job_id']
        #Adding wot's
        searcher.add_wots(job_id)
        #Adding qats
        re = searcher.add_qats(job_id,self.result)
        time.sleep(10)
        # # manager approves job
        manager = user.Manager(self.username_manager,self.password_manager)
        response_approval = manager.approve_job(job_id)
        expected_status_code = 202
        self.assertEqual(response_approval.status_code, expected_status_code)

        #for testing of already approved jobs by manager.

        manager = user.Manager(self.username_manager, self.password_manager)
        time.sleep(10)
        response_approval = manager.approve_job(job_id)
        expected_status_code = 400
        error = response_approval.json()['error']
        expected_error = "Can't 'approve' a job in state of 'approved'"
        self.assertEqual(error,expected_error)
        self.assertEqual(response_approval.status_code, expected_status_code)

    def test_post_approve_job_by_other_users(self):
        '''Description : Approving job by Admin,worker,searcher with
         valid credentials/ expected error : You do not have permission to perform this action
         / test_id = NT_AJ_POST_000'''

        # Creating new job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='5',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        # Fetching job_id
        job_id = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id)

        # Adding qats
        searcher.add_qats(job_id,self.result)

        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_searcher = searcher.approve_job(job_id)
        expected_status_code = 403
        error = response_searcher.json()['detail']
        expected_error = "You do not have permission to perform this action."
        self.assertEqual(response_searcher.status_cotestPostApprode, expected_status_code)
        self.assertEqual(error,expected_error)

        admin  = user.Administrator(self.username_admin, self.password_admin)
        response_admin = admin.approve_job(job_id)
        expected_status_code = 403
        error = response_admin.json()['detail']
        expected_error = "You do not have permission to perform this action."
        self.assertEqual(response_searcher.status_code, expected_status_code)
        self.assertEqual(error, expected_error)

        worker = user.Worker(self.username_worker, self.password_worker)
        response_worker = worker.approve_job(job_id)
        expected_status_code = 403
        error = response_worker.json()['detail']
        expected_error = "You do not have permission to perform this action."
        self.assertEqual(response_searcher.status_code, expected_status_code)
        self.assertEqual(error, expected_error)

    #Test job approval in case of job in initialized state

    def test_post_job_approve_in_initialized_state(self):
        '''Description :Send HTTP POST job approve Intialized job by manager with valid
        credentials / expected error : Can't 'approve' a job in state of initialized
        /test_id =  NT_AJ_POST_001'''

        # Creating new job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        # Fetching job_id
        job_id = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.approve_job(job_id)
        error = response_approval.json()['error']
        expected_error = "Can't 'approve' a job in state of 'being_created'"
        expected_status_code = 400
        self.assertEqual(expected_error,error)
        self.assertEqual(response_approval.status_code,expected_status_code)

    def test_post_job_approve_in_in_progress_state(self):
        '''Description : Approving IN_Progeress job by manager with valid
                credentials / expected error : "Can't 'approve' a job in state of 'in_progress'"
                /test_id =  NT_AJ_POST_002'''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        # Fetching job_id
        job_id = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id)
        # Adding qats
        searcher.add_qats(job_id,self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id)
        #Generating random string for user creation
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        username = x
        email = str(x) + '@idemia.com'
        # Creating new user to do job
        admin = user.Administrator(self.username_admin,self.password_admin)
        worker_new = admin.create_users(username,'Password@123',email,"A","W")
        username_worker_new = worker_new.json()['username']
        password = "Password@123"
        # worker login and perform task by posting self.result.
        time.sleep(10)
        worker = user.Worker(username_worker_new,password)
        response_task_id = worker.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        worker.post_task_result(task_id, result)

        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.approve_job(job_id)
        error = response_approval.json()['error']
        expected_error = "Can't 'approve' a job in state of 'in_progress'"
        expected_status_code = 400
        self.assertEqual(expected_error, error)
        self.assertEqual(response_approval.status_code, expected_status_code)





obj1 = TestPostApproveJob()



