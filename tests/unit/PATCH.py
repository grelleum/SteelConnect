# coding: utf-8


# from PRIVATE import REALM_ADMIN, ORG_ADMIN, PASSWORD
# from PRIVATE import REALM_2_8, REALM_2_9, REALM_2_10, REALM_2_11


import json
# import requests




class Fake_Response(object):
    def __init__(self, url, status_code, result, content='json'):
        self.url = url
        self.ok = True if status_code < 300 else False
        self.status_code = status_code
        self.headers= {'Content-Type': 'application/' + content}
        self.text = json.dumps(result, indent=4)
        self.result = result
    def json(self):
        return self.result


responses = {
    'org': {'id': 'not_an_id', 'name': 'steelconnection'},
    'orgs': [{'id': 'not_an_id', 'name': 'steelconnection'}],
    'status': {'scm_version': '2.9.1', 'scm_build': '50'},
}

codes = {}


class Fake_Session(object):

    def get(self, url, auth=None, headers=None, params=None, data=None):
        if data is not None:
            raise ValueError('get data must be None.')
        resource = url.split('/')[-1]
        data = responses.get(resource, {})
        status_code = codes.get(resource, 200)
        return Fake_Response(url, status_code, data)

    def getstatus(self, url, auth=None, headers=None, params=None, data=None):
        if data is not None:
            raise ValueError('getstatus data must be None.')
        resource = url.split('/')[-1]
        data = responses.get(resource, {})
        status_code = codes.get(resource, 200)
        return Fake_Response(url, status_code, data)

    def delete(self, url, auth=None, headers=None, params=None, data=None):
        # if data is None:
        #     raise ValueError('delete must have data')
        resource = url.split('/')[-1]
        data = responses.get(resource, {}) if not data else data
        status_code = codes.get(resource, 200)
        return Fake_Response(url, status_code, data)
 
    def post(self, url, auth=None, headers=None, params=None, data=None):
        if params is not None:
            raise ValueError('post params must be None.')
        if data is None:
            raise ValueError('post have must data')
        resource = url.split('/')[-1]
        status_code = codes.get(resource, 200)
        return Fake_Response(url, status_code, data)

    def put(self, url, auth=None, headers=None, params=None, data=None):
        if data is None:
            raise ValueError('put have must data')        
        resource = url.split('/')[-1]
        status_code = codes.get(resource, 200)
        return Fake_Response(url, status_code, data)

