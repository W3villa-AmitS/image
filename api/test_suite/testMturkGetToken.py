import random
import string

from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
import urllib3,time
urllib3.disable_warnings()

class TestMturkGetToken(SimpleTestCase):
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

    def id_generator(self,size=8, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


    def test_mturk_get_token_by_valid_parameters(self):
        '''
      description= 'Send HTTP POST get token using valid parameters', \
      expected_output = '200',/test_id = MT_PT_GT_GET_000
      '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                         job_description='Testing',
                                         job_max_occurrence='10', job_assignment_duration='10',
                                         job_lifetime_duration='365',
                                         job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                         job_boxing_type='Rectangle')


        expected_status_code = 201
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id,result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id,assignment_id,'SAMPLEWORKER')
        response_get_token = mturk_worker.mturk_get_token(self.hit_id,assignment_id,'SAMPLEWORKER')
        expected_status_code = 200
        self.token = response_get_token.json()['token']
        self.assertEqual(response_get_token.status_code, expected_status_code)
        try:
            if self.token is None:
                print('self.token has no value')
        except NameError:
            print('self.token is not defined')
            assert (False)

    def test_mturk_get_token_by_invalid_worker_id(self):
        '''
      description= 'Send HTTP POST get token using invalid worker_id i.e using lower case
      alphabets', \
      expected_output = '400',/test_id = MT_NT_GT_GET_000
      '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                         job_description='Testing',
                                         job_max_occurrence='10', job_assignment_duration='10',
                                         job_lifetime_duration='365',
                                         job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                         job_boxing_type='Rectangle')

        expected_status_code = 201
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id,result)

        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkWorker(self.hit_id, assignment_id, 'abcdef')
        expected_status_code = 400
        response_get_token = mturk_worker.export_response()
        expected_error_message = ['Invalid format.']
        self.assertTrue(response_get_token.status_code == expected_status_code and response_get_token.json()['worker_id'] == expected_error_message)

    def test_mturk_get_token_by_special_character_in_worker_id(self):
            '''
          description= 'Send HTTP POST get token using invalid worker_id i.e using special character', \
          expected_output = '400',/test_id = MT_NT_GT_GET_001
          '''
            result = {
                "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                    "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                    "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                         {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                             "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                             "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

            searcher = user.Searcher(self.username_searcher, self.password_searcher)
            response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                       job_attributes='cars,bikes',
                                                       job_description='Testing',
                                                       job_max_occurrence='10', job_assignment_duration='10',
                                                       job_lifetime_duration='365',
                                                       job_reward_per_hit='1', job_qats_per_hit='2',
                                                       job_tasks_per_hit='3',
                                                       job_boxing_type='Rectangle')

            expected_status_code = 201
            self.job_id = response_post_job.json()['job_id']
            searcher.mturk_add_wots(self.job_id)
            time.sleep(10)
            searcher.mturk_add_qats(self.job_id,result)
            self.assertEqual(response_post_job.status_code, expected_status_code)
            time.sleep(10)
            manager = user.Manager(self.username_manager, self.password_manager)
            response_approval = manager.mturk_approve_job(self.job_id)
            self.hit_id = response_approval.json()['hits_created']
            assignment_id = self.id_generator()
            mturk_worker = user.MturkWorker(self.hit_id, assignment_id, '@$^&')
            expected_status_code = 400
            response_get_token = mturk_worker.export_response()
            expected_error_message = ['Invalid format.']
            self.assertTrue(response_get_token.status_code == expected_status_code and response_get_token.json()['worker_id'] == expected_error_message)


    def test_mturk_get_token_by_blank_worker_id(self):
        '''
      description= 'Send HTTP POST get token using invalid worker_id i.e using blank value', \
      expected_output = '400',/test_id = MT_NT_GT_GET_002
      '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201

        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id,result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkWorker(self.hit_id, assignment_id, '')
        expected_status_code = 400
        response_get_token = mturk_worker.export_response()
        expected_error_message = ['This field may not be blank.']
        self.assertTrue(response_get_token.status_code == expected_status_code and response_get_token.json()['worker_id'] == expected_error_message)



    def test_mturk_get_token_by_blank_assignment_id(self):
            '''
          description= 'Send HTTP POST get token using invalid assignment_id i.e using blank value', \
          expected_output = '400',/test_id = MT_NT_GT_GET_003
          '''

            result = {
                "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                    "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                    "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                         {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                             "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                             "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
            searcher = user.Searcher(self.username_searcher, self.password_searcher)
            response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                       job_attributes='cars,bikes',
                                                       job_description='Testing',
                                                       job_max_occurrence='10', job_assignment_duration='10',
                                                       job_lifetime_duration='365',
                                                       job_reward_per_hit='1', job_qats_per_hit='2',
                                                       job_tasks_per_hit='3',
                                                       job_boxing_type='Rectangle')

            expected_status_code = 201
            self.job_id = response_post_job.json()['job_id']
            searcher.mturk_add_wots(self.job_id)
            time.sleep(10)
            searcher.mturk_add_qats(self.job_id,result)
            self.assertEqual(response_post_job.status_code, expected_status_code)
            time.sleep(10)
            manager = user.Manager(self.username_manager, self.password_manager)
            response_approval = manager.mturk_approve_job(self.job_id)
            assignment_id = self.id_generator()
            self.hit_id = response_approval.json()['hits_created']
            mturk_worker = user.MturkUser(self.hit_id,assignment_id,'SAMPLEWORKER')
            expected_status_code = 400
            response_get_token = mturk_worker.mturk_get_token(self.hit_id," ","SAMPLEWORKER")
            expected_error_message = ['This field may not be blank.']
            self.assertTrue(response_get_token.status_code == expected_status_code and response_get_token.json()['assignment_id'] == expected_error_message)


    def test_mturk_get_token_by_invalid_hit_id(self):
        '''
      description= 'Send HTTP POST get token using invalid hit_id i.e manipulating the hit_id generated, \
      expected_output = '400',/test_id = MT_NT_GT_GET_004
      '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201

        self.job_id = response_post_job.json()['job_id']

        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id,result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        thisInvalidList = "3ZG552O002VJAD"
        Invalid_hit_id =self.hit_id[0] + thisInvalidList
        assignment_id = self.id_generator()
        mturk_worker = user.MturkWorker(Invalid_hit_id, assignment_id, 'SAMPLEWORKER')
        expected_status_code = 406
        response_get_token = mturk_worker.export_response()
        try:
            if response_get_token.json()['error'] is None:
                print("Error found in generating token")
        except:
            print("Token generated successfully")
            assert (False)
        self.assertEqual(expected_status_code,response_get_token.status_code)

    def test_mturk_get_token_by_null_hit_id(self):
        '''
           description= 'Send HTTP POST get token using null hit_id , \
           expected_output = '400',/test_id = MT_NT_GT_GET_005
           '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201

        self.job_id = response_post_job.json()['job_id']

        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id, 'SAMPLEWORKER')
        expected_status_code = 400
        response_get_token = mturk_worker.mturk_get_token(" ", assignment_id, 'SAMPLEWORKER')
        expected_error_message = [ "This field may not be blank."]
        self.assertTrue(response_get_token.status_code == expected_status_code and response_get_token.json()['hit_id'] == expected_error_message)

    def test_mturk_get_token_without_hit_id(self):
        '''
                   description= 'Send HTTP POST get token using without  hit_id , \
                   expected_output = '400',/test_id = MT_NT_GT_GET_006
                   '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201

        self.job_id = response_post_job.json()['job_id']

        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id, 'SAMPLEWORKER')
        expected_status_code = 400
        response_get_token = mturk_worker.mturk_get_token_testing_without_hit_id(assignment_id, 'SAMPLEWORKER')
        expected_error_message = ['This field is required.']
        self.assertTrue(response_get_token.status_code == expected_status_code and response_get_token.json()['hit_id'] == expected_error_message)

    def test_mturk_get_token_by_integer_worker_id(self):
        '''
                   description= 'Send HTTP POST get token using integer worker_id, \
                   expected_output = '400',/test_id = MT_NT_GT_GET_007
                   '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201

        self.job_id = response_post_job.json()['job_id']

        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id,"SAMPLEWORKERID")
        response_get_token = mturk_worker.mturk_get_token(self.hit_id, assignment_id,7894561237)
        self.token = response_get_token.json()['token']
        expected_status_code = 200
        try:
            if self.token is None:
                print('self.token has no value')
        except NameError:
            print('self.token is not defined')
            assert (False)
        self.assertEqual(response_get_token.status_code,expected_status_code)

    def test_mturk_get_token_by_integer_assignment_id(self):
        '''
                   description= 'Send HTTP POST get token using integer assignment_id, \
                   expected_output = '400',/test_id = MT_NT_GT_GET_008
                   '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201

        self.job_id = response_post_job.json()['job_id']

        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id,assignment_id, 'SAMPLEWORKER')
        random_string = string.digits
        stringLength = 10
        integer_assignment_id = ''.join(random.sample(random_string, stringLength))
        response_get_token = mturk_worker.mturk_get_token(self.hit_id,integer_assignment_id, 'SAMPLEWORKER')
        self.token = response_get_token.json()['token']
        expected_status_code = 200
        try:
            if self.token is None:
                print('self.token has no value')
        except NameError:
            print('self.token is not defined')
            assert (False)
        self.assertEqual(response_get_token.status_code,expected_status_code)


    def test_mturk_get_token_by_integer_hit_id(self):
        '''
                   description= 'Send HTTP POST get token using integer assignment_id, \
                   expected_output = '400',/test_id = MT_NT_GT_GET_009
                   '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkWorker("1234567890", assignment_id, 'SAMPLEWORKER')
        expected_status_code = 406
        response_get_token = mturk_worker.export_response()
        try:
            if response_get_token.json()['error'] is None:
                print("Error found in generating token")
        except:
                print("Token generated successfully")
        self.assertTrue(response_get_token.status_code == expected_status_code)


    def test_mturk_get_token_by_wrong_url(self):
        '''
                   description= 'Send HTTP POST get token by wrong url, \
                   expected_output = '400',/test_id = MT_NT_GT_GET_010
                   '''

        result = {
                "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                    "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                    "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                         {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                             "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                             "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                       job_attributes='cars,bikes',
                                                       job_description='Testing',
                                                       job_max_occurrence='10', job_assignment_duration='10',
                                                       job_lifetime_duration='365',
                                                       job_reward_per_hit='1', job_qats_per_hit='2',
                                                       job_tasks_per_hit='3',
                                                       job_boxing_type='Rectangle')

        expected_status_code = 201

        self.job_id = response_post_job.json()['job_id']

        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id, 'SAMPLEWORKER')
        get_token_response  = mturk_worker.mturk_get_token_testing(self.hit_id,assignment_id,'SAMPLEWORKER')
        expected_status_code = 404
        self.assertEqual(expected_status_code,get_token_response.status_code)

    def test_mturk_get_token_by_list_of_hit_id(self):
        '''
                           description= 'Send HTTP POST get token by list of hit_id's, \
                           expected_output = '400',/test_id = MT_NT_GT_GET_011
                           '''

        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201
        self.job_id = response_post_job.json()['job_id']
        searcher.mturk_add_wots(self.job_id)
        time.sleep(10)
        searcher.mturk_add_qats(self.job_id, result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        self.hit_id = response_approval.json()['hits_created']
        hit_id_list = []
        hitid = str(self.hit_id)
        hit_id_list.append(hitid)
        assignment_id = self.id_generator()
        mturk_worker = user.MturkUser(self.hit_id, assignment_id, 'SAMPLEWORKER')
        response_get_token = mturk_worker.mturk_get_token(hit_id_list, assignment_id, 'SAMPLEWORKER')
        expected_error = ['Invalid format.']
        self.assertEqual(expected_error,response_get_token.json()['hit_id'])
        expected_status_code = 400
        self.assertEqual(expected_status_code,response_get_token.status_code)

obj1 = TestMturkGetToken()





