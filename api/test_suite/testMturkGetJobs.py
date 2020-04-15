from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()



class TestMturkGetJob(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    count = 0

    username_manager='manager1'
    username_admin='sharedadmin'
    username_searcher='searcher1'
    username_worker='worker1'

    password_manager='Insidethepyramid@2'
    password_admin='WY+e5nsQg-43565!'
    password_searcher='Belowthepyramid@2'
    password_worker='Nearthepyramid@2'

# test whether GET jobs api returns a list of jobs in case of manager login

    def test_mturk_get_job_list_by_manager_login(self):
        '''description= 'Send HTTP GET job request using manager login
            at the endpoint ', \expected_output = '200'
                test_id = MT_PT_JL_GET_000'''

        manager = user.Manager(self.username_manager,self.password_manager)
        response_get_jobs = manager.mturk_get_jobs()
        expected_status_code = 200
        self.assertTrue(response_get_jobs)
        self.assertEqual(response_get_jobs.status_code, expected_status_code)

    def test_mturk_get_job_by_invalid_access_token(self):
        '''
            description= 'Send HTTP GET job request using manager login
            at the endpoint  with invalid access_token', \
            expected_output = '403'/Invalid or expired token,test_id = MT_NT_JL_GET_000
         '''
        manager = user.Manager(self.username_manager, self.password_manager)
        token = manager.access_token + "abc"
        response_get_jobs = userApisMturk.mturk_get_jobs(token)
        expected_status_code = 403
        expected_error_message = 'Invalid or expired token.'
        self.assertTrue(response_get_jobs.status_code == expected_status_code and response_get_jobs.json()['detail'] == expected_error_message)

        self.assertEqual(response_get_jobs.status_code, expected_status_code)

    def test_mturk_get_job_list_by_searcher_login(self):
        '''
             description= 'Send HTTP GET job request using searcher login
             at the endpoint ', \
             expected_output = '200',test_id = MT_PT_JL_GET_001
        '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_get_jobs = searcher.mturk_get_jobs()
        expected_status_code = 200
        self.assertTrue(response_get_jobs)
        self.assertEqual(response_get_jobs.status_code, expected_status_code)

    def test_mturk_get_job_list_by_worker_login(self):
        '''
             description= 'Send HTTP GET job request using worker login
             at the endpoint ', \
             expected_output = '400',test_id = MT_PT_JL_GET_002
        '''

        worker = user.Worker(self.username_searcher, self.password_searcher)
        response_get_jobs = worker.mturk_get_jobs()
        expected_status_code = 200
        self.assertTrue(response_get_jobs)
        self.assertEqual(response_get_jobs.status_code, expected_status_code)

    def test_mturk_get_job_list_by_admin_login(self):
        '''
             description= 'Send HTTP GET job request using worker login
             at the endpoint ', \
             expected_output = '400',test_id = MT_PT_JL_GET_003
        '''

        admin = user.Administrator(self.username_admin, self.password_admin)
        response_get_jobs = admin.mturk_get_jobs()
        expected_status_code = 200
        self.assertTrue(response_get_jobs)
        self.assertEqual(response_get_jobs.status_code, expected_status_code)

    def test_mturk_get_job_list_without_login(self):
        '''
             description= 'Send HTTP GET job request without users login
             at the endpoint ', \
             expected_output = '400',test_id = MT_PT_JL_GET_004
        '''

        response_get_jobs = user.mturk_get_jobs()
        expected_status_code = 200
        self.assertTrue(response_get_jobs)
        self.assertEqual(response_get_jobs.status_code, expected_status_code)


obj1 = TestMturkGetJob()
