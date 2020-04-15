from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()


class TestGetUsersList(SimpleTestCase):
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



# test whether GET users api returns a list of user in case of admin and manager login
    def test_get_users_by_valid_users(self):
        '''
                description= 'Send HTTP Get user request using  valid login
                at the endpoint  with valid username and password', \
                expected_output = '200',test_id = PT_US_GET_000
                '''
        manager = user.Manager(self.username_manager,self.password_manager)
        response_get_users = manager.get_users()

        for json_dict in response_get_users.json():
                try:
                    if 'username' in json_dict.keys() is None:
                        print('username has no value')
                except NameError:
                    print('username is not defined')
                    assert (False)
                # else:
                #     print(json_dict['username'])

                try:
                    if 'id' in json_dict.keys() is None:
                        print('id has no value')
                except NameError:
                    print('id is not defined')
                    assert (False)
                # else:
                #     print(json_dict['id'])

                try:
                    if 'email' in json_dict.keys() is None:
                        print('email has no value')
                except NameError:
                    print('email is not defined')
                    assert (False)
                # else:
                #     print(json_dict['email'])
                try:
                    if 'state' in json_dict.keys() is None:
                        print('state has no value')
                except NameError:
                    print('state is not defined')
                    assert (False)
                # else:
                #     print(json_dict['state'])

                try:
                    if 'roles' in json_dict.keys() is None:
                        print('roles has no value')
                except NameError:
                    print('roles is not defined')
                    assert (False)
                # else:
                #     print(json_dict['roles'])

        admin = user.Administrator(self.username_admin, self.password_admin)
        response_get_users_admin = admin.get_users()

        for json_dict in response_get_users_admin.json():
                try:
                    if 'username' in json_dict.keys() is None:
                        print('username has no value')
                except NameError:
                    print('username is not defined')
                    assert (False)
                # else:
                #     print(json_dict['username'])

                try:
                    if 'id' in json_dict.keys() is None:
                        print('id has no value')
                except NameError:
                    print('id is not defined')
                    assert (False)
                # else:
                #     print(json_dict['id'])

                try:
                    if 'email' in json_dict.keys() is None:
                        print('email has no value')
                except NameError:
                    print('email is not defined')
                    assert (False)
                # else:
                #     print(json_dict['email'])
                try:
                    if 'state' in json_dict.keys() is None:
                        print('state has no value')
                except NameError:
                    print('state is not defined')
                    assert (False)
                # else:
                #     print(json_dict['state'])

                try:
                    if 'roles' in json_dict.keys() is None:
                        print('roles has no value')
                except NameError:
                    print('roles is not defined')
                    assert (False)
                # else:
                #     print(json_dict['roles'])


        expected_status_code = 200
        self.assertEqual(response_get_users.status_code, expected_status_code)
        self.assertEqual(response_get_users_admin.status_code, expected_status_code)


# test whether GET users api returns a permission denied status (Forbidden) in case of searcher and worker login
    def test_get_users_by_invalid_users(self):
        '''
                        description= 'Send HTTP Get user request using  invalid user login', \
                        expected_output = '403',test_id = NT_US_GET_000
                        '''
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_get_users = searcher.get_users()
        expected_status_code = 403
        expected_error_message = "You do not have permission to perform this action."
        self.assertTrue(response_get_users.status_code == expected_status_code and response_get_users.json()['detail'] == expected_error_message)

        worker = user.Worker(self.username_worker,self.password_worker)
        response_get_users = worker.get_users()
        expected_status_code = 403
        expected_error_message = "You do not have permission to perform this action."
        self.assertTrue(response_get_users.status_code == expected_status_code and response_get_users.json()['detail'] == expected_error_message)

    def test_get_users_by_invalid_access_token(self):
        manager = user.Manager(self.username_manager, self.password_manager)
        response_get_users = manager.get_users_invalid_access_token()
        print(response_get_users.json())
        print(response_get_users.status_code)

obj1 = TestGetUsersList()

