from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()


class TestListJobByStatus(SimpleTestCase):


    dynamo = dynamoDatabase.Database()
    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'

    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'




    # Listing jobs by different status through a valid users.

    def test_find_job_by_status_by_valid_user(self):
        '''
                        description= 'Send HTTP GET jobs request using valid login
                        at the endpoint  with valid username and password', \
                        expected_output = '200',test_id = PT_JL_GET_000
                        '''

        job_status =["initialized",  # a freshly created job
         "being_created",  # Celery is scheduled to add multiple QATS/WOTS asynchronously
         "finalized",  # QAT condition met
         "approved",  # job approved by a manager
         "disapproved",  # job disapproved by a manager
         "in_progress",  # job is in-progress
         "completed",  # job is completed by workers
         "validated",  # job is validated by searcher
         "rejected"  # job results are discarded by searcher
         ]
        i = 0
        while i < len(job_status):

            # Get a list of job using worker credentials on the basis of job_status
            worker = user.Worker(self.username_worker, self.password_worker)
            response = worker.get_job_status_list('approved')
            expected_status_code = 200
            self.assertEqual(response.status_code,expected_status_code)

            # Get a list of job using searcher credentials on the basis of job_status
            searcher = user.Searcher(self.username_searcher, self.password_searcher)

            response = searcher.get_job_status_list(job_status[i])
            expected_status_code = 200
            self.assertEqual(response.status_code, expected_status_code)

            # Get a list of job using manager credentials on the basis of job_status
            manager = user.Manager(self.username_manager, self.password_manager)

            response = manager.get_job_status_list(job_status[i])
            expected_status_code = 200
            self.assertEqual(response.status_code, expected_status_code)

            # Get a list of job using Administrator credentials on the basis of job_status
            admin = user.Administrator(self.username_admin, self.password_admin)
            response = admin.get_job_status_list(job_status[i])
            expected_error =  'You do not have permission to perform this action.'
            expected_status_code = 403
            self.assertEqual(expected_error,response.json()['detail'])
            self.assertEqual(response.status_code, expected_status_code)
            i += 1

