from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import time

class TestDisengageWorker(SimpleTestCase):

    dynamo = dynamoDatabase.Database()

    #Usernames
    username_searcher = 'searcher1'
    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_worker = 'worker1'
    gender = '"M","F"'
    #password
    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    result = {"qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
        "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
        "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                       {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                           "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                           "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

    # Creating a  new job for a test case.

    searcher = user.Searcher(username_searcher, password_searcher)
    response = searcher.add_job(job_name='new job', job_type='P', job_attributes='cars,bikes',
                                job_description='Mark the cars', job_instructions='Mark the cars',
                                task_max_occurrence='5', job_criteria_age_min='18', job_criteria_age_max='60',
                                job_criteria_location='India', job_initial_qats='2', job_qat_frequency='5',
                                job_criteria_gender = gender, job_criteria_grade='A',job_boxing_type='Rectangle')

    # Fetching job_id for further use.
    job_id = response.json()['job_id']
    # Adding wot's
    # import pdb;pdb.set_trace()
    response_add_wots = searcher.add_wots(job_id)
    time.sleep(5)
    response_add_qats = searcher.add_qats(job_id,result)
    # Managers approves job
    time.sleep(10)
    manager = user.Manager(username_manager,password_manager)
    response_manager_approve = manager.approve_job(job_id)

    time.sleep(10)
    #login by worker to perfom task
    worker_new = user.Worker(username_worker, password_worker)
    #Get task_id from job_id to post result
    response_task_id = worker_new.get_random_task(job_id)
    if response_task_id.status_code == 400:
        jobid = response_task_id.json()['job_id']
        response = worker_new.post_disengage_job(jobid)
    else:
        response_task_id = worker_new.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        result_worker = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
              "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                        {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        response_post_result = worker_new.post_task_result(task_id, result_worker)

    def test_disengage_by_valid_user(self):
        '''
             description= 'Send HTTP POST job disengage request using worker login
                     at the endpoint  with valid job id', \
                     expected_output = '202'/test_id= PT_DW_POST_000,
                     '''
        time.sleep(10)
        worker = user.Worker(self.username_worker,self.password_worker)
        response_disengage_by_worker = worker.post_disengage_job(self.job_id)
        expected_status_code = 202
        self.assertEqual(response_disengage_by_worker.status_code,expected_status_code)

    def test_disengage_by_invalid_user(self):
        '''description= 'Send HTTP POST job disengage request using invalid users login
                     at the endpoint  with valid username and password', \
                         expected_output = '403'/test_id =NT_DW_POST_000,
                              '''

        #disengage by admin
        admin = user.Administrator(self.username_admin,self.password_admin)
        response_disengage_by_admin = admin.post_disengage_job(self.job_id)
        expected_status_code = 403
        self.assertEqual(expected_status_code,response_disengage_by_admin.status_code)
        expected_error = "You do not have permission to perform this action."
        error = response_disengage_by_admin.json()['detail']
        self.assertEqual(expected_error,error)
        #disengage by manager
        manager = user.Manager(self.username_manager, self.password_manager)
        response_disengage_by_manager = manager.post_disengage_job(self.job_id)
        expected_status_code = 403
        self.assertEqual(expected_status_code, response_disengage_by_manager.status_code)
        expected_error = "You do not have permission to perform this action."
        error = response_disengage_by_admin.json()['detail']
        self.assertEqual(expected_error, error)
        #Disengage by searcher
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_disengage_by_searcher = searcher.post_disengage_job(self.job_id)
        expected_status_code = 403
        self.assertEqual(expected_status_code, response_disengage_by_searcher.status_code)
        expected_error = "You do not have permission to perform this action."
        error = response_disengage_by_admin.json()['detail']
        self.assertEqual(expected_error, error)


    def test_disengage_by_invalid_job_id(self):

        '''description= 'Send HTTP POST job disengage request using valid users login
                     at the endpoint  with valid username and password' on invalid job_id \
                         expected_output = '404'/test_id =  NT_DW_POST_001,
                              '''

        worker = user.Worker(self.username_worker, self.password_worker)
        # worker.post_task_result(self.task_id,self.result)
        response_disengage_by_worker = worker.post_disengage_job(self.job_id+'afgs')
        error = response_disengage_by_worker.json()['error']
        expected_status_code = 404
        expected_error = "Unable to find worker allocation on job with specified job_id."
        self.assertEqual(response_disengage_by_worker.status_code, expected_status_code)
        self.assertEqual(error,expected_error)

    def test_disengage_on_null_job_id(self):
        '''description= 'Send HTTP POST job disengage request using valid users login
                             at the endpoint  with on null job_id \
                                 expected_output = '400'/test_id =NT_DW_POST_002,
                                      '''

        worker = user.Worker(self.username_worker, self.password_worker)
        job_id = ' '
        response_null_job_id = worker.post_disengage_job(job_id)
        error = response_null_job_id.json()['error']
        expected_error = 'Unable to find worker allocation on job with specified job_id.'
        expected_status_code = 404
        self.assertEqual(error,expected_error)
        self.assertEqual(expected_status_code,response_null_job_id.status_code)

    def test_disengage_worker_on_not_active_job(self):
        '''description= 'Send HTTP POST job disengage request using valid users login
                             at the endpoint  with valid username and password' on not acitve job_id \
                                 expected_output = '400'/test_id =NT_DW_POST_003,
                                      '''
        worker = user.Worker(self.username_worker,self.password_worker)
        response_not_active_job_id = worker.post_disengage_job(self.job_id)
        error = response_not_active_job_id.json()['error']
        expected_error =  'Worker is not active on this job.'
        expected_status_code = 400
        self.assertEqual(error,expected_error)
        self.assertEqual(expected_status_code,response_not_active_job_id.status_code)

    def test_disengage_with_invalid_acces_token(self):
        '''
             description= 'Send HTTP POST job disengage request using worker login
                     at the endpoint  with valid job id', \
                     expected_output = '202'/test_id= PT_DW_POST_000,
                     '''
        time.sleep(10)
        worker = user.Worker(self.username_worker,self.password_worker)
        response_disengage_by_worker = worker.post_disengage_job(self.job_id)
        expected_status_code = 403
        self.assertEqual(response_disengage_by_worker.status_code,expected_status_code)