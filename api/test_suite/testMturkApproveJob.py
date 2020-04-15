from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
import urllib3,time
urllib3.disable_warnings()



class TestMturkApproveJob(SimpleTestCase):
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

    result = {
        "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

    def test_mturk_approve_job_by_manager_login(self):
        '''
      description= 'Send HTTP POST job approve request using manager login
      at the endpoint  with valid username and password', \
      expected_output = '202'/test_id = MT_PT_AJ_POST_000,
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                         job_description='Testing',
                                         job_max_occurrence='10', job_assignment_duration='10',
                                         job_lifetime_duration='365',
                                         job_reward_per_hit='0.01', job_qats_per_hit='1', job_tasks_per_hit='2',
                                         job_boxing_type='Rectangle')

        expected_status_code = 201
        self.assertEqual(response_post_job.status_code, expected_status_code)
        self.job_id = response_post_job.json()['job_id']

        searcher.mturk_add_wots(self.job_id)
        time.sleep(5)
        searcher.mturk_add_qats(self.job_id,self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        expected_status_code = 202
        self.job_owner = response_approval.json()['job_owner']
        self.hits_created = response_approval.json()['hits_created']
        self.assertEqual(response_approval.status_code, expected_status_code)
        try:
            if self.job_id is None:
                print('self.job_id has no value')
        except NameError:
            print('self.job_id is not defined')
            assert (False)
        # else:
        #     print('self.job_id ' + str(self.job_id))

        try:
            if self.job_owner is None:
                print('self.job_owner has no value')
        except NameError:
            print('self.job_owner is not defined')
            assert (False)
        # else:
        #     print('self.job_owner ' + str(self.job_owner))

        self.assertEqual(response_approval.status_code, expected_status_code)

        try:
            if response_approval.json()['job_name'] is None:
                print('self.job_name has no value')
        except NameError:
            print('self.job_name is not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_name'], 'test Mturk job')

        try:
            if response_approval.json()['job_status'] is None:
                print('self.job_status has no value')
        except NameError:
            print('self.job_status is not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_status'], 'approved')

        try:
            if response_approval.json()['job_type'] is None:
                print('self.job_type has no value')
        except NameError:
            print('self.job_type is not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_type'], 'P')

        try:
            if response_approval.json()['job_attributes'] is None:
                print('self.job_attributes has no value')
        except NameError:
            print('self.job_attributesis not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_attributes'], 'cars,bikes')

        try:
            if response_approval.json()['job_description'] is None:
                print('self.job_description has no value')
        except NameError:
            print('self.job_description not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_description'], 'Testing')

        try:
            if response_approval.json()['job_max_occurrence'] is None:
                print('self.job_max_occurrence has no value')
        except NameError:
            print('self.job_max_occurrence not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_max_occurrence'], 10)

        try:
            if response_approval.json()['job_boxing_type'] is None:
                print('self.job_boxing_type has no value')
        except NameError:
            print('self.job_boxing_type not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_boxing_type'], 'Rectangle')

        try:
            if response_approval.json()['job_assignment_duration'] is None:
                print('self.job_assignment_duration has no value')
        except NameError:
            print('self.job_assignment_duration not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_assignment_duration'], 10)

        try:
            if response_approval.json()['job_lifetime_duration'] is None:
                print('self.job_lifetime_duration has no value')
        except NameError:
            print('self.job_lifetime_duration not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_lifetime_duration'], 365)
        try:
            if response_approval.json()['job_reward_per_hit'] is None:
                print('self.job_reward_per_hit has no value')
        except NameError:
            print('self.job_reward_per_hit not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_reward_per_hit'], 0.01)

        try:
            if response_approval.json()['job_qats_per_hit'] is None:
                print('self.job_qats_per_hit has no value')
        except NameError:
            print('self.job_qats_per_hit not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_qats_per_hit'], 1)
        try:
            if response_approval.json()['job_tasks_per_hit'] is None:
                print('self.job_tasks_per_hit has no value')
        except NameError:
            print('self.job_tasks_per_hit not defined')
            assert (False)
        else:
            self.assertEqual(response_approval.json()['job_tasks_per_hit'], 2)

        try:
            if self.hits_created is None:
                print('self.hits_created has no value')
        except NameError:
            print('self.hits_created is not defined')
            assert (False)
        # else:
        #     print('self.hits_created ' + str(self.hits_created))

    def test_mturk_approve_job_by_invalid_login(self):
        '''
      description= 'Send HTTP POST job approve request using unauthorised users login
      at the endpoint  with valid username and password', \
      expected_output = '403'/test_id = MT_NT_AJ_POST_000,
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
        reponse = searcher.mturk_add_wots(self.job_id)
        response1 = searcher.mturk_add_qats(self.job_id,result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        ## unauthorized actor trying to approve the job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_approval = searcher.mturk_approve_job(self.job_id)
        expected_status_code = 403
        expected_error_message = 'Authentication credentials were not provided.'
        self.assertTrue(response_approval.status_code == expected_status_code and response_approval.json()['detail'] == expected_error_message)


    def test_mturk_approve_invalid_job_id(self):
        '''
            description= 'Send HTTP Post approve request using manager login with
             invalid job_id at the endpoint', \expected_output = '404'/test_id = MT_NT_AJ_POST_001,
        '''

        list_of_existing_job_id = []
        manager = user.Manager(self.username_manager, self.password_manager)
        response_get_jobs = manager.mturk_get_jobs()
        for entry in response_get_jobs.json():
            list_of_existing_job_id.append(entry['job_id'])

        temp = '9qwerty7'
        while temp in list_of_existing_job_id:
            temp += '9qwerty7'
        try:
            invalid_job_id = temp
        except ValueError as e:
            raise

        expected_status_code = 200
        self.assertEqual(response_get_jobs.status_code, expected_status_code)
        time.sleep(10)
        ## manager approves job
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(invalid_job_id)
        expected_status_code = 404
        self.assertEqual(response_approval.status_code, expected_status_code)


    def test_mturk_approve_job_which_is_already_approved(self):
        '''
      description= 'Send HTTP POST job approve request using manager login on an already
       approved job ', \expected_output = '400'/test_id = MT_NT_AJ_POST_002,
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
        time.sleep(5)
        searcher.mturk_add_qats(self.job_id,result)
        self.assertEqual(response_post_job.status_code, expected_status_code)
        time.sleep(10)
        ## manager approves job
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        expected_status_code = 202
        self.assertEqual(response_approval.status_code, expected_status_code)
        time.sleep(10)
        ## manager approves job
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        expected_status_code = 400
        expected_error_message = "Can't 'approve' a job in state of 'approved'"
        self.assertTrue(response_approval.status_code == expected_status_code and response_approval.json()['error'] == expected_error_message)

    def test_mturk_approve_job_in_being_created_state(self):
        '''
            description= 'Send HTTP POST job approve request using manager login on being created
             job ', \expected_output = '400'/test_id = MT_NT_AJ_POST_003,
            '''

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
        ## manager approves job
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        expected_status_code= 400
        self.assertEqual(response_approval.status_code,expected_status_code)
        expected_error =  "Can't 'approve' a job in state of 'being_created'"
        self.assertEqual(expected_error,response_approval.json()['error'])

    def test_mturk_approve_job_in_initialized_state(self):
        '''
                    description= 'Send HTTP POST job approve request using manager login on intialized
                     job ', \expected_output = '400'/test_id = MT_NT_AJ_POST_004,
                    '''
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')

        expected_status_code = 201
        self.assertEqual(expected_status_code,response_post_job.status_code)
        self.job_id = response_post_job.json()['job_id']
        ## manager approves job
        manager = user.Manager(self.username_manager, self.password_manager)
        response_approval = manager.mturk_approve_job(self.job_id)
        expected_error = "Can't 'approve' a job in state of 'initialized'"
        expected_status_code =400
        self.assertEqual(expected_error,response_approval.json()['error'])
        self.assertEqual(expected_status_code,response_approval.status_code)

obj1 = TestMturkApproveJob()

#obj1.test_post_job_by_searcher_login()



