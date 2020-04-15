import random
import string
import uuid
from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
import urllib3
import random, string
urllib3.disable_warnings()
import json


class TestMturkDownloadQat(SimpleTestCase):
    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'

    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'
    gender = '"M","F"'

    result = {
        "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                 {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                     "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                     "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}


    def test_download_qat_by_searcher(self):

        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                         job_description='test2 job',
                                         job_instructions='test2 job', task_max_occurrence='2',
                                         job_criteria_age_min='18',
                                         job_criteria_age_max='60', job_criteria_location='India', job_initial_qats='2',
                                         job_qat_frequency='5', job_criteria_gender=self.gender, job_criteria_grade='D',
                                         job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        searcher.add_wots(job_id)
        searcher.add_qats(job_id, self.result)
        response_download_qat = searcher.mturk_download_qats(job_id)