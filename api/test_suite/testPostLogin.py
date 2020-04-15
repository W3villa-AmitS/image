from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()

class TestPostLogin(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    count = 0

    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'

    wrong_username_manager = 'manager123'
    wrong_username_admin = 'sharedadmin123'
    wrong_username_searcher = 'searcher123'
    wrong_username_worker = 'worker123'

    wrong_password_manager = 'Insidethepyramid@23'
    wrong_password_admin = 'WY+e5nsQg-43565!3'
    wrong_password_searcher = 'Belowthepyramid@23'
    wrong_password_worker = 'Nearthepyramid@23'

    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'

    def test_post_login_by_different_valid_user(self):
        '''
        description= 'Send HTTP POST login request using different user credentials(example:Searcher,worker,admin,manager)
        at the endpoint  with valid username and password', \
        expected_output = '200'/test_id = PT_LO_POST_000,
        '''
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_post_login = searcher.login(self.username_searcher,self.password_searcher)
        self.refresh = response_post_login.json()['refresh']
        self.access = response_post_login.json()['access']
        self.assertTrue(response_post_login)
        try:
            if self.refresh is None:
                print('self.refresh has no value')
        except NameError:
            print('self.refresh is not defined')
            assert (False)
        # else:
        #     print('self.refresh ' + str(self.refresh))

        try:
            if self.access is None:
                print('self.access has no value')
        except NameError:
            print('self.access is not defined')
            assert (False)
        # else:
        #     print('self.access ' + str(self.access))
        expected_status_code = 200
        self.assertEqual(response_post_login.status_code, expected_status_code)

        worker = user.Worker(self.username_worker, self.password_worker)
        response_post_login = worker.login(self.username_worker, self.password_worker)
        try:
            if self.refresh is None:
                print('self.refresh has no value')
        except NameError:
            print('self.refresh is not defined')
            assert (False)
        # else:
        #     print('self.refresh ' + str(self.refresh))

        try:
            if self.access is None:
                print('self.access has no value')
        except NameError:
            print('self.access is not defined')
            assert (False)
        # else:
        #     print('self.access ' + str(self.access))
        expected_status_code = 200
        self.assertEqual(response_post_login.status_code, expected_status_code)

        manager = user.Manager(self.username_manager,self.password_manager)
        response_post_login = manager.login(self.username_manager,self.password_manager)
        try:
            if self.refresh is None:
                print('self.refresh has no value')
        except NameError:
            print('self.refresh is not defined')
            assert (False)
        # else:
        #     print('self.refresh ' + str(self.refresh))

        try:
            if self.access is None:
                print('self.access has no value')
        except NameError:
            print('self.access is not defined')
            assert (False)
        # else:
        #     print('self.access ' + str(self.access))
        expected_status_code = 200
        self.assertEqual(response_post_login.status_code, expected_status_code)

        admin = user.Administrator(self.username_admin,self.password_admin)
        response_post_login = admin.login(self.username_admin,self.password_admin)
        try:
            if self.refresh is None:
                print('self.refresh has no value')
        except NameError:
            print('self.refresh is not defined')
            assert (False)
        # else:
        #     print('self.refresh ' + str(self.refresh))

        try:
            if self.access is None:
                print('self.access has no value')
        except NameError:
            print('self.access is not defined')
            assert (False)
        # else:
        #     print('self.access ' + str(self.access))
        expected_status_code = 200
        self.assertEqual(response_post_login.status_code, expected_status_code)

    def test_login_by_different_verbs(self):
        '''
        description= 'Send HTTP  login request using different verbs
        at the endpoint  with valid username and password', \
        expected_output = '405' Method Not Allowed,/test_id = NT_LO_POST_000
        '''
        user.Searcher(self.username_searcher, self.password_searcher)
        response_login = userApis.login(self.username_searcher,self.password_searcher,'GET')
        expected_status_code = 405
        expected_error_message = "Method \"GET\" not allowed."
        self.assertEqual(response_login.status_code, expected_status_code)
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['detail'] == expected_error_message)

        user.Worker(self.username_worker, self.password_worker)
        response_login = userApis.login(self.username_worker, self.password_worker, 'PUT')
        expected_status_code = 405
        expected_error_message = "Method \"PUT\" not allowed."
        self.assertEqual(response_login.status_code, expected_status_code)
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['detail'] == expected_error_message)

        user.Manager(self.username_manager, self.password_manager)
        response_login = userApis.login(self.username_manager, self.password_manager, 'PATCH')
        expected_status_code = 405
        expected_error_message = "Method \"PATCH\" not allowed."
        self.assertEqual(response_login.status_code, expected_status_code)
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['detail'] == expected_error_message)

        user.Administrator(self.username_admin, self.password_admin)
        response_login = userApis.login(self.username_admin, self.password_admin, 'DELETE')
        expected_status_code = 405
        expected_error_message = "Method \"DELETE\" not allowed."
        self.assertEqual(response_login.status_code, expected_status_code)
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['detail'] == expected_error_message)

    def test_login_by_wrong_users(self):
        '''
        description= 'Send HTTP  login request using wrong users
        at the endpoint  with invalid username and password', \
        expected_output = '400' ,/test_id = NT_LO_POST_001
        '''

        response_login = userApis.login(self.wrong_username_searcher, self.wrong_password_searcher)
        expected_status_code = 400
        expected_error_message = ['No active account found with the given credentials']
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['non_field_errors'] == expected_error_message)

        response_login = userApis.login(self.wrong_username_worker, self.wrong_password_worker)
        expected_status_code = 400
        expected_error_message = ['No active account found with the given credentials']
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['non_field_errors'] == expected_error_message)

        response_login = userApis.login(self.wrong_username_manager, self.wrong_password_manager)
        expected_status_code = 400
        expected_error_message = ['No active account found with the given credentials']
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['non_field_errors'] == expected_error_message)

        response_login = userApis.login(self.wrong_username_admin, self.wrong_password_admin)
        expected_status_code = 400
        expected_error_message = ['No active account found with the given credentials']
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['non_field_errors'] == expected_error_message)

    def test_login_by_blank_credentials(self):
        '''
        description= 'Send HTTP  login request using blank user credentials
        at the endpoint', \
        expected_output = '400' ,/test_id = NT_LO_POST_002
        '''

        response_login = userApis.login("","")
        expected_status_code = 400
        expected_error_message = "This field may not be blank.,This field may not be blank."
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['username'],['password'] == expected_error_message)

        response_login = userApis.login(self.wrong_username_worker,"")
        expected_status_code = 400
        expected_error_message = ["This field may not be blank."]
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['password'] == expected_error_message)

        response_login = userApis.login("", self.wrong_password_manager)
        expected_status_code = 400
        expected_error_message = ["This field may not be blank."]
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['username'] == expected_error_message)

        response_login = userApis.login("", self.wrong_password_admin)
        expected_status_code = 400
        expected_error_message = ["This field may not be blank."]
        self.assertTrue(response_login.status_code == expected_status_code and response_login.json()['username'] == expected_error_message)


obj1 = TestPostLogin()


