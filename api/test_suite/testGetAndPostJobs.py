from django.test import SimpleTestCase
#import os,sys
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()


class TestGetAndPostJobs(SimpleTestCase):
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

# test whether all users can access the getjobs api
    def test_get_jobs_by_authorised_users(self):
        ''' Send HTTP GET jobs using authroised users login with valid credentials
        expecpetd_output = list of all jobs with details / 200'''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_getjob = searcher.get_jobs()
        expected_status_code = 200
        self.assertEqual(response_getjob.status_code,expected_status_code )

        worker = user.Worker(self.username_worker, self.password_worker)
        response_getjob = worker.get_jobs()
        expected_status_code = 200
        self.assertEqual(response_getjob.status_code, expected_status_code)

        manager = user.Manager(self.username_manager, self.password_manager)
        response_getjob = manager.get_jobs()
        expected_status_code = 200
        self.assertEqual(response_getjob.status_code, expected_status_code)

    def test_get_jobs_by_unauthorised_user(self):
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_get_job = admin.get_jobs()
        expected_error = 'You do not have permission to perform this action.'
        expected_status_code = 403
        self.assertEqual(response_get_job.status_code, expected_status_code)
        self.assertEqual(response_get_job.json()['detail'],expected_error)