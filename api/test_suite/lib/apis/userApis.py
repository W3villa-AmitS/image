import sys
import os 
sys.path.append(os.path.abspath(''))
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from test_suite.config import config
import json


def login(username, password, type='POST'):
    import requests
    url = config.URL + 'login/'
    
    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"username\"\r\n\r\n"+str(username)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;  name=\"password\"\r\n\r\n"+str(password)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Cache-Control': "no-cache",
        'Postman-Token': "2f39737c-791f-4a56-89cf-3f40725378fc"
    }
    res = requests.request(type, url, data=payload, headers=headers, verify=False)	
    return res
    
def post_job(job_name, job_type, job_attributes, job_description, job_instructions, task_max_occurrence, job_criteria_age_min, job_criteria_age_max, job_criteria_location, job_initial_qats, job_qat_frequency, job_criteria_gender, job_criteria_grade,job_boxing_type, access_token, type='POST'):
    import requests
    
    url = config.URL +"jobs/"

    payload = "{\n    \"job_name\": \"" + job_name + "\",\n    \"job_type\": \"" + job_type + "\",\n    \"job_attributes\":\"" + job_attributes + "\",\n    \"job_description\": \"" + job_description + "\",\n    \"job_instructions\":\"" + job_instructions + "\",\n    \"job_max_occurrence\": \"" + task_max_occurrence + "\",\n    \"job_criteria_age_min\":\"" + job_criteria_age_min + "\",\n    \"job_criteria_age_max\":\"" + job_criteria_age_max + "\",\n    \"job_criteria_location\":\"" + job_criteria_location + "\",\n    \"job_initial_qats\": \"" + job_initial_qats + "\" ,\n    \"job_qat_frequency\":\"" + job_qat_frequency + "\",\n    \"job_criteria_gender\":""["+ job_criteria_gender +"]"" ,\n    \"job_criteria_grade\": \"" + job_criteria_grade + "\",\"job_boxing_type\":\"" + job_boxing_type + "\"" + "\n}"


    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url, data=payload, headers=headers, verify=False)

def get_jobs(access_token, type='GET'):
    import requests

    url = config.URL + "jobs/"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url,  headers=headers, verify=False)


def add_wots(job_id, access_token):
    import requests

    url = config.URL +"jobs/" + str(job_id) + "/add_wots/"

    files = {'csv_file': ('xyz.csv','image_url\nhttps://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&h=350')}

    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "8d98351b-4777-406e-b3f6-f8cb7bedee55",
        'Authorization': 'Bearer {}'.format(access_token),
        'Access-Control-Request-Headers': 'X-Custom-Header'
    }

    return requests.post(url, headers=headers, files = files, verify=False)

def add_wots_without_csv(job_id, access_token,file):
    import requests

    url = config.URL +"jobs/" + str(job_id) + "/add_wots/"
    headers = {
        'Cache-Control': "no-cache",
        'Postman-Token': "8d98351b-4777-406e-b3f6-f8cb7bedee55",
        'Authorization': 'Bearer {}'.format(access_token),
        'Access-Control-Request-Headers': 'X-Custom-Header'
    }

    return requests.post(url, files = file, headers=headers,  verify = False)


def approve_job(job_id, access_token):
    import requests

    url = config.URL +"jobs/"+str(job_id)+"/approve/"

    payload = ""
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }

    return requests.request("POST", url, data=payload, headers=headers, verify=False)

def disapprove_job(job_id, access_token):
    import requests

    url = config.URL +"jobs/"+str(job_id)+"/disapprove/"

    payload = ""
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"
    }

    return requests.request("POST", url, data=payload, headers=headers, verify=False)


def add_qats(job_id, result,access_token, type='POST'):
    import requests

    url = config.URL +"jobs/"+str(job_id)+"/add_qats/"

    headers = {
        'Content-Type': "application/json",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "ccb18fd4-c57d-4896-8d13-8d2ef816878f"
        }

    return requests.request(type, url, json=result, headers=headers, verify=False)

def add_qat(job_id, image_url, result, access_token, type='POST'):
    import requests

    url = config.URL +"jobs/"+str(job_id)+"/add_qat/"

    # change result json to string
    result = str(result).replace("'", '"')

    payload = "{\n\t\"image_url\": \""+image_url+"\",\n\t\"result\": "+result+"\n\t\n}"
    headers = {
        'Content-Type': "application/json",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "ccb18fd4-c57d-4896-8d13-8d2ef816878f"
        }

    return requests.request(type, url, data=payload, headers=headers, verify=False)


def custom_api(**kwargs):
    url = config.URL + kwargs['endpoint']

    payload = kwargs['payload']
    headers = kwargs['headers']

    return requests.request(type, url, data=payload, headers=headers, verify=False)


def get_users(access_token, type='GET'):
    import requests


    url = config.URL + "users/"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url,  headers=headers, verify=False)

def get_users_with_id(user_id,access_token, type='GET'):
    import requests

    url = config.URL + "users/" + str(user_id)+"/"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url,  headers=headers, verify=False)

def get_job_with_id(job_id,access_token, type='GET'):
    import requests

    url = config.URL + "jobs/" + str(job_id)+"/"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url,  headers=headers, verify=False)

def delete_user_with_id(user_id,access_token, type='DELETE'):
    import requests

    url = config.URL + "users/" + str(user_id)+"/"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url,  headers=headers, verify=False)


def create_users(username, password, email, state, roles, access_token, type='POST'):
    import requests

    url = config.URL + "users/"

    payload = "{\n    \"username\": \"" + username + "\",\n    \"password\": \"" + password + "\",\n    \"email\":\"" + email + "\",\n    \"state\": \"" + state + "\",\n    \"roles\":\"" + roles +"\"\n}"
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url, data=payload, headers=headers, verify=False)


def get_task(job_id, access_token, type='GET'):
    import requests

    url = config.URL + "task?job_id=" + str(job_id)

    headers = {
        'Content-Type': "application/json",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "ccb18fd4-c57d-4896-8d13-8d2ef816878f"
    }

    return requests.request(type, url,headers=headers, verify=False)

def get_job(job_id, access_token, type='GET'):
    import requests

    url = config.URL + "jobs/" + str(job_id)+"/"

    headers = {
        'Content-Type': "application/json",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "ccb18fd4-c57d-4896-8d13-8d2ef816878f"
    }

    return requests.request(type, url, headers=headers, verify=False)


def get_random_task(job_id,access_token, type='GET'):
    import requests

    url = config.URL + "task?job_id=" + str(job_id)
    payload = "{\"job_id\": \"%s\"}" % job_id

    headers = {
        'cache-control': "no-cache",
        'Postman-Token': "9d813f4e-450a-43b1-b13c-f8271643e9dd",
        'Authorization': 'Bearer {}'.format(access_token)
             }
    return requests.request(type, url, headers=headers, verify=False)

def post_disengage_job(job_id,access_token,type='POST'):
    import requests
    url = config.URL +"jobs/" + str(job_id)+ "/disengage"+"/"
    payload = ""
    headers = {
        'cache-control': "no-cache",
        'Postman-Token': "8ed98b2a-3280-4125-b020-29e8be0d48ac",
        'Authorization':'Bearer {}'.format(access_token)
    }
    return requests.request(type, url, data=payload, headers=headers, verify=False)

def post_task_result(task_id,result,access_token, type='POST'):
    import requests

    url = config.URL + "tasks/"+str(task_id)+"/post_result/"

    payload = '{"result":'+str(result)+"}"

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "6d61b9ee-96bb-48fb-86a2-bc0d5aba1f36",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url, data=payload, headers=headers, verify=False)
    
def get_job_status_list(status, access_token):
    import requests

    url =config.URL  + "jobs/?status="+str(status)
    headers  = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "c25847ba-7e1a-4500-aa54-7c00d88b54f8"

    }

    return requests.request("GET", url, headers=headers, verify=False)
    
def engaged_worker(job_id,access_token,type = 'GET'):
    import  requests

    url = config.URL +"workers_engaged?job_id="+str(job_id)
    payload = ""
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "8d98351b-4777-406e-b3f6-f8cb7bedee55",
        'Authorization': 'Bearer {}'.format(access_token)
    }

    return requests.request(type, url, data=payload, headers=headers, verify=False)
    
def verify_user(access_token,type='POST'):
    import requests
    url = config.URL + 'login/verify/'
    payload = "{\"token\" : \"" +access_token+"\" }"

    headers = {
        'Content-Type': "application/json",
        'Authorization': 'Bearer {}'.format(access_token),
        'Cache-Control': "no-cache",
        'Postman-Token': "ccb18fd4-c57d-4896-8d13-8d2ef816878f"
    }
    
    return requests.request(type, url, data=payload, headers=headers, verify=False)

def post_activate(user_id,access_token,type = 'POST'):
    import requests

    url = config.URL + "users/" + (str(user_id)) + "/activate/"
    payload = ""
    headers = {
    'Authorization': 'Bearer {}'.format(access_token),
    'cache-control': "no-cache",
    'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url, data=payload, headers=headers, verify=False)


def post_deactivate(user_id,access_token,type):
    import requests

    url = config.URL + "users/" + (str(user_id)) + "/deactivate/"
    payload = ""
    headers = {
    'Authorization': 'Bearer {}'.format(access_token),
    'cache-control': "no-cache",
    'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url, data=payload, headers=headers, verify=False)

def download_qats(job_id,access_token,type = 'GET'):
    import requests

    url = config.URL + "qats?job_id=" + job_id

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'cache-control': "no-cache",
        'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url,headers=headers, verify=False)

def download_result(job_id,worker_id,access_token,type = 'GET'):
    import requests

    url = config.URL + "results?job_id=" + job_id + "&worker_id=" + worker_id

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'cache-control': "no-cache",
        'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url,headers=headers, verify=False)

def mturk_download_result_by_job_id(job_id,access_token,type = 'GET'):
    import requests

    url = config.URL + "results?job_id=" + job_id

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'cache-control': "no-cache",
        'Postman-Token': "86be456e-7465-4c73-b377-5c81b8d99e88"
    }
    return requests.request(type, url,headers=headers, verify=False)