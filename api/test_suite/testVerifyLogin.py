from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()


class VerifyUser(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    #usernames
    username_searcher = 'searcher1'
    username_manager = 'manager1'
    username_worker = 'worker1'
    username_admin = 'sharedadmin'
    #passwords
    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    def test_verify_user_by_valid_token(self):
        '''Description : Post verify login and on the basis of valid token /
        excepted output : 200 /PT_VL_POST_000'''

        #Testing by searcher token
        searcher = user.User(self.username_searcher,self.password_searcher)
        token = searcher.login(self.username_searcher,self.password_searcher)
        #Fetching access token for verification
        access_token = token.json()['access']
        response_searcher =  searcher.verify_user(access_token)
        expected_status_code = 200
        expected_username = "searcher1"
        expected_user_id = 10
        # verifing username and user_id
        self.assertEqual(response_searcher.status_code,expected_status_code)
        self.assertEqual(response_searcher.json()['username'],expected_username)
        self.assertEqual(response_searcher.json()['user_id'],expected_user_id)

        # Testing by manager token
        manager = user.User(self.username_manager,self.password_manager)
        token = manager.login(self.username_manager,self.password_manager)
        # Fetching access token for verification
        access_token = token.json()['access']
        response_manager = manager.verify_user(access_token)
        expected_status_code = 200
        expected_username = "manager1"
        expected_user_id = 20
        # verifing username and user_id
        self.assertEqual(response_manager.json()['username'], expected_username)
        self.assertEqual(response_manager.json()['user_id'], expected_user_id)
        self.assertEqual(response_manager.status_code, expected_status_code)

        # Testing by worker token
        worker = user.User(self.username_worker, self.password_worker)
        token = worker.login(self.username_worker, self.password_worker)
        # Fetching access token for verification
        access_token = token.json()['access']
        response_worker = worker.verify_user(access_token)
        expected_status_code = 200
        expected_username = "worker1"
        expected_user_id = 14
        # verifing username and user_id
        self.assertEqual(response_worker.json()['username'], expected_username)
        self.assertEqual(response_worker.json()['user_id'], expected_user_id)
        self.assertEqual(response_worker.status_code, expected_status_code)

        # Testing by admin token
        admin = user.User(self.username_admin, self.password_admin)
        token = admin.login(self.username_admin, self.password_admin)
        # Fetching access token for verification
        access_token = token.json()['access']
        response_admin = worker.verify_user(access_token)
        expected_status_code = 200
        expected_username = "sharedadmin"
        expected_user_id = 23
        #verifing username and user_id
        self.assertEqual(response_admin.json()['username'], expected_username)
        self.assertEqual(response_admin.json()['user_id'], expected_user_id)
        self.assertEqual(response_admin.status_code, expected_status_code)

    def test_verify_user_by_invalid_token(self):
        '''Description : Post verify login and on the basis of invalid token /
                excepted output : 401 /test_id = NT_VL_POST_000'''
        searcher = user.User(self.username_searcher, self.password_searcher)
        token = searcher.login(self.username_searcher, self.password_searcher)
        # Fetching access token for verification
        access_token = token.json()['access']
        #Manipulating token
        response_searcher = searcher.verify_user(access_token + 'bsacsk6465dsl')
        error_code = response_searcher.json()['code']
        error = response_searcher.json()['detail']
        expected_error = 'Token is invalid or expired'
        expected_error_code = 'token_not_valid'
        expected_status_code = 401
        #Verifing username and user_id
        self.assertEqual(expected_error,error)
        self.assertEqual(error_code,expected_error_code)
        self.assertEqual(expected_status_code,response_searcher.status_code)

    def test_verify_user_by_null_token(self):
        '''Description : Post verify login and on the basis of null token /
                excepted output : 400/test_id = NT_VL_POST_001 '''
        searcher = user.User(self.username_searcher, self.password_searcher)
        access_token = ""
        response_searcher = searcher.verify_user(access_token)
        error = response_searcher.json()['token']
        expected_error = ["This field may not be blank."]
        expected_status_code = 400
        # comparing expected_error and error
        self.assertEqual(expected_status_code,response_searcher.status_code)
        self.assertEqual(error,expected_error)

