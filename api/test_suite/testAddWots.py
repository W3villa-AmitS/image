import random
import string
from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
from test_suite.lib.apis import userApisMturk
import urllib3
urllib3.disable_warnings()

class TestAddWots(SimpleTestCase):
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
    gender = '"M","F"'

    def test_add_wots_by_valid_user(self):
        '''description= 'Send HTTP POST add_wots request using searcher login
                      at the endpoint  with wots',
                      xpected ouptut = "WOTs added successfully."'
                    expected output : 202 /test_id = PT_AW_POST_000 '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='5',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        #Adding Wots
        response_add_wots = searcher.add_wots(job_id)
        expected_status_code = 202
        expected_output = "WOTs scheduled to add successfully."
        self.assertTrue(response_add_wots.status_code == expected_status_code and response_add_wots.json()['success'] == expected_output)

        # self.assertEqual(expected_output,response_add_wots.json()['success'])
        # self.assertEqual(expected_status_code,response_add_wots.status_code)

    def test_add_wots_by_other_user(self):
        '''description= 'Send HTTP POST add_wots request using unauthorised users login
                              at the endpoint  with valid username and password',
                              adding wots by worker,searcher,admin expected ouptut =
                              "You do not have permission to perform this action."
                            expected output : 403/test_id = NT_AW_POST_000  '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='5',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']

        #Adding wots using manager login
        manager = user.Manager(self.username_manager,self.password_manager)
        response_add_wots = manager.add_wots(job_id)
        expected_status_code = 403
        expected_error = "You do not have permission to perform this action."
        self.assertEqual(expected_error, response_add_wots.json()['detail'])
        self.assertEqual(expected_status_code, response_add_wots.status_code)

        # Adding wots using worker login
        worker = user.Worker(self.username_worker, self.password_worker)
        response_add_wots = worker.add_wots(job_id)
        expected_status_code = 403
        expected_error = "You do not have permission to perform this action."
        self.assertEqual(expected_error, response_add_wots.json()['detail'])
        self.assertEqual(expected_status_code, response_add_wots.status_code)

        # Adding wots using Admin login
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_add_wots = admin.add_wots(job_id)
        expected_status_code = 403
        expected_error = "You do not have permission to perform this action."
        self.assertEqual(expected_error, response_add_wots.json()['detail'])
        self.assertEqual(expected_status_code, response_add_wots.status_code)

    def test_add_wots_without_csv(self):
        '''description= 'Send HTTP POST add_wots request using searcher login
                              at the endpoint  with valid username and password without csv_file',
                              expected_output = '400' and  "Missing 'csv_file' in the request."
                                                 /test_id = NT_AW_POST_001 '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='5',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        file = {}
        response_add_wots = searcher.add_wots_without_csv(job_id,file)
        expected_error = "Missing 'csv_file' in the request."
        expected_status_code = 400
        self.assertEqual(expected_error,response_add_wots.json()['error'])
        self.assertEqual(expected_status_code,response_add_wots.status_code)

    def test_add_wots_with_diff_format_file(self):
        '''description= 'Send HTTP POST add_wots request using searcher login
                              at the endpoint  with valid username and password' with different format file,
                              expected_output = '202'  /test_id = NT_AW_POST_002'''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='5',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')
        job_id = response_post_job.json()['job_id']
        files = {'csv_file': ('xyz',
                              'imhgfhjfg')}
        response_add_wots = searcher.add_wots_without_csv(job_id, files)
        expected_status_code =202
        self.assertEqual(expected_status_code,response_add_wots.status_code)
        '''File should be added only in csv format no other fomat file will be added'''

    def test_add_wots_by_invalid_job_id(self):
        '''description= 'Send HTTP POST Add_wots request using searcher login
                              at the endpoint  with valid username and password'with invalid job_id,
                              expected_output = '404' /test_id = NT_AW_POST_003
                                                            '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='5',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        job_id = response_post_job.json()['job_id']
        response_add_wots = searcher.add_wots(job_id+'sgha')
        expected_status_code = 404
        self.assertEqual(expected_status_code,response_add_wots.status_code)