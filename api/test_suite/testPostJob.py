from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
import json
urllib3.disable_warnings()


class TestPostJob(SimpleTestCase):
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

    def test_post_job_by_searcher_login(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint  with all parameters', \
      expected_output = '201',test_id = PT_JP_POST_000
      '''

        result = {"qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'","result": {
                "cars": [{"x1": "95","y1": "267","x2": "197","y2": "340"}],
                "bikes": [{"x1": "95","y1": "267","x2": "197","y2": "340"}]}},
        {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'","result": {
                "cars": [{"x1": "95","y1": "267","x2": "197","y2": "340"}],
                "bikes": [{"x1": "95","y1": "267","x2": "197","y2": "340"}]}}]}
        searcher = user.Searcher(self.username_searcher, self.password_searcher)

        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                         job_description='test2 job',
                                         job_instructions='test2 job', task_max_occurrence='2',
                                         job_criteria_age_min='18',
                                         job_criteria_age_max='60', job_criteria_location='India', job_initial_qats='2',
                                         job_qat_frequency='5', job_criteria_gender=self.gender, job_criteria_grade='D',job_boxing_type='Rectangle')

        expected_status_code = 201
        self.job_id = response_post_job.json()['job_id']
        searcher.add_wots(self.job_id)
        res = searcher.add_qats(self.job_id, result)
        self.assertEqual(response_post_job.status_code, expected_status_code)


obj1 = TestPostJob()



