from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
from test_suite.lib.apis import userApis
import urllib3,time
urllib3.disable_warnings()


class TestMturkGetJobOnBasisOfId(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    count = 0

    username_manager='manager1'
    username_admin='sharedadmin'
    username_searcher='searcher1'
    username_searcher_one='searcher2'
    username_worker='worker1'

    password_manager='Insidethepyramid@2'
    password_admin='WY+e5nsQg-43565!'
    password_searcher='Belowthepyramid@2'
    password_searcher_one = 'Belowthepyramid@3'
    password_worker='Nearthepyramid@2'

    def test_mturk_get_job_with_id_using_manager_login(self):
        '''
      description= 'Send HTTP Get jobs/job_id request using manager login
      at the endpoint', \expected_output = '200',/test_id = MT_PT_GJ_POST_000
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
                                                   job_max_occurrence='9', job_assignment_duration='10',
                                                   job_lifetime_duration='363',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Square')

        expected_status_code = 201

        self.job_id = response_post_job.json()['job_id']
        self.assertEqual(response_post_job.status_code,expected_status_code)
        searcher.mturk_add_wots(self.job_id)
        searcher.mturk_add_qats(self.job_id,result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        response_get_jobs = manager.mturk_get_job_with_id(self.job_id)
        expected_status_code = 200
        self.assertEqual(response_get_jobs.status_code, expected_status_code)
        try:
            if self.job_id is None:
                print('self.job_id has no value')
        except NameError:
            print('self.job_id is not defined')
            assert (False)
        # else:
        #     print('self.job_id ' + str(self.job_id))

        self.assertEqual(response_get_jobs.status_code, expected_status_code)

        try:
            if response_get_jobs.json()['job_name'] is None:
                print('self.job_name has no value')
        except NameError:
            print('self.job_name is not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_name'], 'test Mturk job')

        try:
            if response_get_jobs.json()['job_type'] is None:
                print('self.job_type has no value')
        except NameError:
            print('self.job_type is not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_type'], 'P')

        try:
            if response_get_jobs.json()['job_attributes'] is None:
                print('self.job_attributes has no value')
        except NameError:
            print('self.job_attributesis not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_attributes'], 'cars,bikes')

        try:
            if response_get_jobs.json()['job_description'] is None:
                print('self.job_description has no value')
        except NameError:
            print('self.job_description not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_description'], 'Testing')

        try:
            if response_get_jobs.json()['job_max_occurrence'] is None:
                print('self.job_max_occurrence has no value')
        except NameError:
            print('self.job_max_occurrence not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_max_occurrence'], 9)

        try:
            if response_get_jobs.json()['job_boxing_type'] is None:
                print('self.job_boxing_type has no value')
        except NameError:
            print('self.job_boxing_type not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_boxing_type'], 'Square')

        try:
            if response_get_jobs.json()['job_assignment_duration'] is None:
                print('self.job_assignment_duration has no value')
        except NameError:
            print('self.job_assignment_duration not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_assignment_duration'], 10)

        try:
            if response_get_jobs.json()['job_lifetime_duration'] is None:
                print('self.job_lifetime_duration has no value')
        except NameError:
            print('self.job_lifetime_duration not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_lifetime_duration'], 363)
        try:
            if response_get_jobs.json()['job_reward_per_hit'] is None:
                print('self.job_reward_per_hit has no value')
        except NameError:
            print('self.job_reward_per_hit not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_reward_per_hit'], 1)

        try:
            if response_get_jobs.json()['job_qats_per_hit'] is None:
                print('self.job_qats_per_hit has no value')
        except NameError:
            print('self.job_qats_per_hit not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_qats_per_hit'], 2)
        try:
            if response_get_jobs.json()['job_tasks_per_hit'] is None:
                print('self.job_tasks_per_hit has no value')
        except NameError:
            print('self.job_tasks_per_hit not defined')
            assert (False)
        else:
            self.assertEqual(response_get_jobs.json()['job_tasks_per_hit'], 3)

    def test_mturk_get_job_with_id_using_valid_searcher_login(self):
            '''
          description= 'Send HTTP Get jobs/job_id request using searcher login
          at the endpoint', \
          expected_output = '200'/test_id = MT_PT_GJ_POST_001,
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
                                                       job_max_occurrence='9', job_assignment_duration='10',
                                                       job_lifetime_duration='363',
                                                       job_reward_per_hit='1', job_qats_per_hit='2',
                                                       job_tasks_per_hit='3',
                                                       job_boxing_type='Square')
            expected_status_code = 201
            self.assertEqual(expected_status_code,response_post_job.status_code)
            self.job_id = response_post_job.json()['job_id']

            reponse = searcher.mturk_add_wots(self.job_id)

            response1 = searcher.mturk_add_qats(self.job_id,result)
            time.sleep(10)
            searcher = user.Searcher(self.username_searcher, self.password_searcher)
            response_get_jobs = searcher.mturk_get_job_with_id(self.job_id)
            expected_status_code = 200
            self.assertEqual(response_get_jobs.status_code, expected_status_code)

            try:
                if self.job_id is None:
                    print('self.job_id has no value')
            except NameError:
                print('self.job_id is not defined')
                assert (False)
            # else:
            #     print('self.job_id ' + str(self.job_id))

            self.assertEqual(response_get_jobs.status_code, expected_status_code)

            try:
                if response_get_jobs.json()['job_name'] is None:
                    print('self.job_name has no value')
            except NameError:
                print('self.job_name is not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_name'], 'test Mturk job')

            try:
                if response_get_jobs.json()['job_type'] is None:
                    print('self.job_type has no value')
            except NameError:
                print('self.job_type is not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_type'], 'P')

            try:
                if response_get_jobs.json()['job_attributes'] is None:
                    print('self.job_attributes has no value')
            except NameError:
                print('self.job_attributesis not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_attributes'], 'cars,bikes')

            try:
                if response_get_jobs.json()['job_description'] is None:
                    print('self.job_description has no value')
            except NameError:
                print('self.job_description not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_description'], 'Testing')

            try:
                if response_get_jobs.json()['job_max_occurrence'] is None:
                    print('self.job_max_occurrence has no value')
            except NameError:
                print('self.job_max_occurrence not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_max_occurrence'], 9)

            try:
                if response_get_jobs.json()['job_boxing_type'] is None:
                    print('self.job_boxing_type has no value')
            except NameError:
                print('self.job_boxing_type not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_boxing_type'], 'Square')

            try:
                if response_get_jobs.json()['job_assignment_duration'] is None:
                    print('self.job_assignment_duration has no value')
            except NameError:
                print('self.job_assignment_duration not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_assignment_duration'], 10)

            try:
                if response_get_jobs.json()['job_lifetime_duration'] is None:
                    print('self.job_lifetime_duration has no value')
            except NameError:
                print('self.job_lifetime_duration not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_lifetime_duration'], 363)
            try:
                if response_get_jobs.json()['job_reward_per_hit'] is None:
                    print('self.job_reward_per_hit has no value')
            except NameError:
                print('self.job_reward_per_hit not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_reward_per_hit'], 1)

            try:
                if response_get_jobs.json()['job_qats_per_hit'] is None:
                    print('self.job_qats_per_hit has no value')
            except NameError:
                print('self.job_qats_per_hit not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_qats_per_hit'], 2)
            try:
                if response_get_jobs.json()['job_tasks_per_hit'] is None:
                    print('self.job_tasks_per_hit has no value')
            except NameError:
                print('self.job_tasks_per_hit not defined')
                assert (False)
            else:
                self.assertEqual(response_get_jobs.json()['job_tasks_per_hit'], 3)



    def test_mturk_get_job_with_id_using_another_searcher_login(self):
        '''
      description= 'Send HTTP Get jobs/job_id request using invalid searcher login
      to check whether the the owner of jobs logged in as ‘Searcher’ can access this API and other searcher
      are forbidden to access the API at the endpoint', \test_id = MT_NT_GJ_GET_000
      expected_output = '204',
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
                                                   job_max_occurrence='9', job_assignment_duration='10',
                                                   job_lifetime_duration='363',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Square')
        expected_status_code = 201
        self.assertEqual(expected_status_code,response_post_job.status_code)
        self.job_id = response_post_job.json()['job_id']
        reponse = searcher.mturk_add_wots(self.job_id)
        response1 = searcher.mturk_add_qats(self.job_id,result)
        time.sleep(10)
        searcher = user.Searcher(self.username_searcher_one, self.password_searcher_one)
        response_get_jobs = searcher.mturk_get_job_with_id(self.job_id)
        expected_status_code = 204
        self.assertTrue(response_get_jobs)
        self.assertEqual(response_get_jobs.status_code, expected_status_code)


    def test_mturk_get_job_with_invalid_job_id(self):
        '''
            description= 'Send HTTP Get jobs/job_id request using unauthorised users login with invalid job_id
            ', \expected_output = '204',/test_id = MT_NT_GJ_GET_001
        '''

        list_of_existing_job_id = []
        manager = user.Manager(self.username_manager, self.password_manager)
        response_get_jobs = manager.mturk_get_jobs()
        for entry in response_get_jobs.json():
            list_of_existing_job_id.append(entry['job_id'])

        temp = '9qwerty'
        while temp in list_of_existing_job_id:
            temp += '9qwerty'
        try:
            invalid_job_id = temp
        except ValueError as e:
            raise

        expected_status_code = 200
        self.assertEqual(response_get_jobs.status_code, expected_status_code)

        manager = user.Manager(self.username_manager, self.password_manager)
        response_get_job_with_job_id = manager.mturk_get_job_with_id(invalid_job_id)
        expected_status_code = 404
        self.assertEqual(response_get_job_with_job_id.status_code, expected_status_code)

    def test_mturk_get_job_with_id_using_unauthorised_user(self):
        '''
      description= 'Send HTTP Get jobs/job_id request using invalid user login
      are forbidden to access the API at the endpoint', \test_id = MT_NT_GJ_GET_002
      expected_output = '204',
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='9', job_assignment_duration='10',
                                                   job_lifetime_duration='363',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Square')
        expected_status_code = 201
        self.assertEqual(expected_status_code,response_post_job.status_code)
        self.job_id = response_post_job.json()['job_id']
        time.sleep(10)
        worker = user.Worker(self.username_worker, self.password_worker)
        response_get_jobs = worker.mturk_get_job_with_id(self.job_id)
        expected_status_code = 403
        self.assertEqual(response_get_jobs.status_code, expected_status_code)


    def test_mturk_get_job_with_id_using_invalid_token(self):
        '''
      description= 'Send HTTP Get jobs/job_id request using invalid access token at the endpoint', \test_id = MT_NT_GJ_GET_003
      expected_output = '403 and 'Invalid or expired token.'',
      '''


        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P',
                                                   job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='9', job_assignment_duration='10',
                                                   job_lifetime_duration='363',
                                                   job_reward_per_hit='1', job_qats_per_hit='2',
                                                   job_tasks_per_hit='3',
                                                   job_boxing_type='Square')
        expected_status_code = 201
        self.assertEqual(expected_status_code,response_post_job.status_code)
        self.job_id = response_post_job.json()['job_id']
        time.sleep(10)
        response_get_jobs = searcher.mturk_get_job_with_id_tesing(self.job_id)
        expected_error = 'Invalid or expired token.'
        self.assertEqual(expected_error,response_get_jobs.json()['detail'])
        expected_status_code = 403
        self.assertEqual(response_get_jobs.status_code, expected_status_code)

obj1 = TestMturkGetJobOnBasisOfId()



