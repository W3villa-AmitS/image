from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()

class TestAddQat(SimpleTestCase):
    fixtures = ('test_suite/fixtures/users.json',)
    dynamo = dynamoDatabase.Database()
    SEARCHER_USERNAME_1 = 'searcher1'
    SEARCHER_PASSWORD_1 = 'Belowthepyramid@2'
    WORKER_USERNAME_1 = 'worker1'
    WORKER_PASSWORD_1 = 'Nearthepyramid@2'
    MANAGER_USERNAME_1 = 'manager1'
    MANAGER_PASSWORD_1 = 'Insidethepyramid@2'
    ADMIN_USERNAME_1 = 'sharedadmin'
    ADMIN_PASSWORD_1 = 'WY+e5nsQg-43565!'
    gender = '"M","F"'
    result = {"qats": [{"image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg",
               "result": {"cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
                          "bikes": [{"x1": "95",
                                     "y1": "267",
                                     "x2": "197",
                                     "y2": "340"
                                     }
                                    ]
                          }
               },
              {
                  "image_url": "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg",
                  "result": {
                      "cars": [
                          {
                              "x1": "95",
                              "y1": "267",
                              "x2": "197",
                              "y2": "340"
                          }
                      ],
                      "bikes": [
                          {
                              "x1": "95",
                              "y1": "267",
                              "x2": "197",
                              "y2": "340"
                          }
                      ]
                  }
              }
              ]
     }

        # add job
    searcher = user.Searcher(SEARCHER_USERNAME_1, SEARCHER_PASSWORD_1)
    response = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes', job_description='test2 job',
                         job_instructions='test2 job', task_max_occurrence='5', job_criteria_age_min='18',
                         job_criteria_age_max='60', job_criteria_location='India', job_initial_qats='2',
                         job_qat_frequency='5', job_criteria_gender= gender, job_criteria_grade='D',job_boxing_type='Rectangle')

    job_id = response.json()['job_id']
    searcher.add_wots(job_id)
        # # The following code is commented as it is not required in the current test case but may
        # # server as example in other test cases. -saurabhrautela
        # manager approves job
        #manager = user.Manager('manager', 'password123')
        #manager.approve_job(self.job_id)

    def test_post_valid_url_result(self):
        '''
        description= 'Send HTTP POST request at the endpoint with valid image url and result.', \
        id ='PT_AQ_POST_000', \
        expected_output = 'QAT updated response with incremented "No of QATs added property".
        HTTP 202 Added',
        '''

        expected_status_code = 202
        # Login as searcher
        searcher = user.Searcher(self.SEARCHER_USERNAME_1, self.SEARCHER_PASSWORD_1)
        # Send POST request with required data
        response = searcher.add_qats(self.job_id,self.result)
        self.assertEqual(response.status_code, expected_status_code)
    #     # TODO logout

    # """    
    # # Commented as it can be tested during load testing
    # def test_multiple_post_valid_url_result(self):
    #     '''
    #     description= 'Send multiple HTTP POST request at the endpoint with different valid 
    #     image url and result.', \
    #     id ='PT_AQ_002', \
    #     expected_output = 'QAT updated response with incremented "No of QATs added" property after every request.
    #     HTTP 202 Added',
    #     '''

    #     image_url = []
    #     result = [{}]
    #     expected_response = [{}]
        
    #     # Login as searcher
    #     searcher = user.Searcher()

    #     for count in range(len(image_url)):
    #         # Send POST request with required data
    #         response = searcher.post_qat(self.job_id, image_url[count], result[count])
    #         self.assertEqual(response, expected_response[count])

    #     # TODO logout 
    # """

    def test_post_job_id_not_present(self):
        '''
        description= 'Send HTTP POST request at the endpoint with valid image url and result. The job id in the result should not be present.', \
        id ='NT_AQ__POST_000', \
        expected_output = '404 Not found',
        '''

        expected_status_code = 404
        # Login as searcher
        searcher = user.Searcher(self.SEARCHER_USERNAME_1, self.SEARCHER_PASSWORD_1)
        # Send POST request with required data
        response = searcher.add_qats(self.job_id + 'ass', self.result)
        self.assertEqual(response.status_code, expected_status_code)

        # TODO logout 

    # def test_post_invalid_image_url(self):
    #     '''
    #     description= 'Send HTTP POST request at the endpoint with invalid image url and valid result.', \
    #     id ='NT_AQ_002', \
    #     expected_output = '400 Bad request',
    #     '''
    #
    #     result_new = {"qats": [{"image_url": "",
    #                         "result": {"cars": [{"x1": "95", "y1": "267", "x2": "197", "y2": "340"}],
    #                                    "bikes": [{"x1": "95",
    #                                               "y1": "267",
    #                                               "x2": "197",
    #                                               "y2": "340"
    #                                               }
    #                                              ]
    #                                    }
    #                         },
    #                        {
    #                            "image_url": "",
    #                            "result": {
    #                                "cars": [
    #                                    {
    #                                        "x1": "95",
    #                                        "y1": "267",
    #                                        "x2": "197",
    #                                        "y2": "340"
    #                                    }
    #                                ],
    #                                "bikes": [
    #                                    {
    #                                        "x1": "95",
    #                                        "y1": "267",
    #                                        "x2": "197",
    #                                        "y2": "340"
    #                                    }
    #                                ]
    #                            }
    #                        }
    #                        ]
    #               }
    #
    #     expected_status_code = 400
    #     # Login as searcher
    #     searcher = user.Searcher(self.SEARCHER_USERNAME_1, self.SEARCHER_PASSWORD_1)
    #     # Send POST request with required data
    #     response = searcher.add_qats(self.job_id ,result_new)
    #     print(response.json())
    #     self.assertEqual(response.status_code, expected_status_code)

        # TODO logout 

    def test_post_invalid_result(self):
        '''
        description= 'Send HTTP POST request at the endpoint with invalid image url and valid result.', \
        id ='NT_AQ_001', \
        expected_output = '400 Bad request',
        '''

        # image_url = 'https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=350'
        invalid_result = '{not a valid json}'

        expected_status_code = 400
        # Login as searcher
        searcher = user.Searcher(self.SEARCHER_USERNAME_1, self.SEARCHER_PASSWORD_1)
        # Send POST request with required data
        response = searcher.add_qats(self.job_id , invalid_result)
        self.assertEqual(response.status_code, expected_status_code)

        # TODO logout 

    def test_post_unauthorized_user(self):
        '''
        description= 'Send HTTP POST  request with valid image url and result when logged in as user other searcher.', \
        id ='NT_AQ_POST_002', \
        expected_output = '403 Forbidden',
        '''

        # image_url = 'https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=350'
        # result = {"cars":[{"x1":"1","y1":"1","x2":"3","y2":"4"},{"x1":"4","y1":"6","x2":"8","y2":"12"}],"bikes" : [{"x1":"5","y1":"2","x2":"6","y2":"3"},{"x1":"7","y1":"9","x2":"8","y2":"10"}]}
        expected_status_code = 403

        #Login as worker
        worker = user.Worker(self.WORKER_USERNAME_1, self.WORKER_PASSWORD_1)
        # Send POST request with required data
        response = userApis.add_qats(self.job_id, self.result,worker.access_token)
        self.assertEqual(response.status_code, expected_status_code)
        # TODO logout

        #Login as admin
        admin = user.Administrator(self.ADMIN_USERNAME_1, self.ADMIN_PASSWORD_1)
        # Send POST request with required data
        response = userApis.add_qats(self.job_id,self.result, admin.access_token)
        self.assertEqual(response.status_code, expected_status_code)
        # TODO logout

        #Login as worker
        manager = user.Manager(self.MANAGER_USERNAME_1, self.MANAGER_PASSWORD_1)
        # Send POST request with required data
        response = userApis.add_qats(self.job_id,self.result, manager.access_token)
        self.assertEqual(response.status_code, expected_status_code)
        # TODO logout

    def test_add_qat_with_other_verbs(self):
        '''
        description= 'Send HTTP request at endpoint with a verb not allowed by API.', \
        id ='NT_AQ_POST_003', \
        expected_output = 'HTTP 405 Method Not Allowed',
        '''

        # image_url = 'https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=350'
        # result = {"cars":[{"x1":"1","y1":"1","x2":"3","y2":"4"},{"x1":"4","y1":"6","x2":"8","y2":"12"}],"bikes" : [{"x1":"5","y1":"2","x2":"6","y2":"3"},{"x1":"7","y1":"9","x2":"8","y2":"10"}]}
        expected_status_code = 405
        # Login as searcher
        searcher = user.Searcher(self.SEARCHER_USERNAME_1, self.SEARCHER_PASSWORD_1)
        # Send POST request with required data
        response = userApis.add_qats(self.job_id,self.result, searcher.access_token, 'GET')
        self.assertEqual(response.status_code, expected_status_code)
        # TODO logout 