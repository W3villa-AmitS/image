import sys
import os

sys.path.append(os.path.abspath(''))
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from test_suite.config import config



def mturk_post_job(job_name, job_type, job_attributes, job_description, job_max_occurrence, job_assignment_duration, job_lifetime_duration,job_reward_per_hit, job_qats_per_hit, job_tasks_per_hit,job_boxing_type,access_token,type='POST'):
    import requests

    url = config.URLMTURK +"jobs/"


    payload = "{\n    \"job_name\": \""+ job_name +"\",\n    \"job_type\": \""+ job_type +"\",\n    \"job_attributes\":\""+ job_attributes +"\",\n    \"job_description\": \""+ job_description +"\",\n    \"job_max_occurrence\":\""+ job_max_occurrence +"\",\n    \"job_assignment_duration\": \""+ job_assignment_duration +"\",\n    \"job_lifetime_duration\":\""+ job_lifetime_duration +"\",\n    \"job_reward_per_hit\":\""+ job_reward_per_hit +"\",\n    \"job_qats_per_hit\":\""+ job_qats_per_hit +"\",\n    \"job_tasks_per_hit\": \""+ job_tasks_per_hit +"\",\"job_boxing_type\":\"" + job_boxing_type + "\"" + "\n}"

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "35dada7a-6c81-4fe8-8641-213c89216763",
        'Authorization': 'Bearer {}'.format(access_token)
    }
    return requests.request(type, url, data=payload, headers=headers, verify=False)

#For testiing pupose only "post mturk job with integer type attribute in payload"
def mturk_post_job_testing(job_name, job_type, job_attributes, job_description, job_max_occurrence, job_assignment_duration, job_lifetime_duration,job_reward_per_hit, job_qats_per_hit, job_tasks_per_hit,job_boxing_type,access_token,type='POST'):
    import requests

    url = config.URLMTURK +"jobs/"


    payload = "{\n    \"job_name\": \""+ job_name +"\",\n    \"job_type\": \""+ job_type +"\",\n    \"job_attributes\":\""+ str(job_attributes) +"\",\n    \"job_description\": \""+ job_description +"\",\n    \"job_max_occurrence\":\""+ job_max_occurrence +"\",\n    \"job_assignment_duration\": \""+ job_assignment_duration +"\",\n    \"job_lifetime_duration\":\""+ job_lifetime_duration +"\",\n    \"job_reward_per_hit\":\""+ job_reward_per_hit +"\",\n    \"job_qats_per_hit\":\""+ job_qats_per_hit +"\",\n    \"job_tasks_per_hit\": \""+ job_tasks_per_hit +"\",\"job_boxing_type\":\"" + job_boxing_type + "\"" + "\n}"

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "35dada7a-6c81-4fe8-8641-213c89216763",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url, data=payload, headers=headers, verify=False)


def mturk_get_jobs(access_token, type='GET'):
    import requests

    url = config.URLMTURK + "jobs/"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url, headers=headers, verify=False)


def mturk_get_job_with_id(job_id,access_token, type='GET'):
    import requests

    url = config.URLMTURK + "jobs/" + str(job_id)+"/"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url,  headers=headers, verify=False)


def mturk_add_wots(job_id, access_token):
    import requests

    url = config.URLMTURK + "jobs/" + str(job_id) + "/add_wots/"

    files = {'csv_file': ('xyz.csv',
                          'image_url\nhttps://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=350')}

    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "8d98351b-4777-406e-b3f6-f8cb7bedee55",
        'Authorization': 'Bearer {}'.format(access_token),
        'Access-Control-Request-Headers': 'X-Custom-Header'
    }

    return requests.post(url, headers=headers, files=files, verify=False)


def mturk_add_wots_new(job_id, access_token,file):
    import requests

    url = config.URLMTURK +"jobs/" + str(job_id) + "/add_wots/"

    # files = {'csv_file': ('xyz.csv',
    #                       'image_url\nhttps://images.pexels.com/photos/248768/pexels-photo-248768.jpeg?auto=compress&cs=tinysrgb&h=350')}

    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "8d98351b-4777-406e-b3f6-f8cb7bedee55",
        'Authorization': 'Bearer {}'.format(access_token),
        'Access-Control-Request-Headers': 'X-Custom-Header'
    }


    return requests.post(url,files = file, headers=headers,  verify = False)

#For testing of add wots without wots
def test_mturk_add_wots(job_id, access_token,file):
    import requests

    url = config.URLMTURK +"jobs/" + str(job_id) + "/add_wots/"

    '''no wots'''
    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "8d98351b-4777-406e-b3f6-f8cb7bedee55",
        'Authorization': 'Bearer {}'.format(access_token),
        'Access-Control-Request-Headers': 'X-Custom-Header'
    }

    return requests.post(url,files= file, headers=headers,verify = False)

#For testing of add wots through different request type.(GET)

def mturk_add_wots_get_method(job_id, access_token,file):
    import requests

    url = config.URLMTURK +"jobs/" + str(job_id) + "/add_wots/"

    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "8d98351b-4777-406e-b3f6-f8cb7bedee55",
        'Authorization': 'Bearer {}'.format(access_token),
        'Access-Control-Request-Headers': 'X-Custom-Header'
    }

    return requests.get(url,files= file, headers=headers,verify = False)
	
def mturk_approve_job(job_id, access_token):
    import requests

    url = config.URLMTURK +"jobs/"+str(job_id)+"/approve/"
    payload = ""
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }

    return requests.request("POST", url, data=payload, headers=headers, verify=False)

def mturk_disapprove_job(job_id, access_token):
    import requests

    url = config.URLMTURK +"jobs/"+str(job_id)+"/disapprove/"

    payload = ""
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }

    return requests.request("POST", url, data=payload, headers=headers, verify=False)


def mturk_add_qat(job_id, image_url, result, access_token, type='POST'):
    import requests

    url = config.URLMTURK + "jobs/" + str(job_id) + "/add_qat/"

    # change result json to string
    result = str(result).replace("'", '"')

    payload = "{\n\t\"image_url\": \"" + image_url + "\",\n\t\"result\": " + result + "\n\t\n}"
    headers = {
        'Content-Type': "application/json",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "ccb18fd4-c57d-4896-8d13-8d2ef816878f"
    }
    return requests.request(type, url, data=payload, headers=headers, verify=False)

def mturk_add_qats(job_id, result, access_token, type='POST'):
    import requests

    url = config.URLMTURK + "jobs/" + str(job_id) + "/add_qats/"

    headers = {
            'Content-Type': "application/json",
            'Authorization': 'Bearer {}'.format(access_token),
            'Cache-Control': "no-cache",
            'Postman-Token': "ccb18fd4-c57d-4896-8d13-8d2ef816878f"
        }

    return requests.request(type, url, json=result, headers=headers, verify=False)

#for testing of add qat with different request type(GET)
def test_mturk_add_qats(job_id, result, access_token, type='GET'):
    import requests

    url = config.URL + "jobs/" + str(job_id) + "/add_qats/"

    headers = {
            'Content-Type': "application/json",
            'Authorization': 'Bearer {}'.format(access_token),
            'Cache-Control': "no-cache",
            'Postman-Token': "ccb18fd4-c57d-4896-8d13-8d2ef816878f"
        }

    return requests.request(type, url, json=result, headers=headers, verify=False)


def mturk_get_token(hit_id, assignment_id,worker_id):
    import requests

    url = config.URLMTURK +"get_token"

    payload = "{\n    \"hit_id\": \n        \"" + hit_id[0] + "\"\n    ,\n    \"assignment_id\": \n        \"" + str(assignment_id) + "\"\n    ,\n    \"worker_id\": \n        \"" + str(worker_id) + "\"\n    \n}"
    headers = {
        'content-type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }

    return requests.request("POST", url,data=payload, headers=headers, verify=False)

#For testing of API without Hit_id
def mturk_get_token_testing_without_hit_id(assignment_id,worker_id):
    import requests

    url = config.URLMTURK +"get_token"

    payload = "{\n    \"assignment_id\": \n        \"" + str(assignment_id) + "\"\n    ,\n    \"worker_id\": \n        \"" + str(worker_id) + "\"\n    \n}"
    headers = {
        'content-type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }

    return requests.request("POST", url,data=payload, headers=headers, verify=False)


#This function is used for testing by manipulation url
def mturk_get_token_testing(hit_id, assignment_id,worker_id):
    import requests
    #url manipulated
    url = config.URLMTURK +"get_tokens"

    payload = "{\n    \"hit_id\": \n        \"" + str(hit_id) + "\"\n    ,\n    \"assignment_id\": \n        \"" + assignment_id + "\"\n    ,\n    \"worker_id\": \n        \"" +worker_id + "\"\n    \n}"
    headers = {
        'content-type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }

    return requests.request("POST", url,data=payload, headers=headers, verify=False)

def mturk_get_task(token):
    import requests

    url = config.URLMTURK +"task"

    payload = ""

    headers = {
        'content-type': "application/json",
        'Authorization': 'Bearer {}'.format(token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }
    return requests.request("GET", url, data=payload, headers=headers,verify =False)

#for testing of api on wrong URL
def mturk_get_task_testing(token):
    import requests

    url = config.URLMTURK +"tsk"

    payload = ""

    headers = {
        'content-type': "application/json",
        'Authorization': 'Bearer {}'.format(token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }
    return requests.request("GET", url, data=payload, headers=headers,verify =False)


def mturk_post_task_result(task_id, result, token,type = 'POST'):
    import requests

    url = config.URLMTURK + "tasks/" + str(task_id) + "/post_result/"


    payload = '{"result":' + str(result) + "}"


    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(token)
    }

    return requests.request(type, url, data = payload, headers=headers,verify = False)

#for testing of POST_RESULT API without  token
def mturk_post_task_result_test(task_id, result):
    import requests

    url = config.URLMTURK + "tasks/" + str(task_id) + "/post_result/"

    payload = '{"result":' + str(result) + "}"

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
    }

    return requests.request('POST',url, data = payload, headers=headers,verify = False)

#for testing of POST_RESULT API without task_id

def mturk_post_task_result_test_new(result, token):
    import requests

    url = config.URLMTURK +  "tasks/" + "/post_result/"

    payload = '{"result":' + str(result) + "}"

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(token)
    }

    return requests.request('POST', url, data = payload, headers=headers,verify = False)


def mturk_get_job_status_list(status, access_token):
    import requests

    url = config.URLMTURK + "jobs/?status=" + str(status)
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"

    }

    return requests.request("GET", url, headers=headers, verify=False)

def mturk_download_qats(job_id,access_token,type = 'GET'):
    import requests

    url = config.URLMTURK + "qats?job_id=" + job_id

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'cache-control': "no-cache",
        'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url,headers=headers, verify=False)


def mturk_download_result_by_job_id(job_id,access_token,type = 'GET'):

    import requests

    url = config.URLMTURK + "results?job_id=" + job_id

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'cache-control': "no-cache",
        'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url,headers=headers, verify=False)

#for testing of API without user login
def mturk_download_result_by_job_id_testing(job_id,type = 'GET'):

    import requests

    url = config.URLMTURK + "results?job_id=" + job_id

    headers = {
        'cache-control': "no-cache",
        'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url,headers=headers, verify=False)


def mturk_download_result_by_job_id_and_worker_id(job_id,worker_id,access_token,type = 'GET'):

    import requests

    url = config.URLMTURK + "results?job_id=" + job_id  + "&worker_id=" + worker_id

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'cache-control': "no-cache",
        'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url,headers=headers, verify=False)


    #for testing of api without user login
def mturk_download_result_by_job_id_and_worker_id_testing(job_id,worker_id,type = 'GET'):

    import requests

    url = config.URLMTURK + "results?job_id=" + job_id  + "&worker_id=" + worker_id
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"

    }

    return requests.request(type, url,headers=headers, verify=False)

def mturk_consolidate_result_of_job_id(job_id,access_token,type = 'GET'):

    import requests

    url = config.URLMTURK + "jobs/" + job_id  + "/consolidate/"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"

    }

    return requests.request(type, url,headers=headers, verify=False)

def mturk_consolidate_result_of_task_id(task_id,access_token,type = 'GET'):

    import requests

    url = config.URLMTURK + "tasks/" + task_id  + "/consolidate/"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"

    }

    return requests.request(type, url,headers=headers, verify=False)