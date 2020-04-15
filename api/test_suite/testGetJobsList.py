from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()


class TestGetJobsList(SimpleTestCase):
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

# test whether GET jobs api returns a list of jobs in case of admin,manager,searcher and worker login
    def test_get_jobs_list_by_different_users(self):
        '''
                description= 'Send HTTP GET jobs request using valid login
                at the endpoint  with valid username and password', \
                expected_output = '200',test_id = PT_JB_GET_000
                '''

        manager = user.Manager(self.username_manager,self.password_manager)
        response_getjobs = manager.get_jobs()
        expected_status_code = 200
        self.assertEqual(response_getjobs.status_code, expected_status_code)


        admin = user.Administrator(self.username_admin, self.password_admin)
        response_getjobs = admin.get_jobs()
        expected_status_code = 200
        self.assertEqual(response_getjobs.status_code, expected_status_code)


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_getjobs = searcher.get_jobs()
        expected_status_code = 200
        self.assertEqual(response_getjobs.status_code, expected_status_code)


        worker = user.Worker(self.username_worker, self.password_worker)
        response_getjobs = worker.get_jobs()
        expected_status_code = 200
        self.assertEqual(response_getjobs.status_code, expected_status_code)


obj1 = TestGetJobsList()


