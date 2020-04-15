from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()
import random
import string


class TestPostUsers(SimpleTestCase):
    dynamo = dynamoDatabase.Database()
    count = 0
    #Usernames and passwords
    username_manager = 'manager1'
    username_admin = 'sharedadmin'
    username_searcher = 'searcher1'
    username_worker = 'worker1'

    password_manager = 'Insidethepyramid@2'
    password_admin = 'WY+e5nsQg-43565!'
    password_searcher = 'Belowthepyramid@2'
    password_worker = 'Nearthepyramid@2'
    #Generating random string for creating new username and email_id
    random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
    i = 0
    stringLength = 6
    x = ''.join(random.sample(random_string, stringLength))
    user_name = x
    email = str(x) + '@idemia.com'

    def test_admin_posting_user(self):
        '''
        description= 'Send HTTP POST users request using admin login
        at the endpoint  with valid username and password', \
        expected_output = user created successfully and status_code = 201,
        test_id = PT_PU_POST_000'''
        admin = user.Administrator(self.username_admin,self.password_admin)
        response_post_user = admin.create_users(self.user_name,'Tes t41@123',self.email,'A','M')
        expected_status_code = 201
        self.assertEqual(response_post_user.status_code, expected_status_code)
        self.assertEqual(response_post_user.json()['username'],self.user_name)
        self.assertEqual(response_post_user.json()['email'],self.email)
        id = response_post_user.json()['id']
        admin.post_deactivate(id)

    def test_post_user_by_different_user(self):
            '''
            description= 'Send HTTP POST users request using searcher,manager,and worker login
            at the endpoint  with valid username and password', \
            expected_output = '403 Forbidden' and "You do not have permission to perform this action.",
            test_id = NT_PU_POST_000'''
            #creating user by searcher
            searcher = user.Searcher(self.username_searcher,self.password_searcher)
            response_post_user = searcher.create_users('test43', 'Test43@123', 'test43@idemia.com', 'A', 'M')
            expected_status_code = 403
            error = "You do not have permission to perform this action."
            self.assertEqual(response_post_user.json()['detail'],error)
            self.assertEqual(response_post_user.status_code, expected_status_code)
            #creating user by manager
            manager = user.Manager(self.username_manager, self.password_manager)
            response_post_user = manager.create_users('test43', 'Test43@123', 'test43@idemia.com', 'A', 'M')
            expected_status_code = 403
            error = "You do not have permission to perform this action."
            self.assertEqual(response_post_user.json()['detail'], error)
            self.assertEqual(response_post_user.status_code, expected_status_code)
            # creating user by worker
            worker = user.Worker(self.username_worker, self.password_worker)
            response_post_user = worker.create_users('test43', 'Test43@123', 'test43@idemia.com', 'A', 'M')
            expected_status_code = 403
            error = "You do not have permission to perform this action."
            self.assertEqual(response_post_user.json()['detail'], error)
            self.assertEqual(response_post_user.status_code, expected_status_code)

    def test_post_user_already_created(self):
        '''
               description= 'Send HTTP POST users request using admin login
               at the endpoint  with valid username and password' and existing email id, \
               expected_output = status_code = 400/User with this email already exists.
               ,test_id = NT_PU_POST_001'''

        admin = user.Administrator(self.username_admin, self.password_admin)
        response_post_user = admin.create_users(self.user_name,'Test43@123',self.email, 'A', 'M')
        error_username =  ['User with this username already exists.']
        error_email = ["User with this email already exists."]
        self.assertEqual(response_post_user.json()['username'],error_username)
        self.assertEqual(response_post_user.json()['email'],error_email)
        expected_status_code = 400
        self.assertEqual(expected_status_code,response_post_user.status_code)

    def test_post_user_with_inavlid_password(self):
        ''' description= 'Send HTTP POST users request using admin login with
            invalid password format at the endpoint  with valid username and password\
            expected_output = status_code = 400/'Password minimal complexity not met.,test_id = NT_PU_POST_002'''

         #Generating random string for creating new username and email_id
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        user_name = x
        email = str(x) + '@idemia.com'
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_post_user = admin.create_users(user_name, 'test43@123',email, 'A', 'W')
        error = ["{'password': ['Password minimal complexity not met. It must contain at least 1 upper-case character.']}"]
        expected_status_code = 400
        self.assertEqual(response_post_user.json()['password'],error)
        self.assertEqual(response_post_user.status_code,expected_status_code)


    def test_post_user_with_existing_username(self):
        '''
            description= 'Send HTTP POST users request using admin login
            with existing username at the endpoint  with valid username and password.\
                expected_output = status_code = 400/"User with this username already exists.",
                test_id = NT_PU_POST_003 '''


        #Generating random string for creating new username and email_id
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        email = str(x) + '@idemia.com'
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_post_user = admin.create_users(self.user_name, 'Test43@123', email, 'A', 'W')
        expected_error = ["User with this username already exists."]
        expected_status_code = 400
        self.assertEqual(response_post_user.json()['username'],expected_error)
        self.assertEqual(expected_status_code,response_post_user.status_code)

    def test_post_user_with_invalid_email_id(self):
        '''
                    description= ''Send HTTP POST users request using admin login
                        with invalid email_id at the endpoint  with valid username and password\
                        expected_output = status_code = 400/"Enter a valid email address..",
                                         test_id = NT_PU_POST_004     '''
        # Generating random string for creating new username and email_id
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        user_name = x
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_post_user = admin.create_users(user_name, 'Test43@123', 'qwerty', 'A', 'W')
        error = ['Enter a valid email address.']
        expected_status_code = 400
        self.assertEqual(response_post_user.json()['email'], error)
        self.assertEqual(response_post_user.status_code, expected_status_code)

    def test_post_user_with_inavlid_role_type(self):
        '''
                description= 'Send HTTP POST users request using admin login
                at the endpoint  with valid username and password' and invalid role type\
                 expected_output = status_code = 400/"Invalid role type specified.",
                 test_id = NT_PU_POST_005 '''

        #Generating random string for creating new username and email_id
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        user_name = x
        email = str(x) + '@idemia.com'
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_post_user = admin.create_users(user_name, 'test43@123', email, 'A', 'Q')
        error = ["Invalid role type specified."]
        expected_status_code = 400
        self.assertEqual(response_post_user.json()['roles'], error)
        self.assertEqual(response_post_user.status_code, expected_status_code)

    def test_post_user_with_inavlid_state_type(self):
        '''
                        description= 'Send HTTP POST users request using admin login with invalid state type
                        at the endpoint  with valid username and password'
                         expected_output = status_code = 400/"User with this username already exists.",
                            test_id = NT_PU_POST_006'''

        #Generating random string for creating new username and email_id
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        user_name = x
        email = str(x) + '@idemia.com'
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_post_user = admin.create_users(user_name, 'test43@123', email, 'T', 'Q')
        error = ["\"T\" is not a valid choice."]
        expected_status_code = 400
        self.assertEqual(response_post_user.json()['state'], error)
        self.assertEqual(response_post_user.status_code, expected_status_code)

    def test_post_user_with_two_roles(self):
        '''
                                description= 'Send HTTP POST users request using admin login
                                at the endpoint  with valid username and password' and more than one roles \
                                 expected_output = status_code = 400/".","Invalid role type specified.",
                                 test_id = NT_PU_POST_007'''

        # Generating random string for creating new username and email_id
        random_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
        stringLength = 6
        x = ''.join(random.sample(random_string, stringLength))
        user_name = x
        email = str(x) + '@idemia.com'
        admin = user.Administrator(self.username_admin, self.password_admin)
        response_post_user = admin.create_users(user_name, 'Test43@123', email, 'A', 'W,S')
        error = ["Invalid role type specified."]
        expected_status_code = 400
        self.assertEqual(response_post_user.json()['roles'], error)
        self.assertEqual(response_post_user.status_code, expected_status_code)

