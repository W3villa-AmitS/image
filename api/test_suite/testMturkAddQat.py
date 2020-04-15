
import uuid
from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApisMturk
import urllib3
urllib3.disable_warnings()

class TestMturkAddQat(SimpleTestCase):
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
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                 {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                     "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                     "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

    '''Adding qat with valid credentials and valid data'''

    def test_add_qat_through_valid_user(self):
        '''
                  description= 'Send HTTP POST ADD_QAT request using searcher login
                  at the endpoint  with valid username and password',
                  expected_output = '202'/test_id = MT_PT_AQ_POST_000 ,
                  '''

        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEquals(expected_status_code, response_post_job.status_code)
        job_id = response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                              'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id,file)
        response_add_qat = searcher.mturk_add_qats(job_id,self.result)
        expected_status_code = 202
        self.assertEqual(expected_status_code,response_add_qat.status_code)


    '''Adding qat with valid credentials and  data
       and without wots ,expected_output = 400'''

    def test_add_qat_without_wots(self):

        ''' description= 'Send HTTP POST ADD_QAT request using searcher login without adding wots
            at the endpoint  with valid username and password',
            expected_output = '400',/test_id = MT_NT_AQ_POST_000'''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEqual(expected_status_code, response_post_job.status_code)
        job_id = response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_add_qat = searcher.mturk_add_qats(job_id,self.result)
        expected_status_code = 400
        self.assertEqual(expected_status_code , response_add_qat.status_code)


            # if response_add_qat.json()['job_number_of_more_qats_required_to_add'] == 0:
            #     break

    '''Adding qat with valid credentials and  data
       and without without image urls, expected_output = 400'''

    def test_add_qat_without_image_urls(self):

        '''
                                 description= 'Send HTTP POST ADD_QAT request using searcher login
                                 at the endpoint  with valid username and password',
                                 expected_output = '400'/test_id = MT_NT_AQ_POST_001,
                                 '''
        result_add_qat = {
            "qats": [{"image_url": "", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                     {"image_url": "", "result": {
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
        self.assertEqual(expected_status_code, response_post_job.status_code)
        job_id = response_post_job.json()['job_id']

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}
        searcher.mturk_add_wots_new(job_id,file)
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_add_qat = searcher.mturk_add_qats(job_id,result_add_qat)
        expected_status_code = 202
        self.assertEqual(expected_status_code, response_add_qat.status_code)
        '''Adding qatwith valid credentials and  data
       and  with 'GET' request expected_output = 405'''

    def test_add_qat_by_get_request(self):

        '''
                         description= 'Send HTTP POST ADD_QAt request using searcher login
                         at the endpoint  with GET type request',
                         expected_output = '201'/test_id = MT_NT_AQ_POST_002,
                         '''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEqual(expected_status_code, response_post_job.status_code)
        job_id = response_post_job.json()['job_id']

        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}
        searcher.mturk_add_wots_new(job_id,file)

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_add_qat = searcher.test_mturk_add_qats(job_id,self.result)
        expected_status_code = 405
        self.assertEqual(expected_status_code, response_add_qat.status_code)


    def test_add_qat_with_insufficient_images(self):
        '''description= 'Send HTTP POST ADD_QAt request using searcher login
                         at the endpoint  with insufficient images in csv or json',
                         expected_output = '202'/test_id = MT_NT_AQ_POST_003'''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                               job_description='Testing',
                                               job_max_occurrence='10', job_assignment_duration='10',
                                               job_lifetime_duration='365',
                                               job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                               job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEqual(expected_status_code, response_post_job.status_code)
        job_id = response_post_job.json()['job_id']

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}
        searcher.mturk_add_wots_new(job_id,file)
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_add_qat = searcher.mturk_add_qats(job_id,result)
        expected_status_code = 202
        self.assertEqual(expected_status_code,response_add_qat.status_code)

    def test_add_qat_with_empty_result(self):
        '''
                  description= 'Send HTTP POST ADD_QAT request using searcher login
                  at the endpoint  with empty result',
                  expected_output = '202'/test_id =  MT_NT_AQ_POST_004 ,
                  '''

        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEquals(expected_status_code, response_post_job.status_code)
        job_id = response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                              'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id,file)
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                "cars": [],
                "bikes": []}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                         "cars": [],
                         "bikes": []}}]}

        response_add_qat = searcher.mturk_add_qats(job_id,result)
        expected_status_code = 202
        self.assertEqual(expected_status_code,response_add_qat.status_code)

    def test_add_qat_with_less_attributes(self):
        '''
                  description= 'Send HTTP POST ADD_QAT request using searcher login
                  at the endpoint  with less attributes',
                  expected_output = '202'/test_id = MT_NT_AQ_POST_005 ,
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
        job_id = response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                }},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                         "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                         }}]}
        response_add_qat = searcher.mturk_add_qats(job_id,result)
        expected_status_code = 202
        self.assertEqual(expected_status_code, response_add_qat.status_code)

    def test_add_qat_through_float_type_result(self):
        '''
                  description= 'Send HTTP POST ADD_QAT request using searcher login
                  at the endpoint  with float type result',
                  expected_output = '202'/test_id =  MT_NT_AQ_POST_006 ,
                  '''

        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEquals(expected_status_code, response_post_job.status_code)
        job_id = response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                              'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id,file)
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                "cars": [{"x1": "95.11", "y1": "267.11", "x2": "197.11", "y2": "340.11"}],
                "bikes": [{"x1": "95.11", "y1": "267.11", "x2": "197.11", "y2": "340.11"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                         "cars": [{"x1": "95.11", "y1": "267.11", "x2": "197.11", "y2": "340.11"}],
                         "bikes": [{"x1": "95.11", "y1": "267.11", "x2": "197.11", "y2": "340.11"}]}}]}

        response_add_qat = searcher.mturk_add_qats(job_id,result)
        expected_status_code = 202
        self.assertEqual(expected_status_code,response_add_qat.status_code)


    '''Adding qat with valid credentials and  data
       and without wots ,expected_output = 400'''

    def test_add_qat_string_type_result(self):

        ''' description= 'Send HTTP POST ADD_QAT request using searcher login without adding wots
            at the endpoint  with string type result',
            expected_output = '400',/test_id =  MT_NT_AQ_POST_007'''

        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_post_job = searcher.mturk_add_job(job_name='test Mturk job', job_type='P', job_attributes='cars,bikes',
                                                   job_description='Testing',
                                                   job_max_occurrence='10', job_assignment_duration='10',
                                                   job_lifetime_duration='365',
                                                   job_reward_per_hit='1', job_qats_per_hit='2', job_tasks_per_hit='3',
                                                   job_boxing_type='Rectangle')
        expected_status_code = 201
        self.assertEqual(expected_status_code, response_post_job.status_code)
        job_id = response_post_job.json()['job_id']
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        file = {'csv_file': ('xyz.csv',
                             'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350,')}

        searcher.mturk_add_wots_new(job_id, file)
        result = {
            "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                "cars": [{"x1": "ninty", "y1": "twenty", "x2": "ninteen", "y2": "thirtyfour"}],
                "bikes": [{"x1": "nintyfive", "y1": "twentysix", "x2": "ninteen", "y2": "thirtyfour"}]}},
                     {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg'", "result": {
                         "cars": [{"x1": "ninty", "y1": "twenty", "x2": "ninteen", "y2": "thirtyfour"}],
                         "bikes": [{"x1": "nintyfive", "y1": "twentysix", "x2": "ninteen", "y2": "thirtyfour"}]}}]}

        response_add_qat = searcher.mturk_add_qats(job_id,result)
        expected_status_code = 202
        self.assertEqual(expected_status_code , response_add_qat.status_code)


obj = TestMturkAddQat()


