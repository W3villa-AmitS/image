import random
import string
import uuid
import csv
from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
import urllib3
urllib3.disable_warnings()

class TestMturkAddWot(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    count = 0
    #usernames
    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'
    #passwords
    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    #searcher creating job
    searcher = user.Searcher(username_searcher, password_searcher)
    response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                               job_description='Testing',
                                               job_max_occurrence='10', job_assignment_duration='10',
                                               job_lifetime_duration='365',
                                               job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                               job_boxing_type='Rectangle')


    #File used to add wot .
    file = {'csv_file': ('xyz.csv',
                         'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

    '''Adding wots with valid credentials and data / expected output : 202'''


    def test_add_wot_through_valid_users(self):
        '''
                      description= 'Send HTTP POST ADD WOT request using searcher login
                      at the endpoint  with valid wots',
                      expected_output = '202'/test_id = MT_PT_AW_POST_000,
                      '''

        job_id = self.response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_searcher = searcher.mturk_add_wots_new(job_id,self.file)
        expected_status_code = 202
        expected_response = "WOTs scheduled to add successfully."
        self.assertEqual(expected_response,response_searcher.json()['success'])
        self.assertEqual(expected_status_code,response_searcher.status_code)
        expected_number_of_wots = 1
        self.assertEqual(expected_number_of_wots,response_searcher.json()['job_number_of_wots_scheduled_to_add'])
        expected_number_of_qats = 0
        self.assertEqual(expected_number_of_qats,response_searcher.json()['job_number_of_qats_added'])
        expected_number_of_hits = 1
        self.assertEqual(expected_number_of_hits,response_searcher.json()['job_number_of_hits'])
        expected_numer_of_qats_required = 2
        self.assertEqual(expected_numer_of_qats_required,response_searcher.json()['job_number_of_total_qats_required'])
        expected_qats_required_to_add = 2
        self.assertEqual(expected_qats_required_to_add,response_searcher.json()['job_number_of_more_qats_required_to_add'])


    '''Adding wots with valid credentials and without csv_file / / expected output : 400 & 
    expected error "Missing 'csv_file' in the request." '''

    def test_adding_wot_without_csv_file(self):
        '''
                      description= 'Send HTTP POST ADD_WOTS request using searcher login
                      at the endpoint  without csv_file',
                      expected_output = '201'/test_id = MT_NT_AW_POST_000 ,
                      '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEquals(expected_status_code, response_post_job.status_code)
        #fetching job_id for further use
        job_id = response_post_job.json()['job_id']
        file = {}

        #Adding Wots by searcher
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_no_csv = searcher.test_mturk_add_wots(job_id,file)
        #fetching error for assertion
        error = response_no_csv.json()['error']
        expected_status_code = 400
        expected_error  = "Missing 'csv_file' in the request."
        self.assertEqual(expected_error,error)
        self.assertEqual(expected_status_code,response_no_csv.status_code)

    '''Adding wots with valid credentials and invalid request verb(get,post) / expected output : 405 
    & expected error  : 'Method "GET" not allowed.' '''

    def test_add_wots_invalid_request_verbs(self):
        '''
                      description= 'Send HTTP POST ADD_WOTS request using searcher login
                      at the endpoint  with invalid request verb',
                      expected_output = '405'/test_id = MT_NT_AW_POST_001,
                      '''

        job_id = self.response_post_job.json()['job_id']
        #Adding wots by searcher.
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_invalid_request = searcher.mturk_add_wots_get_method(job_id,self.file)
        #fetching error for assertion
        error = response_invalid_request.json()['detail']
        expected_error =  'Method "GET" not allowed.'
        expected_status_code = 405
        self.assertEqual(expected_error,error)
        self.assertEqual(expected_status_code,response_invalid_request.status_code)

        '''Adding wots with invalid users with valid credentials & expected status code : 403
        & expected error : "Authentication credentials were not provided" '''

    def test_add_wot_by_invalid_users(self):
        ''' description= 'Send HTTP POST ADD_WOTS request using uauthorised users login
            at the endpoint',
            expected_output = '403'/test_id = MT_NT_AW_POST_002,'''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEquals(expected_status_code, response_post_job.status_code)
        #adding Qat through manager
        job_id_new_manager = response_post_job.json()['job_id']
        manager = user.Manager(self.username_manager,self.password_manager)
        response_manager = manager.mturk_add_wots_new(job_id_new_manager,self.file)
        expected_status_code = 403
        #fetching error fo assertion
        error = response_manager.json()['detail']
        expected_error = "Authentication credentials were not provided."
        self.assertEqual(expected_error, error)
        self.assertEqual(expected_status_code, response_manager.status_code)

        #Adding wots through worker
        job_id_worker = self.response_post_job.json()['job_id']
        worker = user.Worker(self.username_worker, self.password_worker)
        response_worker = worker.mturk_add_wots_new(job_id_worker,self.file)
        #fetching error for assertion.
        error = response_worker.json()['detail']
        expected_status_code = 403
        expected_error = "Authentication credentials were not provided."
        self.assertEqual(expected_error, error)
        self.assertEqual(expected_status_code, response_worker.status_code)

        #Adding wots by admin
        job_id_admin = self.response_post_job.json()['job_id']
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_admin = admin.mturk_add_wots_new(job_id_admin,self.file)
        #fetching error for assertion
        error = response_admin.json()['detail']
        expected_status_code = 403
        expected_error = "Authentication credentials were not provided."
        self.assertEqual(expected_error, error)
        self.assertEqual(expected_status_code, response_admin.status_code)

    def test_add_wot_using_invalid_urls(self):
        '''
                      description= 'Send HTTP POST ADD WOT request using searcher login
                      at the endpoint  with invalid urls of images',
                      expected_output = '202'/test_id = MT_NT_AW_POST_003,
                      '''

        job_id = self.response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248769/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        response_searcher = searcher.mturk_add_wots_new(job_id, file)
        expected_status_code = 202
        self.assertEqual(expected_status_code,response_searcher.status_code)


    def test_add_wot_using_invalid_extension_file(self):
        '''
                      description= 'Send HTTP POST ADD WOT request using searcher login
                      at the endpoint  with invalid extension file',
                      expected_output = '400'/test_id = MT_NT_AW_POST_004,
                      '''

        job_id = self.response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        file = {'cvs_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248769/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        response_searcher = searcher.mturk_add_wots_new(job_id, file)
        expected_status_code = 400
        expected_error = "Missing 'csv_file' in the request."
        self.assertEqual(expected_status_code,response_searcher.status_code)
        self.assertEqual(expected_error,response_searcher.json()['error'])

    def test_add_wot_with_blank_csv(self):
        '''
                      description= 'Send HTTP POST ADD WOT request using searcher login
                      at the endpoint  with blank csv',
                      expected_output = '400'/test_id = MT_NT_AW_POST_005,
                      '''

        job_id = self.response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        file = {'csv_file': ('xyz.csv','image_url\n ')}
        expected_error = "Considering single file, too less URLs in csv file to form a HIT."
        response_searcher = searcher.mturk_add_wots_new(job_id, file)
        expected_status_code = 400
        self.assertEqual(expected_status_code,response_searcher.status_code)
        self.assertEqual(expected_error,response_searcher.json()['error'])

    def test_add_wot_to_invalid_job_id(self):
        ''' description= 'Send HTTP POST ADD WOT request using searcher login
              at the endpoint  with invalid job_id',
              expected_output = '404'/test_id = MT_NT_AW_POST_006,'''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        jobid = response_post_job.json()['job_id']
        job_id = jobid + 'as'
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_searcher = searcher.mturk_add_wots_new(job_id, self.file)
        expected_status_code = 404
        self.assertEqual(expected_status_code, response_searcher.status_code)