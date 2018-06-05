# SteelConnection
REST API access to Riverbed SteelConnect Manager.

SteelConnection provides wrapper objects to simplify access to the Riverbed SteelConnect REST API.
The SteelConnection objects store the SCM base URL and authentication so that you only need to pass in the resource and any required data.
The object creates a Request session object, which is sent to the SteelConnect Manager and passes back a response object with an additional 'data' attribute containing any data from the SteelConnect Manager.

Supports Python 2.7, 3.4, 3.5, 3.6


## Requires:
Requests


## HOWTO:


### NOTE:
2018-06-04: The SteelConnection API has changed.  Previously there were two objects, Config and Reporting, to match the two SteelConnect REST APIs.  Now the two APIs are consolidated under a single object.  Calls to `get`, `post`, `put`, and `delete` are now prefaced with either `config.` or `report.`


### TL;DR:
See the examples direcory for sample scripts.


### Getting Started:
* Make sure the REST API is enabled on your SteelConnect realm before trying to access the REST API.
* Copy the steelconnecton.py file into the same folder as your script.
* Import steelconnection and create a new object by providing the Fully qualified DNS name of your realm.  This would typically be `REALM_NAME.riverbed.cc`, where `REALM_NAME` is specific to your realm.
```python
import steelconnection
sconnect = steelconnection.SConAPI('REALM.riverbed.cc')
```

### Realms and Organizations:
There is a one to one relationship between a Realm and a SteelConnect Manager.  The SteelConnect Manager acts as the controller for a the realm.  A newly created realm would not have any organizations, otherwise a realm will have one or more organizations.  Each oganization within a realm acts an autonomous network system. In practice, most REST API operations are performed within a specific organization.

You normally access the SteelConnect Manager (SCM) using a web browser.\
The URL you use includes the realm and organization that you are managing and takes the form:
`    https://realm.riverbed.cc/admin/Organization`.\
The Organization is case-sensistive and is also known as the organization short name, as opposed to the longname, which is more descriptive and can include spaces, and other characters.


### Authentication:

#### Note on password security:
The password entered gets stored in the wrapper object in plain text.  So if you were to query the object attributes you could easily see the password.  This is done for the convienience of not requiring the password to be input or passed everytime an API call is made.

#### Interactive login:
SteelConnect REST API uses username and password authentication.  If a SteelConnection object gets created without a specified username and password, the object will interactively prompt you for your username and password.  
```python
>>> import steelconnection
>>> sconnect = steelconnection.SConAPI('REALM.riverbed.cc')
Enter username: admin
Enter password: 
Retype password: 
>>> 
```
#### Specifying username and password:
If you prefer to use some other method to obtain the username and password, you can supply those as the time of object creation using the username and password keywaord argumets.\
For example, if you want to store your credentials in your system environment variables you could do something similar to the following:
```python
import os
import steelconnection

username = os.environ.get('SCONUSER')
password = os.environ.get('SCONPASSWD')

sconnect = steelconnection.SConAPI('REALM.riverbed.cc', username=username, password=password)
```

### Understanding the API:
The Riverbed SteelConnect REST API allows HTTPS access to the SteelConnect Manager (SCM) via the use of GET, POST, PUT, and DELETE commands.\
SteelConneciton (this module) acts to simplify coding by providing an object that remembers your realm, version, and authentication and builds yje HTTPS requests with that information included.  A `requests.session` object is used to allow a single TCP connection to be re-used for each API request.\

**With** SteelConnection, a request to get a list of all organizations in the realm would look like this:\
`orgs = sconnect.config.get('orgs').data`

**Without** SteelConnection, the same request would look like this:\
`orgs = requests.get('https://REALM.riverbed.cc/api/scm.config/1.0/orgs', auth=(username, password)).json()['items']`

#### Available Methods:
SteelConneciton provides the `.get`, `.post`, `.put`, and `.delete` metheods to simplify access to the API.\
These methods will build the request to include api version, auth, etc, so you onlu need to specify the resource you are interrested in.

* Get: Used for retrieving information or status about a resource.  Expect data to be returned.
* Post: Create or deploy a resource that does not already exist.
* Put: Use to edit or update some existing resource.
* Delete: Delete an existing resource/

#### Two APIs:
Riverbed divides the REST API into two APIs:
* Config: used to make configurations changes and get information about SteelConnect resources.\
https://support.riverbed.com/apis/scm_beta/scm-2.10.0/scm.config/index.html
* Reporting: used to get current status information about a resource.\
https://support.riverbed.com/apis/scm_beta/scm-2.10.0/scm.reporting/index.html

SteelConnections deals with this by providing two paths to access these two APIs.
* To  access the Config API: <pre>sconnect.<b>config</b>.get(<i>resource_path</i>)</pre>
* To  access the Reporting API: <pre>sconnect.<b>report</b>.get(<i>resource_path</i>)</pre>

For example, To see how a port on an appliance is configured use the `config` path:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`sconnect.config.get(f'port/{port}').data`\
To see the the actual link state, speed, and duplex for a port, you would use the `report` path:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`sconnect.report.get(f'port/{port}').data`\
    `sconnect.config.get(f'port/{port}').data`\

### Retrieving Data:
The steelconnect methods leverage the popular requests package.  All returned objects are a `requests.response` object, with an extra `.data` attribute added.  By providing the full `requests.response` object you are free to check status and see all headers.  The additional `.data` attibute will contain a 'best-guess' python native format object that is most likely what you are trying to retrieve by making the call.

For example, the 'get orgs' requests should always provide a list of orgs within the realm.  By adding the `.data` to the request we can directly assign the return list as a native Python list.\
`list_of_all_orgs = sconnect.config.get('orgs').data`

Here are the rules to determine what gets returned in the `response.data` attribute:
* If json data is returned and the key 'items' is in the json data, then return a python list of 'items'.
* If json data is returned and the key 'items' is not in the json data, then return the json data as a python dictionary.
* If no json data is returned, data will be an empty python dictionary.


### Convienience functions:
The SteelConnect Manager stores resources in a database with a uniquie identifier (id).  Many API calls require that you know the id number of the resource you are interested in.\
SteelConnection provides a collection of `lookup` functions to look up the id for various API resources.\
Currently these are the available lookup functions:\
* `lookup.orgid(org_short_name)`\
* `lookup.nodeid(serial)`\
* `lookup.siteid(site_name, org_id=org_id)`\

##### Lookup Organization ID:
Many REST API calls require that you know the org id of your organization.  You can provide the organization short name to the function and it will return the org id.
```python
>>> org_id = sconnect.lookup.orgid('Spacely')
>>> org_id
'org-Spacely-0a0b1cbadb33f34'
>>> 
```
##### Lookup Node ID:
Similarly, the `lookup.nodeid` method exists to privide the node id when you supply the appliance serial number.
```python
>>> node_id = sconnect.lookup.nodeid('XN00012345ABCDEF')
>>> node_id
'node-56f1968e222ab789'
>>> 
```
##### Lookup Site ID:
The site id can be found in a similar way, but since the same site name, like HQ, could exist in multiple organizations, the org_id must also be supplied.
```python
>>> site_id = sconnect.lookup.siteid('Skypad', orgid='org-Spacely-0a501e7f27b2c03e')
>>> site_id
'site-Skypad-884b9071141e4bc0'
>>> 
```
