from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import time,random,string,json


class TestPostTaskResult(SimpleTestCase):
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

    result = {
        "qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
            "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
            "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}},
                 {"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg", "result": {
                     "cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                     "bikes": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}]}}]}

    def test_post_task_result_by_valid_user(self):
        '''Description : Send HTTP POST request using worker login with valid task id
         :expected output : 200/test_id = PT_PTR_POST_000'''


        # Creating new job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        # Fetching job_id
        job_id = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id)
        # Adding qats
        searcher.add_qats(job_id,self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id)
        # worker login and perform task by posting self.result.
        time.sleep(10)
        worker = user.Worker(self.username_worker, self.password_worker)
        response_task_id = worker.get_random_task(job_id)
        error = response_task_id.json()['error']
        jobid = response_task_id.json()['job_id']
        if error == 'Worker already active on another job.':
            worker.post_disengage_job(jobid)
        response_task_id = worker.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        time.sleep(5)
        response_worker = worker.post_task_result(task_id,result)
        expected_status_code = 200
        self.assertEqual(response_worker.status_code,expected_status_code)

    def test_post_task_result_by_invalid_user(self):

        '''Description : Post task result by invalid user with valid credentials
            expected output : "You do not have permission to perform this action.",
        /status code 403 /test_id= NT_PTR_POST_000'''

        # Creating new job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        # Fetching job_id
        job_id = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id)
        # Adding qats
        searcher.add_qats(job_id,self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id)
        # worker login and perform task by posting result.
        time.sleep(5)
        worker = user.Worker(self.username_worker, self.password_worker)
        response_task_id = worker.get_random_task(job_id)
        error = response_task_id.json()['error']
        jobid = response_task_id.json()['job_id']
        if error == 'Worker already active on another job.':
            worker.post_disengage_job(jobid)
        worker.get_random_task(job_id)
        response_task_id = worker.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        #posting result through manager
        manager = user.Manager(self.username_manager,self.password_manager)
        response_manager = manager.post_task_result(task_id,self.result)
        error = response_manager.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code = 403
        self.assertEqual(expected_status_code,response_manager.status_code)
        self.assertEqual(expected_error,error)
        # posting result through searcher
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        response_searcher = searcher.post_task_result(task_id,self.result)
        error = response_searcher.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code = 403
        self.assertEqual(expected_status_code, response_manager.status_code)
        self.assertEqual(expected_error, error)
        # posting result through Admin
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_admin = admin.post_task_result(task_id,self.result)
        error = response_admin.json()['detail']
        expected_error = "You do not have permission to perform this action."
        expected_status_code = 403
        self.assertEqual(expected_status_code, response_manager.status_code)
        self.assertEqual(expected_error, error)

    def test_post_task_result_invalid_task_id(self):
        '''Description : Post task result by valid user with valid credentials,
        /passing invalid task_id , expected output : "Invalid task "/status code 404
        /test_id= NT_PTR_POST_001'''

        # Creating new job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        # Fetching job_id
        job_id = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id)
        searcher.add_qats(job_id,self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id)
        # worker login and perform task by posting result.
        time.sleep(10)
        worker = user.Worker(self.username_worker, self.password_worker)
        response_task_id = worker.get_random_task(job_id)
        error = response_task_id.json()['error']
        jobid = response_task_id.json()['job_id']
        if error == 'Worker already active on another job.':
            worker.post_disengage_job(jobid)
        worker.get_random_task(job_id)
        response_task_id = worker.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        response_worker = worker.post_task_result(task_id+'hjas', self.result)
        expected_status_code = 404
        error = response_worker.json()['error']
        expected_error = "Invalid task"
        self.assertEqual(error,expected_error)
        self.assertEqual(response_worker.status_code, expected_status_code)

    def test_post_task_result_on_not_active_job(self):
        '''Description : Post task result by valid user with valid credentials
            on non active job expected output : "Worker not active on job with job_id "
            /expected status code  406/ test_id = NT_PTR_POST_002'''

        # Creating new job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        # Fetching job_id
        job_id = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id)
        # Adding qats
        searcher.add_qats(job_id,self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id)
        # worker login and perform task by posting result.
        time.sleep(10)
        worker = user.Worker(self.username_worker, self.password_worker)
        response_task_id = worker.get_random_task(job_id)
        error = response_task_id.json()['error']
        jobid = response_task_id.json()['job_id']
        if error == 'Worker already active on another job.':
            worker.post_disengage_job(jobid)
        # worker = worker.get_random_task(jobid)
        response_task_id = worker.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        result = json.dumps(result)
        worker.post_task_result(task_id, result)


        '''Second scenario'''
        # Creating new job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')

        # Fetching job_id
        job_id_new = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id_new)
        # Adding qats
        searcher.add_qats(job_id_new ,self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id_new)
        # worker login and perform task by posting result.
        time.sleep(10)
        worker = user.Worker(self.username_worker, self.password_worker)
        response_task_id = worker.get_random_task(job_id)
        error_id = response_task_id.json()['job_id']
        error = response_task_id.json()['error']
        jobidnew = response_task_id.json()['job_id']
        if error == 'Worker already active on another job.':
            worker.post_disengage_job(jobidnew)
        # worker = worker.get_random_task(jobid)
        response_task_id = worker.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        result = json.dumps(result)
        response_worker = worker.post_task_result(task_id,result)
        error = response_worker.json()['error']
        expected_error = "Worker not active on job with job_id "+ "'" +str(error_id)+"'"
        expected_status_code = 406
        self.assertEqual(error,expected_error)
        self.assertEqual(expected_status_code,response_worker.status_code)

    def test_post_task_result_on_same_task_id(self):
        '''Description :Send HTTP POST request using worker  login on same task id
        expected output : "Re-submission of the result for the same task is not allowed."/
        status code : 406 /test_id = NT_PTR_POST_003'''

        # Creating new job
        searcher = user.Searcher(self.username_searcher, self.password_searcher)
        # Posting job
        response_post_job = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes',
                                             job_description='test2 job',
                                             job_instructions='test2 job', task_max_occurrence='5',
                                             job_criteria_age_min='18',
                                             job_criteria_age_max='60', job_criteria_location='India',
                                             job_initial_qats='2',
                                             job_qat_frequency='5', job_criteria_gender=self.gender,
                                             job_criteria_grade='D', job_boxing_type='Rectangle')
        job_id = response_post_job.json()['job_id']
        # Adding wot's
        searcher.add_wots(job_id)
        searcher.add_qats(job_id,self.result)
        time.sleep(10)
        manager = user.Manager(self.username_manager, self.password_manager)
        manager.approve_job(job_id)
        # worker login and perform task by posting result.
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        user_name = x
        email = str(x) +'@idemia.com'
        time.sleep(10)
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_post_user = admin.create_users(user_name, 'Password@123',email, 'A', 'W')
        username_worker = response_post_user.json()['username']
        password = 'Password@123'
        worker = user.Worker(username_worker, password)
        # worker.get_random_task(job_id)
        response_task_id = worker.get_random_task(job_id)
        task_id = response_task_id.json()['task_id']
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        result = json.dumps(result)
        worker.post_task_result(task_id,result)
        response_resubmission = worker.post_task_result(task_id,result)
        error = response_resubmission.json()['error']
        expected_error = "Re-submission of the result for the same task is not allowed."
        expected_status_code = 406
        self.assertEqual(expected_status_code,response_resubmission.status_code)
        self.assertEqual(expected_error,error)

