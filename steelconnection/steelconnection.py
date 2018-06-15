# coding: utf-8

"""SteelConnection

Convienience objects for making REST API calls
to Riverbed SteelConnect Manager.

Usage:
    sconnect = steelconnection.SConAPI(scm_name, username, password)

    Option keyword version can be used to specify an API version number.
    Currently there is only one API version: '1.0'.

    Once you have instantiated an object as shown above,
    you can use the object to make calls to the REST API.

    For example, to get all nodes in the realm:
    nodes = sconnect.config.get('nodes')
    ... or in a specifc org:
    nodes = sconnect.config.get('/org/' + orgid + '/nodes')  
    
    Any call that does not result in a success (HTTP status code 200)
    will raise an exception, so calls should be wrapped in a try/except pair.
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import getpass
import json
import requests
import sys

from requests import HTTPError
from steelconnection.lookup import _LookUp
from steelconnection.input_tools import get_username, get_password


class SConError(HTTPError):
    pass


class SConAPI(object):
    """Make REST API calls to Riverbed SteelConnect Manager."""

    def __init__(
        self,
        controller,
        username=None,
        password=None,
        version='1.0',
        exit_on_error = False,
        raise_on_bad_request = True,
    ):
        """Initialize attributes."""
        if not controller.endswith('.cc'):
            raise ValueError("SteelConnect Manager's name must end with '.cc'")
        self.version = version
        self.controller = controller
        self.exit_on_error = exit_on_error
        self.raise_on_bad_request = raise_on_bad_request
        self.username = get_username() if username is None else username
        self.password = get_password() if password is None else password
        self.session = requests.Session()
        self.result = None
        self.response = None
        self.headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
        }
        self.lookup = _LookUp(self)
        # self.org = Org()

    def __bool__(self):
        """Return the success of the last request."""
        if self.response is None:
            return False
        return True if self.response.status_code == 200 else False

    def __repr__(self):
        """Return a string consisting of class name, controller, and api."""
        details = ', '.join([
            "controller: '{0}'".format(self.controller),
            "api version: '{0}'".format(self.version),
            "response: '{0}'".format(self.response),
        ])
        return '{0}({1})'.format(self.__class__.__name__, details)

    def get(self, resource, data=None):
        """Make an HTTP GET request for the Config API resource."""
        return self._request(self.session.get, 'config', resource)

    def getstatus(self, resource, data=None):
        """Make an HTTP GET request for the Reporting API resource."""
        return self._request(self.session.get, 'reporting', resource)

    def delete(self, resource, data=None):
        """Make an HTTP DELETE request for the Config API resource."""
        return self._request(self.session.delete, 'config', resource)

    def post(self, resource, data=None):
        """Make an HTTP POST request for the Config API resource."""
        return self._request(self.session.post, 'config', resource, data)

    def put(self, resource, data=None):
        """Make an HTTP PUT request for the Config API resource."""
        return self._request(self.session.put, 'config', resource, data)

    def url(self, api, resource):
        """Combine attributes and resource as a url string."""
        resource = resource[1:] if resource.startswith('/') else resource
        return 'https://{0}/api/scm.{1}/{2}/{3}'.format(
            self.controller, api, self.version, resource,
        )
    
    def _request(self, request_method, api, resource, data=None):
        """Send request to controller and handle response."""
        self.response = self._make_request(request_method, api, resource, data)
        if not self.response.ok:
            error = _error_string(self.response)
            if self.exit_on_error:
                print(error, file=sys.stderr)
                sys.exit(1)
            elif self.raise_on_bad_request:
                raise SConError(error)
            return {'error': error}
        if not self.response.json():
            self.result = {}
        elif 'items' in self.response.json():
            self.result = self.response.json()['items']
        else:
            self.result = self.response.json()
        return self.result

    def _make_request(self, request_method, api, resource, data=None):
        """Send HTTP request to SteelConnect manager."""
        if data and isinstance(data, dict):
            data = json.dumps(data)
        try:
            response = request_method(
                url=self.url(api, resource),
                auth=(self.username, self.password),
                headers=self.headers,
                data=data,
            )
        except Exception as e:
            if self.exit_on_error:
                error = 'Connection to SteelConnect Manager failed:'
                print(error, file=sys.stderr)
                print(e, file=sys.stderr)
                sys.exit(1)
            else:
                raise e
        return response


def _error_string(response):
    try:
        details = response.json()
    except json.JSONDecodeError:
        details = {}
    finally:
        details = details.get('error', {}).get('message', '')
    error = '{} - {}\nURL: {}{}'.format(
        response.status_code,
        response.reason,
        response.url,
        '\nServer response: ' + details if details else '',
    )
    return error
