from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import random,string,time

class TestEngagedWorker(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    
    gender = '"M","F"'

    username_searcher = 'searcher1'
    username_manager = 'manager1'
    username_worker = 'worker1'
    username_admin = 'sharedadmin'

    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    # Creating new job for testing.
    searcher = user.Searcher(username_searcher, password_searcher)
    response = searcher.add_job(job_name='new job', job_type='P', job_attributes='cars',
                                job_description='Mark the cars', job_instructions='Mark the cars',
                                task_max_occurrence='5', job_criteria_age_min='18', job_criteria_age_max='60',
                                job_criteria_location='India', job_initial_qats='2', job_qat_frequency='5',
                                job_criteria_gender=gender, job_criteria_grade='A',job_boxing_type='Rectangle')

    job_id = response.json()['job_id']
    response_add_wots = searcher.add_wots(job_id)
    result = {
        "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                 {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                     "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                     "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
    response_add_qat = searcher.add_qats(job_id,result)
    time.sleep(10)
    # Manager approves new job.
    manager = user.Manager(username_manager,password_manager)
    response = manager.approve_job(job_id)
    time.sleep(10)
    # Worker perfoms task
    worker = user.Worker(username_worker,password_worker)
    response_random_task = worker.get_random_task(job_id)
    response_code = response.status_code
    job_id_new = response.json()['job_id']

    # If the worker already engaged on any other job then.
    # First disengage the worker from the current job and then proceed.
    if response_code == 400 :
        response = worker.disengage_worker(job_id_new)

    # Now check the workers engaged on a particular job by valid user.

    def test_engaged_worker_by_valid_user(self):
        '''description= 'Send HTTP GET worker engaged request using valid users login
                        at the endpoint  with valid username and password'
                            expected_output = '200'/test_id =PT_WE_GET_000,
                                              '''

        # Checking through manager login.
        manager = user.Manager(self.username_manager,self.password_manager)
        response_manager = manager.engaged_worker(self.job_id)
        expected_status_code = 200
        self.assertEqual(response_manager.status_code,expected_status_code)

        # Checking through searcher login.
        searcher = user.Searcher(self.username_searcher ,self.password_searcher)
        response_searcher = searcher.engaged_worker(self.job_id)
        expected_status_code = 200
        self.assertEqual(response_searcher.status_code, expected_status_code)

    # Now check the enageged worker by a invalid users.
    def test_engaged_worker_by_invalid_user(self):
        '''description= 'Send HTTP GET worker engaged request using invalid users login
                                at the endpoint  with valid username and password'
                                    expected_output = '403'/test_id = NT_WE_GET_000,
                                                      '''

        # Checking through a worker login
        worker = user.Worker(self.username_worker, self.password_worker)
        response_worker = worker.engaged_worker(self.job_id)
        expected_error = 'You do not have permission to perform this action.'
        expected_status_code = 403
        self.assertEqual(response_worker.status_code, expected_status_code)
        self.assertEqual(response_worker.json()['detail'],expected_error)
        # Checking through a Administrator login
        Admin = user.Administrator(self.username_admin, self.password_admin)
        response_admin = Admin.engaged_worker(self.job_id)
        expected_error = 'You do not have permission to perform this action.'
        expected_status_code = 403
        self.assertEqual(response_admin.status_code, expected_status_code)
        self.assertEqual(response_admin.json()['detail'],expected_error)

    def test_engaged_worker_by_invalid_job_id(self):
        '''description= 'Send HTTP GET worker engaged request using valid users login and invalid job_id
                                        at the endpoint  with valid username and password'
                                            expected_output = '404'/test_id = NT_WE_GET_001,
                                                              '''

        manager = user.Manager(self.username_manager,self.password_manager)
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 8
        job_id = ''.join(random.sample(random_string, stringLength))
        response_invalid_job_id = manager.engaged_worker(job_id)
        expected_status_code = 404
        self.assertEqual(expected_status_code,response_invalid_job_id.status_code)

    def test_engaged_worker_by_null_job_id(self):
        '''description= 'Send HTTP GET worker engaged request using valid users login and null job_id
                                at the endpoint  with valid username and password'
                                expected_output = '400'/test_id = NT_WE_GET_002,
                                                                      '''

        manager = user.Manager(self.username_manager,self.password_manager)
        null_job_id = ' '
        response_null_id = manager.engaged_worker(null_job_id)
        expected_status_code = 400
        error = response_null_id.json()['error']
        expected_error = "Invalid or no job_id's specified."
        self.assertEqual(error,expected_error)
        self.assertEqual(expected_status_code,response_null_id.status_code)

    def test_engaged_worker_by_disapproved_job(self):
        '''description= 'Send HTTP GET worker engaged request using valid users login on disapproved job
                                        at the endpoint  with valid username and password'
                                        expected_output = '200'/test_id = NT_WE_GET_003,
                                                                              '''

        manager = user.Manager(self.username_manager,self.password_manager)
        manager.disapprove_job(self.job_id)
        response_disapproved = manager.engaged_worker(self.job_id)
        expected_status_code = 200
        self.assertEqual(response_disapproved.status_code,expected_status_code)
        manager.approve_job(self.job_id)

    def test_engaged_worker_on_disengaged_job_id(self):
        '''description= 'Send HTTP GET worker engaged request using valid users login and disengaged job_id
                                        at the endpoint  with valid username and password'
                                        expected_output = '200'/test_id = NT_WE_GET_004,
                                                                              '''
        manager = user.Manager(self.username_manager,self.password_manager)
        response_disengage = manager.engaged_worker(self.job_id_new)
        expected_status_code = 200
        self.assertEqual(response_disengage.status_code, expected_status_code)

    def test_engaged_worker_on_initialized_job(self):
        '''description= 'Send HTTP GET worker engaged request using valid users login and intialized    job_id
                                                at the endpoint  with valid username and password'
                                                expected_output = '200'/test_id = NT_WE_GET_005,
                                                                                      '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response = searcher.add_job(job_name='new job', job_type='P', job_attributes='cars',
                                    job_description='Mark the cars', job_instructions='Mark the cars',
                                    task_max_occurrence='5', job_criteria_age_min='18', job_criteria_age_max='60',
                                    job_criteria_location='India', job_initial_qats='2', job_qat_frequency='5',
                                    job_criteria_gender = self.gender, job_criteria_grade='A', job_boxing_type='Rectangle')

        job_id = response.json()['job_id']
        searcher.add_wots(job_id)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_initialized = manager.engaged_worker(job_id)
        expected_status_code = 200
        self.assertEqual(response_initialized.status_code, expected_status_code)


ob = TestEngagedWorker()