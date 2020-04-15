import random
import string
from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
from test_suite.lib.apis import userApisMturk
import urllib3
urllib3.disable_warnings()

class TestDeactivateUser(SimpleTestCase):
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

    def id_generator(self,size=8, chars=string.ascii_uppercase + string.ascii_lowercase):
        return ''.join(random.choice(chars) for _ in range(size))

    def id_generator_password(self, size=15):
        result = ''
        for i in range(0, size-1):
            result += random.choice(string.ascii_uppercase)
            result += random.choice(string.ascii_lowercase)
            result += random.choice(string.digits)
            #result += random.choice(string.punctuation)
            result += '#$%^&*'

        return result

    def test_deactivate_user_by_admin_login(self):
        '''
        description= 'Send HTTP POST deactivate request using admin login
        at the endpoint  with valid_user_id', \
        expected_output = '200',test_id = PT_DU_POST_000
        '''

        admin = user.Administrator(self.username_admin,self.password_admin)
        username = self.id_generator()
        temp_email = self.id_generator()
        email = temp_email + "@gmail.com"
        password = self.id_generator_password()
        response_post_user = admin.create_users(username,password,email,'A','M')
        expected_status_code = 201
        self.assertEqual(response_post_user.status_code, expected_status_code)
        self.id = response_post_user.json()['id']
        response_deactivate_user_with_generated_id = admin.post_deactivate(self.id)
        expected_status_code = 200
        self.assertEqual(response_deactivate_user_with_generated_id.status_code, expected_status_code)

    def test_deactivate_user_by_different_user_login(self):
        '''
        description= 'Send HTTP POST deactivate request using different user login
        at the endpoint', \
        expected_output = '403 forbidden',test_id = NT_DU_POST_000
        '''

        admin = user.Administrator(self.username_admin, self.password_admin)
        username = self.id_generator()
        temp_email = self.id_generator()
        email = temp_email + "@gmail.com"

        password = self.id_generator_password()

        response_post_user = admin.create_users(username, password, email, 'A', 'M')
        expected_status_code = 201
        self.assertEqual(response_post_user.status_code, expected_status_code)
        self.id = response_post_user.json()['id']
        searcher = user.Searcher(self.username_searcher,self.password_searcher)
        response_deactivate_user_with_different_login = searcher.post_deactivate(self.id)
        expected_status_code = 403
        expected_error_message = "You do not have permission to perform this action."
        self.assertTrue(response_deactivate_user_with_different_login.status_code == expected_status_code and response_deactivate_user_with_different_login.json()['detail'] == expected_error_message)

    def test_deactivate_user_by_differnt_verbs(self):
        '''
        description= 'Send HTTP different verbs on deactivate user request using admin login
        at the endpoint with different verb', \
        expected_output = '405',test_id = NT_DU_POST_001
        '''

        admin = user.Administrator(self.username_admin,self.password_admin)
        username = self.id_generator()
        temp_email = self.id_generator()
        email = temp_email + "@gmail.com"

        password = self.id_generator_password()

        response_post_user = admin.create_users(username,password,email,'A','M')
        expected_status_code = 201
        self.assertEqual(response_post_user.status_code, expected_status_code)
        self.id = response_post_user.json()['id']

        response_deactivate_user_with_generated_id = admin.post_deactivate(self.id,'GET')
        expected_status_code = 405
        expected_error_message = "Method \"GET\" not allowed."
        self.assertTrue(response_deactivate_user_with_generated_id.status_code == expected_status_code and response_deactivate_user_with_generated_id.json()['detail'] == expected_error_message)

    def test_deactivate_user_by_invalid_id(self):
        '''
        description= 'Send HTTP POST deactivate request using admin login
        at the endpoint  with invalid_user_id', \
        expected_output = '204',test_id = NT_DU_POST_002
        '''

        admin = user.Administrator(self.username_admin, self.password_admin)
        username = self.id_generator()
        temp_email = self.id_generator()
        email = temp_email + "@gmail.com"
        password = self.id_generator_password()
        response_post_user = admin.create_users(username, password, email, 'A', 'M')
        expected_status_code = 201
        self.assertEqual(response_post_user.status_code, expected_status_code)
        self.id = response_post_user.json()['id']
        response_deactivate_user_with_generated_id = admin.post_deactivate(self.id + 1)
        expected_error_message = "No such user exist"
        expected_status_code = 404
        self.assertTrue(response_deactivate_user_with_generated_id.status_code == expected_status_code and response_deactivate_user_with_generated_id.json()['error'] == expected_error_message)

    def test_deactivate_user_by_null_id(self):
        '''
        description= 'Send HTTP POST deactivate request using admin login
        at the endpoint with null user_id', \
        expected_output = '400',test_id = NT_DU_POST_003
        '''

        admin = user.Administrator(self.username_admin, self.password_admin)
        username = self.id_generator()
        temp_email = self.id_generator()
        email = temp_email + "@gmail.com"

        password = self.id_generator_password()

        response_post_user = admin.create_users(username, password, email, 'A', 'M')
        expected_status_code = 201
        self.assertEqual(response_post_user.status_code, expected_status_code)
        self.id = None
        response_deactivate_user_with_generated_id = admin.post_deactivate(self.id)
        expected_status_code = 400
        self.assertEqual(response_deactivate_user_with_generated_id.status_code, expected_status_code)

    def test_deactivate_user_by_alphabets_in_id(self):
        '''
        description= 'Send HTTP POST deactivate request using admin login
        at the endpoint  with alphabets in user_id', \
        expected_output = '400',test_id = NT_DU_POST_004
        '''

        admin = user.Administrator(self.username_admin, self.password_admin)
        username = self.id_generator()
        temp_email = self.id_generator()
        email = temp_email + "@gmail.com"

        password = self.id_generator_password()

        response_post_user = admin.create_users(username, password, email, 'A', 'M')
        expected_status_code = 201
        self.assertEqual(response_post_user.status_code, expected_status_code)
        self.id = 'abc'
        response_deactivate_user_with_generated_id = admin.post_deactivate(self.id)
        expected_status_code = 400
        self.assertEqual(response_deactivate_user_with_generated_id.status_code, expected_status_code)

    def test_deactivate_user_by_special_character_in_id(self):
        '''
        description= 'Send HTTP POST deactivate request using admin login
        at the endpoint  with specia; character in user_id', \
        expected_output = '400',test_id = NT_DU_POST_005
        '''

        admin = user.Administrator(self.username_admin, self.password_admin)
        username = self.id_generator()
        temp_email = self.id_generator()
        email = temp_email + "@gmail.com"
        password = self.id_generator_password()

        response_post_user = admin.create_users(username, password, email, 'A', 'M')
        expected_status_code = 201
        self.assertEqual(response_post_user.status_code, expected_status_code)
        self.id = '%@#*&**()'
        response_deactivate_user_with_generated_id = admin.post_deactivate(self.id)
        expected_status_code = 400
        self.assertEqual(response_deactivate_user_with_generated_id.status_code, expected_status_code)

    def test_deactivate_user_on_already_deactivated_user(self):
            '''
            description= 'Send HTTP POST deactivate request using admin login
            at the endpoint  on already deactivated user', \
            expected_output = '409',NT_DU_POST_006
            '''

            admin = user.Administrator(self.username_admin, self.password_admin)
            username = self.id_generator()
            temp_email = self.id_generator()
            email = temp_email + "@gmail.com"
            password = self.id_generator_password()
            response_post_user = admin.create_users(username, password, email, 'A', 'M')
            self.id = response_post_user.json()['id']
            admin.post_deactivate(self.id)
            response_deactivate_user_again = admin.post_deactivate(self.id)
            expected_error_message = "Can't deactivate a user in state other than 'Activated'"
            expected_status_code = 400
            self.assertTrue(response_deactivate_user_again.status_code == expected_status_code and response_deactivate_user_again.json()['error'] == expected_error_message)


obj1 = TestDeactivateUser()

