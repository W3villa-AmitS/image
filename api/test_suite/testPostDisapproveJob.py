
from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import time
import string
import random


class TestPostDisapproveJob(SimpleTestCase):
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

    def test_post_disapprove_job(self):
        '''
        description= 'Send HTTP POST job disapprove request using manager login
        at the endpoint  with valid username and password', \
        expected_output = '202'/test_id = PT_DJ_POST_000',
        '''

        # Creating a job using searcher credentials
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
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
        searcher.add_qats(job_id, result)
        # # manager disapproves job
        time.sleep(10)
        manager = user.Manager(self.username_manager,self.password_manager)
        response_approval = manager.disapprove_job(job_id)
        expected_status_code = 202
        self.assertEqual(response_approval.status_code, expected_status_code)

    def test_post_disapprove_job_by_other_users(self):
        '''
               description= 'Send HTTP POST job disapprove request by unauthorised users
               at the endpoint  with valid username and password', \
               expected_output = '403 and You do not have permission to perform this action.
                '/test_id = NT_DJ_POST_000',
               '''

        # Creating a job using searcher credentials
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
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
        # Adding qats
        searcher.add_qats(job_id, result)

        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_disapprove_searcher = searcher.disapprove_job(job_id)
        error = response_disapprove_searcher.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code = 403
        self.assertEqual(error,expected_error)
        self.assertEqual(expected_status_code,response_disapprove_searcher.status_code)

        worker = user.Worker(self.username_worker, self.password_worker)
        response_disapprove_worker = worker.disapprove_job(job_id)
        error = response_disapprove_worker.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code = 403
        self.assertEqual(error, expected_error)
        self.assertEqual(expected_status_code, response_disapprove_worker.status_code)

        admin = user.Administrator(self.username_admin, self.password_admin)
        response_disapprove_admin = admin.disapprove_job(job_id)
        error = response_disapprove_admin.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code = 403
        self.assertEqual(error, expected_error)
        self.assertEqual(expected_status_code, response_disapprove_admin.status_code)

    def test_post_disapprove_job_by_invalid_job_id(self):
        '''
             description= 'Send HTTP POST job disapprove request by valid login and invalid job_id
            at the endpoint  with valid username and password', \
            expected_output = '403 and You do not have permission to perform this action.
                '/test_id = NT_DJ_POST_001',
                       '''

        # Creating a job using searcher credentials
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
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
        searcher.add_qats(job_id,result)

        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.disapprove_job(job_id+'asgah')
        expected_status_code = 404
        self.assertEqual(expected_status_code,response_approval.status_code)

    def test_post_disapprove_job_in_being_created_state(self):
        '''
                     description= 'Send HTTP POST job disapprove request by valid login and valid job_id
                     and the job is in being_created state at the endpoint  with valid username and password', \
                    expected_output = '403 and Can't 'disapprove' a job in state of 'being_created'
                        '/test_id = NT_DJ_POST_002',
                               '''

        # Creating a job using searcher credentials
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
        response_approval_initialized = manager.disapprove_job(job_id)
        error = response_approval_initialized.json()['error']
        expected_error = "Can't 'disapprove' a job in state of 'being_created'"
        expected_error_code = 400
        self.assertEqual(response_approval_initialized.status_code,expected_error_code)
        self.assertEqual(error,expected_error)

    def test_post_disapprove_job_in_in_progress_state(self):
        '''Description : Approving Intialized job by manager with valid
                credentials / expected error :Can't 'approve' a job in state of 'being_created
                /test_id = NT_DJ_POST_003'''

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
        self.assertEqual(expected_error, error)
        self.assertEqual(response_approval.status_code, expected_status_code)

    def test_post_job_disapprove_ongoing_job(self):
        '''Description : Approving IN_Progeress job by manager with valid
                credentials / expected error : "Can't 'approve' a job in state of 'in_progress'"
                /test_id =  NT_DJ_POST_004'''

        # Creating a job using searcher credentials

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
        # Adding qats
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
        searcher.add_qats(job_id,result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id)
        # Generating random string for user creation
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        username = x
        email = str(x) + '@idemia.com'
        # Creating new user to do job
        admin = user.Administrator(self.username_admin, self.password_admin)
        worker_new = admin.create_users(username, 'Password@123', email, "A", "W")
        username_worker_new = worker_new.json()['username']
        password = "Password@123"
        # worker login and perform task by posting result.
        time.sleep(5)
        worker = user.Worker(username_worker_new,password)
        response_task_id = worker.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        worker.post_task_result(task_id, result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.disapprove_job(job_id)
        error = response_approval.json()['error']
        expected_error = "Can't 'disapprove' a job in state of 'in_progress'"
        expected_status_code = 400
        self.assertEqual(expected_error, error)
        self.assertEqual(response_approval.status_code, expected_status_code)


obj1 = TestPostDisapproveJob()


