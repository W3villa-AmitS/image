from django.test import SimpleTestCase
from test_suite.lib.database import dynamoDatabase
from test_suite.lib.users import user
import json
from test_suite.lib.apis import userApis
import urllib3
urllib3.disable_warnings()



class testInitialQatAndFrequency(SimpleTestCase):
        fixtures = ('test_suite/fixtures/users.json',)
        dynamo = dynamoDatabase.Database()
        username_manager = 'manager1'
        username_admin = 'sharedadmin'
        username_searcher = 'searcher1'
        username_worker = 'worker1'

        password_manager = 'Insidethepyramid@2'
        password_admin = 'WY+e5nsQg-43565!'
        password_searcher = 'Belowthepyramid@2'
        password_worker = 'Nearthepyramid@2'
        job_initial_qats = '3'
        task_max_occurance= '5'
        qat_to_be_added=0
        frequency_test_result="true"
        gender = '"M","F"'
        qat_frequency='2'
        qat_frequency_ok='false'
        result = {"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        searcher_result={"cars": [{"x1": "1", "y1": "1", "x2": "3", "y2": "4"}, {"x1": "4", "y1": "6", "x2": "8", "y2": "12"}],
                  "bikes": [{"x1": "5", "y1": "2", "x2": "6", "y2": "3"},
                            {"x1": "7", "y1": "9", "x2": "8", "y2": "10"}]}
        result=json.dumps(result)
        qat_urls = ["https://images.pexels.com/photos/248794/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=350",
                    "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=351",
                    "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=352",
                    "https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=353","https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=388"
                    ]
        wots='image_url\nhttps://images.pexels.com/photos/248785/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=050\nhttps://images.pexels.com/photos/248781/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=250\nhttps://images.pexels.com/photos/248785/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=850\nhttps://images.pexels.com/photos/248785/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=34\nhttps://images.pexels.com/photos/248785/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=357\n'

        searcher = user.Searcher(username_searcher,password_searcher)
        # add job
        response = searcher.add_job(job_name='test2 job', job_type='P', job_attributes='cars,bikes', job_description='test2 job',
                         job_instructions='test2 job', task_max_occurrence='5', job_criteria_age_min='18',
                         job_criteria_age_max='60', job_criteria_location='India', job_initial_qats='3',
                         job_qat_frequency='5', job_criteria_gender= gender, job_criteria_grade='D',job_boxing_type='Rectangle')

        job_id =response.json()['job_id']
        #add wots
        response_wot=searcher.add_wots(job_id)
        qat_to_be_added=response_wot.json()['job_number_of_total_qats_required']
        searcher = user.Searcher(username_searcher,password_searcher)
        # add number of qats as per the initial qat requirement
        for i in qat_urls[0:(int(qat_to_be_added))]:
            response_add_qat = searcher.add_qat(job_id, i,result)
        # approve job by manager
        manager = user.Manager(username_manager,password_manager)
        resp = manager.approve_job(job_id)
        print(resp.json())

        # # The following code is commented as it is not required in the current test case but may
        # # server as example in other test cases. -saurabhrautela
        # manager approves job
        #manager = user.Manager('manager', 'password@123')
        #manager.approve_job(self.job_id)
        def test_initial_qats(self):

            worker = user.Worker(self.username_worker,self.password_worker)
            counter=0
            #fetch tasks as worker
            for index in range(int(self.job_initial_qats)):
                    response=worker.get_task(self.job_id)
                    if response.status_code == 400 and response.json()['error'] == "Worker already active on another job.":
                            worker.post_disengage_job(response.json()['job_id'])
                            responsev=worker.get_task(self.job_id)
                            incoming_task=responsev.json()['image_url']
                    else:        
                            incoming_task=response.json()['image_url']

            #check whether the number of qat tasks are same as mentioned in intitial qats
                    for qat_url in self.qat_urls:
                        if incoming_task==qat_url:
                            counter+=1
                            break

            #here index is the index of job initial_qats which starts from 0 so increment the number to get actual number of initial qats.
            self.assertEqual(counter,index+1)

        #This test checks whether the qats are appearing as per frequency mentioned by the searcher earlier.
        def test_qat_frequency(self):
            searcher = user.Searcher(self.username_searcher,self.password_searcher)
            response_getjob=searcher.get_job(self.job_id)

            #get total number of tasks
            total_no_of_tasks=int(response_getjob.json()['job_number_of_wots_added'])+int(response_getjob.json()['job_number_of_qats_added'])
            worker = user.Worker(self.username_worker,self.password_worker)
            task_type=[]

            #get tasks and post result in the database
            for i in range(total_no_of_tasks-int(self.job_initial_qats)):
                    response_getTask = worker.get_task(self.job_id)
                    task_id=response_getTask.json()['task_id']
                    resk=worker.post_task_result(int(task_id),self.result)

                    task_type.append(resk.json()['task'])

           #check the task type for each task appearing and match the frequency of qat
            for j in range(int(self.qat_frequency),len(task_type),int(self.qat_frequency)+1):
                if(task_type[j]=='qat'):
                    self.qat_frequency_ok='true'

                else:
                    self.qat_frequency_ok = 'false'


            if self.qat_frequency_ok== self.frequency_test_result:
             self.assertEqual(self.frequency_test_result,self.qat_frequency_ok)
