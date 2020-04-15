import sys
import os
import token

sys.path.append(os.path.abspath(''))
#sys.path.append('D:\\Git\\ImageFactory\\dev\\backend\\api\\')
from test_suite.config import constant
from test_suite.lib.apis import userApis
from test_suite.lib.apis import userApisMturk

class User:
    """
    Base class for all the users in image factory.
    """
    def __init__(self, username, password):
        self.user_name = username
        self.password = password
        self.response = self.login(self.user_name, self.password)
        self.access_token = self.get_access_token(self.response)
    
    def login(self, username, password):
        return userApis.login(username, password)

    def get_access_token(self, response):
        return response.json()['access']

    def verify_user(self, access_token):
        return userApis.verify_user(access_token)


class MturkWorker():
    def __init__(self,hit_id, assignment_id, worker_id):
        self.response = userApisMturk.mturk_get_token(hit_id, assignment_id, worker_id)
        self.response_test = userApisMturk.mturk_get_token_testing(hit_id, assignment_id, worker_id)
        self.session_token = self.get_session_token(self.response)

    def export_session_token(self):
        if self.session_token:
            return self.session_token
        else:
            return
    def export_response(self):
        return self.response

    def get_session_token(self, response):
        try:
            return response.json()['token']
        # TODO name exception
        except:
            return


    def mturk_get_task(self,mturk_token):
            return userApisMturk.mturk_get_task(mturk_token)


class MturkUser():
        def __init__(self, hit_id, assignment_id, worker_id):
            self.hit_id = hit_id
            self.assignment_id = assignment_id
            self.worker_id = worker_id
            # response = self.mturk_token(self.hit_id,self.assignment_id,self.worker_id)
            # self.mturk_token = self.mturk_token(response)

        def mturk_get_token(self, hit_id, assignment_id, worker_id):
            return userApisMturk.mturk_get_token(hit_id, assignment_id, worker_id)

        #For testing of API without Hit_id
        def mturk_get_token_testing_without_hit_id(self,assignment_id, worker_id):
            return userApisMturk.mturk_get_token_testing_without_hit_id(assignment_id,worker_id)

        def mturk_get_task(self,mturk_token):
            return userApisMturk.mturk_get_task(mturk_token)

        #For testing of get_task with worng url
        def mturk_get_task_testing(self,mturk_token):
            return userApisMturk.mturk_get_task_testing(mturk_token)

        def mturk_post_task_result(self,task_id,result,token):
            return  userApisMturk.mturk_post_task_result(task_id,result,token)

        def mturk_post_task_result_test_new(self,result, token):
            return  userApisMturk.mturk_post_task_result_test_new(result, token)

        def mturk_get_token_testing(self, hit_id, assignment_id, worker_id):
            # print("printing inside user", hit_id, assignment_id, worker_id)
            return userApisMturk.mturk_get_token_testing(hit_id, assignment_id, worker_id)


class Worker(User):
    def __init__(self, username, password):
        super().__init__(username, password)

    def get_task(self, job_id):
        return userApis.get_task(job_id, self.access_token)

    def post_task_result(self, task_id, result):
        return userApis.post_task_result(task_id, result, self.access_token)
        
    def get_jobs(self):
        return userApis.get_jobs(self.access_token)    

    def get_users(self):
        return userApis.get_users(self.access_token)

    def get_users_with_id(self,user_id):
        return userApis.get_users_with_id(user_id,self.access_token)

    def get_job_with_id(self, user_id):
        return userApis.get_job_with_id(user_id, self.access_token)

    def delete_user_with_id(self, user_id):
        return userApis.delete_user_with_id(user_id, self.access_token)
        
    def get_random_task(self,job_id):
        return userApis.get_random_task(job_id,self.access_token)

    def create_users(self, username, password,email,state,roles):
        return userApis.create_users(username, password,email,state,roles,self.access_token)
        
    def get_job_status_list(self, status):
        return userApis.get_job_status_list(status, self.access_token)

    def mturk_get_job_status_list(self, status):
        return userApisMturk.mturk_get_job_status_list(status, self.access_token)

    def engaged_worker(self, job_id):
        return userApis.engaged_worker(job_id, self.access_token)
        
    def post_disengage_job(self,job_id):
        return userApis.post_disengage_job(job_id, self.access_token)

    #for testing purpose only with invalid access token
    def post_disengage_job_testing(self,job_id):
        return userApis.post_disengage_job(job_id, self.access_token+"hello")

    def add_wots(self, job_id):
        return userApis.add_wots(job_id,self.access_token)

    def mturk_add_wots(self, job_id,file):
         return userApisMturk.mturk_add_wots(job_id,self.access_token,file)

    def mturk_add_wots_new(self, job_id, file):
        return userApisMturk.mturk_add_wots_new(job_id, self.access_token, file)
		
    def mturk_add_qat(self, job_id, image_url, result):
         return userApisMturk.mturk_add_qat(job_id, image_url, result, self.access_token)

    def mturk_add_qats(self, job_id, result):
        return userApisMturk.mturk_add_qats(job_id, result, self.access_token)

    def add_qats(self, job_id, result):
        return userApis.add_qats(job_id, result, self.access_token)
	
    def mturk_post_task_result(self, task_id, result):
         return userApis.post_task_result(task_id, result,self.mturk_get_token)
		
    def mturk_get_token(self,hit_id,assignment_id,worker_id):
        return  userApisMturk.mturk_get_token(hit_id,assignment_id,worker_id)

    def approve_job(self, job_id):
        return userApis.approve_job(job_id, self.access_token)

    def disapprove_job(self, job_id):
        return userApis.disapprove_job(job_id, self.access_token)

    def mturk_get_job_with_id(self,job_id):
        return userApisMturk.mturk_get_job_with_id(job_id,self.access_token)

    def mturk_download_result_by_job_id(self,job_id):
        return userApisMturk.mturk_download_result_by_job_id(job_id,self.access_token)

    def mturk_download_result_by_job_id_and_worker_id(self,job_id):
        return userApisMturk.mturk_download_result_by_job_id_and_worker_id(job_id,self.access_token)

    def mturk_consolidate_result_of_job_id(self, job_id):
        return userApisMturk.mturk_consolidate_result_of_job_id(job_id, self.access_token)

    def mturk_consolidate_result_of_task_id(self, task_id):
        return userApisMturk.mturk_consolidate_result_of_task_id(task_id, self.access_token)


class Searcher(User):
    def __init__(self, username, password):
        super().__init__(username, password)

    def add_job(self, job_name, job_type, job_attributes, job_description, job_instructions, task_max_occurrence, job_criteria_age_min, job_criteria_age_max, job_criteria_location, job_initial_qats, job_qat_frequency, job_criteria_gender, job_criteria_grade,job_boxing_type):
        return userApis.post_job(job_name, job_type, job_attributes, job_description, job_instructions, task_max_occurrence, job_criteria_age_min, job_criteria_age_max, job_criteria_location, job_initial_qats, job_qat_frequency, job_criteria_gender, job_criteria_grade,job_boxing_type,self.access_token)

    def mturk_add_job(self, job_name, job_type, job_attributes, job_description, job_max_occurrence, job_assignment_duration, job_lifetime_duration, job_reward_per_hit, job_qats_per_hit, job_tasks_per_hit,job_boxing_type):
        return userApisMturk.mturk_post_job(job_name, job_type, job_attributes, job_description, job_max_occurrence, job_assignment_duration, job_lifetime_duration,job_reward_per_hit, job_qats_per_hit, job_tasks_per_hit, job_boxing_type, self.access_token)


    # For testiing pupose only "post mturk job with integer type attribute in payload"
    def mturk_add_job_testing(self, job_name, job_type, job_attributes, job_description, job_max_occurrence, job_assignment_duration, job_lifetime_duration, job_reward_per_hit, job_qats_per_hit, job_tasks_per_hit,job_boxing_type):
        return userApisMturk.mturk_post_job_testing(job_name, job_type, job_attributes, job_description, job_max_occurrence, job_assignment_duration, job_lifetime_duration,job_reward_per_hit, job_qats_per_hit, job_tasks_per_hit, job_boxing_type, self.access_token)


    def mturk_add_qat(self, job_id, image_url, result):
        return userApisMturk.mturk_add_qat(job_id, image_url, result, self.access_token)

    def add_qat(self, job_id, image_url, result):
        return userApis.add_qat(job_id, image_url, result,self.access_token)

    def add_qats(self, job_id, result):
        return userApis.add_qats(job_id, result, self.access_token)

    def test_mturk_add_qat(self, job_id,image_url, result):
         return userApisMturk.test_mturk_add_qat(job_id, image_url, result, self.access_token)

    def mturk_add_qats(self, job_id, result):
        return userApisMturk.mturk_add_qats(job_id, result, self.access_token)

    def test_mturk_add_qats(self, job_id, result):
        return userApisMturk.test_mturk_add_qats(job_id, result, self.access_token)

    def add_wots(self, job_id):
        return userApis.add_wots(job_id,self.access_token)

    def add_wots_without_csv(self, job_id,file):
         return userApis.add_wots_without_csv(job_id,self.access_token,file)

    def mturk_add_wots(self, job_id):
        return userApisMturk.mturk_add_wots(job_id,self.access_token)

    def mturk_add_wots_new(self, job_id,file):
         return userApisMturk.mturk_add_wots_new(job_id,self.access_token,file)

    def test_mturk_add_wots(self, job_id,file):
         return userApisMturk.test_mturk_add_wots(job_id,self.access_token,file)

    def test_mturk_add_wots_new(self, job_id):
        return userApisMturk.test_mturk_add_wots_new(job_id,self.access_token)

    def mturk_add_wots_get_method(self, job_id,file):
        return userApisMturk.mturk_add_wots_get_method(job_id,self.access_token,file)

    def get_job(self, job_id):
        return userApis.get_job(job_id, self.access_token)

    def post_task_result(self,task_id,result):
        return userApis.post_task_result(task_id,result, self.access_token)

    def get_jobs(self):
        return userApis.get_jobs(self.access_token)

    def get_users(self):
        return userApis.get_users(self.access_token)

    def get_users_with_id(self,user_id):
        return userApis.get_users_with_id(user_id,self.access_token)


    def get_job_with_id(self, user_id):
        return userApis.get_job_with_id(user_id, self.access_token)

    def mturk_get_job_with_id(self,job_id):
        return userApisMturk.mturk_get_job_with_id(job_id,self.access_token)

    #For testing of get job on basis of id with invalid token
    def mturk_get_job_with_id_testing(self,job_id):
        return userApisMturk.mturk_get_job_with_id(job_id,self.access_token+"hello")

    def delete_user_with_id(self, user_id):
        return userApis.delete_user_with_id(user_id, self.access_token)

    def create_users(self, username, password,email,state,roles):
        return userApis.create_users(username, password,email,state,roles,self.access_token)

    def get_job_status_list(self, status):
        return userApis.get_job_status_list(status, self.access_token)

    def mturk_get_job_status_list(self, status):
        return userApisMturk.mturk_get_job_status_list(status, self.access_token)

    #for testing for api with invalid access token
    def mturk_get_job_status_list_testing(self, status):
        return userApisMturk.mturk_get_job_status_list(status, self.access_token+"helllo")

    def engaged_worker(self, job_id):
        return userApis.engaged_worker(job_id, self.access_token)

    def post_disengage_job(self,job_id):
        return userApis.post_disengage_job(job_id, self.access_token)

    def get_random_task(self,job_id):
        return userApis.get_random_task(job_id,self.access_token)

    def mturk_get_jobs(self):
        return userApisMturk.mturk_get_jobs(self.access_token)

    def mturk_approve_job(self, job_id):
        return userApisMturk.mturk_approve_job(job_id, self.access_token)

    def mturk_disapprove_job(self, job_id):
        return userApisMturk.mturk_disapprove_job(job_id, self.access_token)

    def mturk_get_token(self,hit_id,assignment_id,worker_id):
        return  userApisMturk.mturk_get_token(hit_id,assignment_id,worker_id)

    def post_deactivate(self, user_id, type ="POST"):
        return userApis.post_deactivate(user_id, self.access_token, type)

    def post_activate(self,user_id,type = "POST"):
        return userApis.post_activate(user_id,self.access_token,type)

    def approve_job(self, job_id):
        return userApis.approve_job(job_id, self.access_token)

    def disapprove_job(self, job_id):
        return userApis.disapprove_job(job_id, self.access_token)

    def download_qats(self,job_id):
        return userApis.download_qats(job_id,self.access_token)


    def mturk_download_qats(self, job_id):
        return userApisMturk.mturk_add_qats(job_id, self.access_token)

    def download_result(self,job_id):
        return userApis.download_result(job_id,self.access_token)

    def mturk_download_result_by_job_id(self,job_id):
        return userApisMturk.mturk_download_result_by_job_id(job_id,self.access_token)



class Manager(User):
    def __init__(self, username, password):
        super().__init__(username, password)

    def approve_job(self, job_id):
        return userApis.approve_job(job_id, self.access_token)

    def mturk_approve_job(self, job_id):
        return userApisMturk.mturk_approve_job(job_id, self.access_token)

    def mturk_disapprove_job(self, job_id):
        return userApisMturk.mturk_disapprove_job(job_id, self.access_token)

    def disapprove_job(self, job_id):
        return userApis.disapprove_job(job_id, self.access_token)

    def get_jobs(self):
        return userApis.get_jobs(self.access_token)

    def mturk_get_jobs(self):
        return userApisMturk.mturk_get_jobs(self.access_token)

    def get_users(self):
        return userApis.get_users(self.access_token)

    # for testing purpose only with invalid access_token
    def get_users_invalid_access_token(self):
        return userApis.get_users(self.access_token+"hello")

    def get_users_with_id(self,user_id):
        return userApis.get_users_with_id(user_id,self.access_token)

        # for testing purpose only with invalid access_token
    def get_users_with_id_using_invalid_token(self, user_id):
        return userApis.get_users_with_id(user_id, self.access_token + "hello")

    def get_job_with_id(self,user_id):
        return userApis.get_job_with_id(user_id,self.access_token)

    def delete_user_with_id(self, user_id):
        return userApis.delete_user_with_id(user_id, self.access_token)

    def create_users(self, username, password,email,state,roles):
        return userApis.create_users(username, password,email,state,roles,self.access_token)

    def get_job_status_list(self, status):
        return userApis.get_job_status_list(status, self.access_token)

    def mturk_get_job_status_list(self, status):
        return userApisMturk.mturk_get_job_status_list(status, self.access_token)

    def engaged_worker(self, job_id):
        return userApis.engaged_worker(job_id, self.access_token)

    def post_disengage_job(self,job_id):
        return userApis.post_disengage_job(job_id, self.access_token)

    def add_wots(self, job_id):
        return userApis.add_wots(job_id,self.access_token)

    def get_random_task(self,job_id):
        return userApis.get_random_task(job_id,self.access_token)

    def mturk_add_job(self, job_name, job_type, job_attributes, job_description, job_max_occurrence, job_assignment_duration, job_lifetime_duration,job_reward_per_hit, job_qats_per_hit, job_tasks_per_hit,job_boxing_type):
        return userApisMturk.mturk_post_job(job_name, job_type, job_attributes, job_description, job_max_occurrence,job_assignment_duration, job_lifetime_duration, job_reward_per_hit, job_qats_per_hit, job_tasks_per_hit, job_boxing_type, self.access_token)

    def mturk_add_wots(self, job_id,file):
        return userApisMturk.mturk_add_wots(job_id,self.access_token,file)

    def mturk_add_wots_new(self, job_id, file):
        return userApisMturk.mturk_add_wots_new(job_id, self.access_token, file)

    def mturk_add_qat(self, job_id, image_url, result):
        return userApisMturk.mturk_add_qat(job_id, image_url, result, self.access_token)

    def mturk_add_qats(self, job_id, result):
        return userApis.mturk_add_qats(job_id, result, self.access_token)

    def add_qats(self, job_id, result):
        return userApis.add_qats(job_id, result, self.access_token)

    def mturk_get_job_with_id(self,job_id):
        return userApisMturk.mturk_get_job_with_id(job_id,self.access_token)

    def mturk_get_token(self,hit_id,assignment_id,worker_id):
        return  userApisMturk.mturk_get_token(hit_id,assignment_id,worker_id)

    def mturk_post_task_result(self, task_id, result):
         return userApis.post_task_result(task_id, result,self.mturk_get_token)

    def post_task_result(self, task_id, result):
        return userApis.post_task_result(task_id, result, self.access_token)


    def mturk_download_result_by_job_id(self,job_id):
        return userApisMturk.mturk_download_result_by_job_id(job_id,self.access_token)

    def mturk_download_result_by_job_id_and_worker_id(self,job_id,worker_id):
        return userApisMturk.mturk_download_result_by_job_id_and_worker_id(job_id,worker_id,self.access_token)

    def mturk_consolidate_result_of_job_id(self,job_id):
        return  userApisMturk.mturk_consolidate_result_of_job_id(job_id,self.access_token)

    def mturk_consolidate_result_of_task_id(self, task_id):
        return userApisMturk.mturk_consolidate_result_of_task_id(task_id, self.access_token)


class Administrator(User):
    def __init__(self, username, password):
        super().__init__(username, password)

    def create_user(self):
            pass
    
    def get_jobs(self):
        return userApis.get_jobs(self.access_token)    

    def get_users(self):
        return userApis.get_users(self.access_token)

    def get_users_with_id(self,user_id):
        return userApis.get_users_with_id(user_id,self.access_token)

    def get_job_with_id(self, user_id):
        return userApis.get_job_with_id(user_id, self.access_token)

    def delete_user_with_id(self, user_id):
        return userApis.delete_user_with_id(user_id, self.access_token)

    def create_users(self, username, password,email,state,roles):
        return userApis.create_users(username, password,email,state,roles,self.access_token)
        
    def get_job_status_list(self, status):
        return userApis.get_job_status_list(status, self.access_token)

    def mturk_get_job_status_list(self, status):
        return userApisMturk.mturk_get_job_status_list(status, self.access_token)

    def engaged_worker(self, job_id):
        return userApis.engaged_worker(job_id, self.access_token)
        
    def post_disengage_job(self,job_id):
        return userApis.post_disengage_job(job_id, self.access_token)

    def get_random_task(self,job_id):
        return userApis.get_random_task(job_id,self.access_token)

    def add_wots(self, job_id):
        return userApis.add_wots(job_id,self.access_token)
		
    def mturk_add_wots(self, job_id,file):
         return userApisMturk.mturk_add_wots(job_id,self.access_token,file)

    def mturk_add_wots_new(self, job_id, file):
        return userApisMturk.mturk_add_wots_new(job_id, self.access_token, file)

    def mturk_add_qat(self, job_id, image_url, result):
        return userApisMturk.mturk_add_qat(job_id, image_url, result, self.access_token)

    def add_qats(self, job_id, result):
        return userApis.add_qats(job_id, result, self.access_token)

    def mturk_add_qats(self, job_id, result):
        return userApis.mturk_add_qats(job_id, result, self.access_token)

    def mturk_post_task_result(self, task_id, result):
        return userApis.post_task_result(task_id, result, self.mturk_get_token)

    def mturk_get_token(self,hit_id,assignment_id,worker_id):
         return  userApisMturk.mturk_get_token(hit_id,assignment_id,worker_id)

    def post_activate(self,user_id,type = "POST"):
        return userApis.post_activate(user_id,self.access_token,type)

    def post_deactivate(self, user_id, type = "POST"):
        return userApis.post_deactivate(user_id, self.access_token, type)

    def approve_job(self, job_id):
        return userApis.approve_job(job_id, self.access_token)

    def disapprove_job(self, job_id):
        return userApis.disapprove_job(job_id, self.access_token)

    def post_task_result(self, task_id, result):
        return userApis.post_task_result(task_id, result, self.access_token)
