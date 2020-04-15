from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
import urllib3
urllib3.disable_warnings()


class TestMturkPostJob(SimpleTestCase):
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

    def test_mturk_post_job_by_valid_login(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint  with valid username and password', \
      expected_output = '201' i.e job created,/test_id = MT_PT_JP_POST_000
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
        self.job_name = response_post_job.json()['job_name']

        searcher.mturk_add_wots(self.job_id)

        searcher.mturk_add_qats(self.job_id,result)

        self.assertTrue(response_post_job)
        try:
            if self.job_id is None:
                print('self.job_id has no value')
        except NameError:
            print('self.job_id is not defined')
            assert (False)
        # else:
        #     print('self.job_id ' + str(self.job_id))

        self.assertEqual(response_post_job.status_code, expected_status_code)

        try:
            if response_post_job.json()['job_name'] is None:
                print('self.job_name has no value')
        except NameError:
            print('self.job_name is not defined')
            assert (False)
        else:
            self.assertEqual(response_post_job.json()['job_name'], 'test Mturk job')

        try:
            if response_post_job.json()['job_type'] is None:
                print('self.job_type has no value')
        except NameError:
            print('self.job_type is not defined')
            assert (False)
        else:
            self.assertEqual(response_post_job.json()['job_type'], 'P')

        try:
            if response_post_job.json()['job_attributes'] is None:
                print('self.job_attributes has no value')
        except NameError:
            print('self.job_attributesis not defined')
            assert (False)
        else:
            self.assertEqual(response_post_job.json()['job_attributes'], 'cars,bikes')

        try:
            if response_post_job.json()['job_max_occurrence'] is None:
                print('self.job_max_occurrence has no value')
        except NameError:
            print('self.job_max_occurrence not defined')
            assert (False)
        else:
            self.assertEqual(response_post_job.json()['job_max_occurrence'], 10)

        try:
            if response_post_job.json()['job_boxing_type'] is None:
                print('self.job_boxing_type has no value')
        except NameError:
            print('self.job_boxing_type not defined')
            assert (False)
        else:
            self.assertEqual(response_post_job.json()['job_boxing_type'], 'Rectangle')

    def test_mturk_post_job_by_invalid_login(self):
        '''
      description= 'Send HTTP POST job request using invalid login
      at the endpoint ', \
      expected_output = '403 Forbidden',/test_id = MT_NT_JP_POST_000
      '''
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

        manager = user.Manager(self.username_manager, self.password_manager)
        response_post_job = manager.mturk_add_job(job_name='test Mturk job with invalid login', job_type='P',
                                                  job_attributes='cars,bikes',
                                                  job_description='Testing Invalid credential',
                                                  job_max_occurrence='10', job_assignment_duration='10',
                                                  job_lifetime_duration='365',
                                                  job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                  job_boxing_type='Rectangle')
        expected_error_message = 'Authentication credentials were not provided.'
        expected_status_code = 403
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['detail'] == expected_error_message)


    def test_mturk_post_job_by_invalid_access_token(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint  with invalid access_token', \
      expected_output = '403'Invalid or expired token,/test_id = MT_NT_JP_POST_001
      '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        token = searcher.access_token + "abc"

        response_post_job = userApisMturk.mturk_post_job('Test Invalid token', 'P', 'cars,bikes',
                                                         'Testing Invalid token', '10',
                                                         '10', '365', '1',
                                                         '2', '3', 'Rectangle', token)

        expected_error_message = 'Invalid or expired token.'
        expected_status_code = 403
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['detail'] == expected_error_message)

    def test_mturk_post_job_entering_invalid_job_occurrence(self):
        '''
        description= 'Send HTTP POST job request using searcher login
        at the endpoint entering invalid value', \
        expected_output = '400',/test_id = MT_NT_JP_POST_002
        '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job entering invalid value', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='testing',
                                                   job_max_occurrence='-1', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message =  ['Ensure this value is greater than or equal to 1.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_max_occurrence'] == expected_error_message)


    def test_mturk_post_job_without_entering_all_mandatory_field(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint  without entering all mandatory field', \
      expected_output = '400',/test_id = MT_NT_JP_POST_003
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job without entering all field',
                                                   job_type='P', job_attributes='cars,bikes',
                                                   job_description='',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message = ['This field may not be blank.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_description'] == expected_error_message)

    def test_mturk_post_job_entering_special_character_in_job_occurrence(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint entering special character in field', \
      expected_output = '400',/test_id = MT_NT_JP_POST_004
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job entering special character in field',
                                                   job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='testing',
                                                   job_max_occurrence='&', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message = ['A valid integer is required.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_max_occurrence'] == expected_error_message)


    def test_mturk_post_job_entering_invalid_value_in_job_assignment_duration(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint entering invalid value in job_assignment_duration i.e 0', \
      expected_output = '400',/test_id = MT_NT_JP_POST_005
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(
            job_name='test Mturk job entering invalid value in job assignment duration', job_type='P',
            job_attributes='cars,bikes',
            job_description='testing',
            job_max_occurrence='10', job_assignment_duration='0',
            job_lifetime_duration='365',
            job_reward_per_hit='1', job_qats_per_hit='2',
            job_tasks_per_hit='3',
            job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message = ['Ensure this value is greater than or equal to 1.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_assignment_duration'] == expected_error_message)


    def test_mturk_post_job_entering_invalid_value_in_job_lifetime_duration(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint entering invalid value in job_lifetime_duration i.e 0', \
      expected_output = '400',//test_id = MT_NT_JP_POST_006
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(
            job_name='test Mturk job entering invalid value in job lifetime duration', job_type='P',
            job_attributes='cars,bikes',
            job_description='testing',
            job_max_occurrence='10', job_assignment_duration='10',
            job_lifetime_duration='0',
            job_reward_per_hit='1', job_qats_per_hit='2',
            job_tasks_per_hit='3',
            job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message = ['Ensure this value is greater than or equal to 1.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_lifetime_duration'] == expected_error_message)


    def test_mturk_post_job_entering_negative_value_in_job_reward_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint entering invalid value in job_reward_per_hit', \
      expected_output = '400',//test_id = MT_NT_JP_POST_007
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(
            job_name='test Mturk job entering negative value in job reward per hit', job_type='P',
            job_attributes='cars,bikes',
            job_description='testing',
            job_max_occurrence='10', job_assignment_duration='10',
            job_lifetime_duration='365',
            job_reward_per_hit='-1', job_qats_per_hit='2',
            job_tasks_per_hit='3',
            job_boxing_type='Rectangle')

        expected_status_code = 400
        expected_error_message = ['Ensure this value is greater than or equal to 0.01.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_reward_per_hit'] == expected_error_message)


    def test_mturk_post_job_entering_zero_value_in_job_reward_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint entering zero value in job_reward_per_hit', \
      expected_output = '400',//test_id = MT_NT_JP_POST_008
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(
            job_name='test Mturk job entering zero value in job reward per hit', job_type='P',
            job_attributes='cars,bikes',
            job_description='testing',
            job_max_occurrence='10', job_assignment_duration='10',
            job_lifetime_duration='365',
            job_reward_per_hit='0', job_qats_per_hit='2',
            job_tasks_per_hit='3',
            job_boxing_type='Rectangle')
        expected_status_code = 400

        expected_error_message = ['Ensure this value is greater than or equal to 0.01.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_reward_per_hit'] == expected_error_message)

    def test_mturk_post_job_entering_special_character_in_job_reward_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint entering special character in job_reward_per_hit', \
      expected_output = '400',/test_id = MT_NT_JP_POST_009
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(
            job_name='test Mturk job entering special character in job reward per hit', job_type='P',
            job_attributes='cars,bikes',
            job_description='testing',
            job_max_occurrence='10', job_assignment_duration='10',
            job_lifetime_duration='5',
            job_reward_per_hit='&', job_qats_per_hit='2',
            job_tasks_per_hit='3',
            job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message = ['A valid number is required.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_reward_per_hit'] == expected_error_message)


    def test_mturk_post_job_entering_alphabets_in_job_reward_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint entering alphabets in job_reward_per_hit', \
      expected_output = '400',//test_id = MT_NT_JP_POST_010
      '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(
            job_name='test Mturk job entering alphabets job reward per hit', job_type='P',
            job_attributes='cars,bikes',
            job_description='testing',
            job_max_occurrence='10', job_assignment_duration='10',
            job_lifetime_duration='12',
            job_reward_per_hit='abc', job_qats_per_hit='2',
            job_tasks_per_hit='3',
            job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message = ['A valid number is required.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_reward_per_hit'] == expected_error_message)


    def test_mturk_post_job_by_entering_negative_value_in_qats_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint by entering negative value in qats per hit', \
      expected_output = '400',//test_id = MT_NT_JP_POST_011
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='-2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message = ['Ensure this value is greater than or equal to 1.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_qats_per_hit'] == expected_error_message)


    def test_mturk_post_job_by_entering_zero_value_in_qats_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint by entering zero value in qats per hit', \
      expected_output = '400',/test_id = MT_NT_JP_POST_012
      '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='0',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 400
        expected_error_message = ['Ensure this value is greater than or equal to 1.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_qats_per_hit'] == expected_error_message)

    def test_mturk_post_job_by_entering_negative_value_in_task_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint by entering negative value in task per hit', \
      expected_output = '400',//test_id = MT_NT_JP_POST_013
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='-5',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 400

        expected_error_message = ['Ensure this value is greater than or equal to 1.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_tasks_per_hit'] == expected_error_message)


    def test_mturk_post_job_by_entering_zero_value_in_task_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint by entering zero value in task per hit', \
      expected_output = '400',//test_id = MT_NT_JP_POST_014
      '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='0',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 400

        expected_error_message = ['Ensure this value is greater than or equal to 1.']
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()['job_tasks_per_hit'] == expected_error_message)

    def test_mturk_post_job_by_qats_same_as_task_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint  with same number of qats and task per hit', \
      expected_output = '400',/test_id = MT_NT_JP_POST_015
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='5',
                                                   job_tasks_per_hit='5',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 400

        expected_error_message = ["error: Number of QATs per HIT can't be greater than or equal to number of tasks per HIT."]
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json() == expected_error_message)

    def test_mturk_post_job_by_qats_more_than_task_per_hit(self):
        '''
      description= 'Send HTTP POST job request using searcher login
      at the endpoint  with  qats more than task per hit', \
      expected_output = '400',//test_id = MT_NT_JP_POST_016
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='7',
                                                   job_tasks_per_hit='5',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 400
        expected_error_message = ["error: Number of QATs per HIT can't be greater than or equal to number of tasks per HIT."]
        self.assertTrue(response_post_job.status_code == expected_status_code and response_post_job.json()== expected_error_message)

    def test_mturk_post_job_by_entering_invalid_job_type(self):
        '''
      description= 'Send HTTP POST job request using valid login and invalid value for job type
      at the endpoint ', \
      expected_output = '403 Forbidden',/test_id = MT_NT_JP_POST_017
      '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_invalid_job_type = searcher.mturk_add_job(job_name='test Mturk job with invalid login', job_type='K',
                                                  job_attributes='cars,bikes',
                                                  job_description='Testing Invalid credential',
                                                  job_max_occurrence='10', job_assignment_duration='10',
                                                  job_lifetime_duration='365',
                                                  job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                  job_boxing_type='Rectangle')
        error = ['"K" is not a valid choice.']
        self.assertEqual(error,response_invalid_job_type.json()['job_type'])
        expected_status_code = 400
        self.assertEqual(expected_status_code,response_invalid_job_type.status_code)

    def test_mturk_post_job_with_integer_job_attributes(self):
        '''
              description= 'Send HTTP POST job request using valid login with integer job attributes
              at the endpoint ', \
              expected_output = '403 Forbidden',/test_id = MT_NT_JP_POST_018
              '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_invalid_job_attributes = searcher.mturk_add_job_testing(job_name='test_job', job_type='P',
                                                           job_attributes= 3,
                                                           job_description='Testing Invalid credential',
                                                           job_max_occurrence='10', job_assignment_duration='10',
                                                           job_lifetime_duration='365',
                                                           job_reward_per_hit='1', job_qats_per_hit='2',
                                                           job_tasks_per_hit='3',
                                                           job_boxing_type='Rectangle')


        self.assertEqual(response_invalid_job_attributes.json()['job_name'],'test_job')
        self.assertEqual(response_invalid_job_attributes.json()['job_type'],'P')
        self.assertEqual(response_invalid_job_attributes.json()['job_attributes'],'3')
        self.assertEqual(response_invalid_job_attributes.json()['job_max_occurrence'],10)
        self.assertEqual(response_invalid_job_attributes.json()['job_boxing_type'],'Rectangle')

        expected_status_code = 201
        self.assertEqual(response_invalid_job_attributes.status_code,expected_status_code)

    def test_mturk_post_job_with_invalid_job_boxing_type(self):
        '''
              description= 'Send HTTP POST job request using valid login with invalid job boxing type
              at the endpoint ', \
              expected_output = '403 Forbidden',/test_id = MT_NT_JP_POST_019
              '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_invalid_job_boxing_type = searcher.mturk_add_job(job_name='test Mturk job with invalid login', job_type='P',
                                                           job_attributes= 'cars,bikes',
                                                           job_description='Testing Invalid credential',
                                                           job_max_occurrence='10', job_assignment_duration='10',
                                                           job_lifetime_duration='365',
                                                           job_reward_per_hit='1', job_qats_per_hit='2',
                                                           job_tasks_per_hit='3',
                                                           job_boxing_type='Rectengle')
        expected_error = ['"Rectengle" is not a valid choice.']
        expected_status_code = 400
        self.assertEqual(expected_error,response_invalid_job_boxing_type.json()['job_boxing_type'])
        self.assertEqual(expected_status_code,response_invalid_job_boxing_type.status_code)


    def test_mturk_post_without_user_login(self):
        '''
                     description= 'Send HTTP POST job request withput user login
                     at the endpoint ', \
                     expected_output = '403 Forbidden',/test_id = MT_NT_JP_POST_020
                     '''
        response_post_job_without_login = userApisMturk.mturk_post_job(job_name='test Mturk job with invalid login',
                                                                 job_type='P',
                                                                 job_attributes='cars,bikes',
                                                                 job_description='Testing Invalid credential',
                                                                 job_max_occurrence='10', job_assignment_duration='10',
                                                                 job_lifetime_duration='365',
                                                                 job_reward_per_hit='1', job_qats_per_hit='2',
                                                                 job_tasks_per_hit='3',
                                                                 job_boxing_type='Rectangle',access_token = None)
        expected_error = 'Invalid or expired token.'
        expected_status_code = 403
        self.assertEqual(response_post_job_without_login.status_code,expected_status_code)
        self.assertEqual(expected_error,response_post_job_without_login.json()['detail'])

obj1 = TestMturkPostJob()

# obj1.test_post_job_by_searcher_login()
