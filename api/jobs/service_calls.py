import json
import simplejson
import requests
from   requests.exceptions import HTTPError

from django.conf import settings
from rest_framework import status


class ExternalMicroServiceError(Exception):
    """
    Todo:
    """
    def __init__(self, *args):
        super(ExternalMicroServiceError, self).__init__(*args)

class ConnectivityError(ExternalMicroServiceError):
    """
    Todo:
    """
    def __init__(self, *args):
        super(ConnectivityError, self).__init__(*args)

class URLError(ExternalMicroServiceError):
    """
    Todo:
    """
    def __init__(self, *args):
        super(URLError, self).__init__(*args)

class ResponseError(ExternalMicroServiceError):
    """
    Todo:
    """
    def __init__(self, *args):
        super(ResponseError, self).__init__(*args)

class AnnotationAnalysisAndProcessingApi(object):
    HOST = settings.MICRO_SERVICES['ANNOTATION_ANALYSIS_AND_PROCESSING']

    @classmethod
    def qualify(cls, searcher_dict, worker_dict):

        payload = {
                    'searcher': searcher_dict,
                    'worker': worker_dict
                  }

        headers = {
                    'Content-Type': 'application/json',
                  }
        try:
            response =  requests.post(url     = cls.HOST + r'qualify/',
                                      headers = headers,
                                      data    = json.dumps(payload))
            response.raise_for_status()

        except requests.exceptions.ConnectionError as err:
            raise ConnectivityError(err.args[0])

        except simplejson.errors.JSONDecodeError as err:
            raise URLError(err.args[0])

        except HTTPError:
            raise ResponseError(response.json()['error'])

        if response.status_code != status.HTTP_200_OK:
            raise ResponseError(response.json()['error'])

        return response.json()

    @classmethod
    def validate(cls, json_dict):
        headers = {
                    'Content-Type': 'application/json',
                  }
        try:
            response =  requests.post(url     = cls.HOST + r'validate/',
                                      headers = headers,
                                      data    = json.dumps(json_dict))
            response.raise_for_status()

        except requests.exceptions.ConnectionError as err:
            raise ConnectivityError(err.args[0])

        except simplejson.errors.JSONDecodeError as err:
            raise URLError(err.args[0])

        except HTTPError:
            raise ResponseError(response.json()['error'])

        if response.status_code != status.HTTP_200_OK:
            raise ResponseError(response.json()['error'])

    @classmethod
    def validate_boxing_type(cls, boxing_type, json_input):
        payload = {
                    'boxing_type': boxing_type,
                    'json': json_input
                  }

        headers = {
                    'Content-Type': 'application/json',
                  }
        try:
            response =  requests.post(url     = cls.HOST + r'validate_boxing_type/',
                                      headers = headers,
                                      data    = json.dumps(payload))
            response.raise_for_status()

        except requests.exceptions.ConnectionError as err:
            raise ConnectivityError(err.args[0])

        except simplejson.errors.JSONDecodeError as err:
            raise URLError(err.args[0])

        except HTTPError:
            raise ResponseError(response.json()['error'])

        if response.status_code != status.HTTP_200_OK:
            raise ResponseError(response.json()['error'])

    @classmethod
    def consolidate(cls, data):
        headers = {
                    'Content-Type': 'application/json',
                  }
        try:
            response =  requests.post(url     = cls.HOST + r'consolidate/',
                                      headers = headers,
                                      data    = json.dumps(data))
            response.raise_for_status()

        except requests.exceptions.ConnectionError as err:
            raise ConnectivityError(err.args[0])

        except simplejson.errors.JSONDecodeError as err:
            raise URLError(err.args[0])

        except HTTPError:
            raise ResponseError(response.json()['error'])

        if response.status_code != status.HTTP_200_OK:
            raise ResponseError(response.json()['error'])

        return response.json()