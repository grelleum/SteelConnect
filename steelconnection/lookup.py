# coding: utf-8

"""SteelConnection

Convienience object for ID value lookups based on common criteria.

Should be instantiated within a steelconnection object.
"""


class _LookUp(object):
    """Provide convienience tools to lookup objects."""

    def __init__(self, sconnection):
        """Obtain access to SteelConect Manager."""
        self.sconnection = sconnection

    def _lookup(self, domain, value, key, return_value='id'):
        """Generic lookup function."""
        items = self.sconnection.get(domain)
        for item in items:
            item_value = item.get(key, '')
            if item_value and value in item_value:
                self.sconnection.result = item.get(return_value, '')
                return self.sconnection.result, item

    def nodeid(self, serial, key='serial'):
        """Return node id that matches appliance serial number provided."""
        result, _details = self._lookup(domain='nodes', value=serial, key=key)
        return result

    def orgid(self, name, key='name'):
        """Return org id that matches organization short name provided."""
        result, _details = self._lookup(domain='orgs', value=name, key=key)
        # self.sconnection.org.details = details
        return result

    def siteid(self, name, orgid=None, key='name'):
        """Return site id that matches site short name
        based on the organization provided.
        """
        if not orgid:
            raise ValueError('orgid required when looking up a site.')
        resource = '/'.join(('org', orgid, 'sites'))
        result, _details = self._lookup(domain=resource, value=name, key=key)
        return result

    def node(self, serial, key='serial'):
        """Return node id that matches appliance serial number provided."""
        return self._lookup(domain='nodes', value=serial, key=key)

    def org(self, name, key='name'):
        """Return org id that matches organization short name provided."""
        return self._lookup(domain='orgs', value=name, key=key)

    def site(self, name, orgid=None, key='name'):
        """Return site id that matches site short name
        based on the organization provided.
        """
        if not orgid:
            raise ValueError('orgid required when looking up a site.')
        resource = '/'.join(('org', orgid, 'sites'))
        return self._lookup(domain=resource, value=name, key=key)
