from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import string,random

class TestGetDetailsOfJobs(SimpleTestCase):
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

    # searcher credentials
    searcher = user.Searcher(username_searcher, password_searcher)

    # add job
    response_post_job = searcher.add_job(job_name='test5 job', job_type='P', job_attributes='cars,bus',
                                         job_description='test5 job',
                                         job_instructions='test5 job', task_max_occurrence='5',
                                         job_criteria_age_min='18',
                                         job_criteria_age_max='60', job_criteria_location='India',
                                         job_initial_qats='2',
                                         job_qat_frequency='5', job_criteria_gender=gender,
                                         job_criteria_grade='D',job_boxing_type='Rectangle')



# test whether GET job with {job_id} api returns detail of job with respect to job_id
    def test_get_details_of_jobs_with_different_user_and_valid_id(self):
        '''
                description= 'Send HTTP GET job request using valid login and valid job_id
                at the endpoint, \
                expected_output = '200',test_id = PT_JD_GET_000
                '''
        self.job_id = self.response_post_job.json()['job_id']
        manager = user.Manager(self.username_manager,self.password_manager)
        response_get_job_with_job_id = manager.get_job_with_id(self.job_id)
        expected_status_code = 200
        self.assertEqual(response_get_job_with_job_id.status_code, expected_status_code)

        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_get_job_with_job_id = searcher.get_job_with_id(self.job_id)
        expected_status_code = 200
        self.assertEqual(response_get_job_with_job_id.status_code, expected_status_code)

        worker = user.Worker(self.username_worker,self.password_worker)
        response_get_job_with_job_id = worker.get_job_with_id(self.job_id)
        expected_status_code = 200
        self.assertEqual(response_get_job_with_job_id.status_code, expected_status_code)


# test whether GET job with {job_id} api returns Not found 404 in case of invalid job_id
    def test_get_details_of_job_with_invalid_user_and_inValid_id(self):
        '''
                       description= 'Send HTTP GET job request using invalid user and invalid job_id
                       at the endpoint, \
                       expected_output = '200',test_id = NT_JD_GET_000
                       '''
        #Generating random string for invalid job_id
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 8
        invalid_job_id = ''.join(random.sample(random_string, stringLength))

        manager = user.Manager(self.username_manager,self.password_manager)
        response_get_job_with_job_id = manager.get_job_with_id(invalid_job_id)
        expected_status_code = 404
        self.assertEqual(response_get_job_with_job_id.status_code, expected_status_code)

        admin = user.Administrator(self.username_admin,self.password_admin)
        response_get_job_with_job_id = admin.get_job_with_id(invalid_job_id)
        expected_status_code = 403
        self.assertEqual(response_get_job_with_job_id.status_code, expected_status_code)

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_get_job_with_job_id = searcher.get_job_with_id(invalid_job_id)
        expected_status_code = 404
        self.assertEqual(response_get_job_with_job_id.status_code, expected_status_code)

        worker = user.Worker(self.username_worker,self.password_worker)
        response_get_job_with_job_id = worker.get_job_with_id(invalid_job_id)
        expected_status_code = 404
        self.assertEqual(response_get_job_with_job_id.status_code, expected_status_code)






