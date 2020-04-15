from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import string,random

class TestGetDetailsOfUsers(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    count = 0

    def setUp(self):
        pass

# test whether GET users with {user_id} api returns detail of user with respect to user_id
    def test_get_details_of_user_with_valid_user_and_valid_id(self):
        '''description= 'Send HTTP Get users by user_id request using  valid login
            at the endpoint  with valid username and password', \
            expected_output = '200',test_id = PT_SU_GET_000
                       '''

        manager = user.Manager('manager1', 'Insidethepyramid@2')
        response_get_user_with_user_id = manager.get_users_with_id(1)
        expected_status_code = 200
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)


        admin = user.Administrator('sharedadmin', 'WY+e5nsQg-43565!')
        response_get_user_with_user_id = admin.get_users_with_id(2)
        expected_status_code = 200
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)

# test whether GET users with {user_id} api returns a permission denied status (Forbidden) in case of searcher and worker login
    def test_get_details_of_user_with_unauthorised_user_and_valid_id(self):
        '''
                       description= 'Send HTTP Get user by user_id request using  invalid login
                       at the endpoint  with valid username and password', \
                       expected_output = '403',test_id = NT_SU_GET_000
                       '''

        searcher = user.Searcher('searcher1', 'Belowthepyramid@2')
        response_get_user_with_user_id = searcher.get_users_with_id(1)
        expected_status_code = 403
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)

        worker = user.Worker('worker1', 'Nearthepyramid@2')
        response_get_user_with_user_id = worker.get_users_with_id(2)
        expected_status_code = 403
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)

# test whether GET users with {user_id} api returns Not found 404 in case of invalid user_id
    def test_get_details_of_user_with_authorised_user_and_invalid_id(self):
        '''
             description= 'Send HTTP Get user by  valid login request using  invalid user_id
             at the endpoint  with valid username and password', \
            expected_output = '404',test_id = NT_SU_GET_001
                              '''
        random_string = string.digits
        stringLength = 10
        invalid_user_id = ''.join(random.sample(random_string, stringLength))
        manager = user.Manager('manager1', 'Insidethepyramid@2')
        response_get_user_with_user_id = manager.get_users_with_id(invalid_user_id)
        expected_status_code = 404
        error = response_get_user_with_user_id.json()['error']
        expected_error = "No such user exist"
        self.assertEqual(error,expected_error)
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)

        admin = user.Administrator('sharedadmin', 'WY+e5nsQg-43565!')
        response_get_user_with_user_id = admin.get_users_with_id(invalid_user_id)
        expected_status_code = 404
        error = response_get_user_with_user_id.json()['error']
        expected_error = "No such user exist"
        self.assertEqual(expected_error,error)
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)

    def test_get_details_of_user_with_zero_user_id(self):
        '''description= 'Send HTTP Get users by user_id request 0 in user_id
            at the endpoint  with valid username and password', \
            expected_output = '200',test_id = NT_SU_GET_002
                       '''

        manager = user.Manager('manager1', 'Insidethepyramid@2')
        response_get_user_with_user_id = manager.get_users_with_id(0)
        expected_status_code =404
        expected_error = 'No such user exist'
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)
        self.assertEqual(expected_error,response_get_user_with_user_id.json()['error'])


    def test_get_details_of_user_with_null_user_id(self):
        '''description= 'Send HTTP Get users by user_id request using  Null at user_id
            at the endpoint  with valid username and password', \
            expected_output = '200',test_id = NT_SU_GET_003
                       '''

        manager = user.Manager('manager1', 'Insidethepyramid@2')
        response_get_user_with_user_id = manager.get_users_with_id(None)
        expected_status_code =400
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)

    def test_get_details_of_user_without_login(self):
        '''description= 'Send HTTP Get users by user_id request without user login
            at the endpoint  with valid username and password', \
            expected_output = '200',test_id = NT_SU_GET_004
                       '''

        response_get_user_with_user_id = userApis.get_users_with_id(1,None )
        expected_error = 'token_not_valid'
        expected_status_code = 401
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)
        self.assertEqual(expected_error,response_get_user_with_user_id.json()['code'])

    def test_get_user_with_id_with_invalid_access_token(self):
        '''description= 'Send HTTP Get users by user_id request with invalid access_token
                  at the endpoint  with valid username and password', \
                  expected_output = '401',test_id = NT_SU_GET_005
                             '''
        manager = user.Manager('manager1', 'Insidethepyramid@2')
        response_get_user_with_user_id = manager.get_users_with_id_using_invalid_token(1)
        expected_error = 'token_not_valid'
        expected_status_code = 401
        self.assertEqual(response_get_user_with_user_id.status_code, expected_status_code)
        self.assertEqual(response_get_user_with_user_id.json()['code'],expected_error)

