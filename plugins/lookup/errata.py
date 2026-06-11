import requests

from typing import NoReturn

from ansible.plugins.lookup import LookupBase

DOCUMENTATION = """
name: errata
short_description: Look up Red Hat Errata details.
version_added: 1.0.0
author:
    - Derek Waters (derek@frisbeeworld.com)
description:
    - Retrieve a Red Hat Errata record via its RHSA identifier.
options:
  rhsa:
    description:
      - The RHSA identifier of the errata to be retrieved.
    required: true
    type: str
"""


EXAMPLES = """
- name: Retrieve a Red Hat Errata record
  ansible.builtin.debug:
    msg: "{{ lookup('derekwaters.rh_errata.errata',
                    rhsa='RHSA-2022:6155') }}"
"""

RETURN = """
_raw:
  description:
      - A list of dictionaries containing the Red Hat Errata data.
      - Refer to the Red Hat Errata Security API documentation for the details of what will be returned.
  type: list
  elements: dict
  sample:
    rhsa: "RHS-2022:6155"
    severity: "critical"
"""

BASE_URL = "https://access.redhat.com/hydra/rest/securitydata/"


class LookupModule(LookupBase):

    def _get_data(self, url):
        errata_data = None

        session = requests.Session()
        response = session.request('GET', url)
        response.raise_for_status()
        if response.content:
            return response.json()
        else:
            raise AnsiblePluginError(
                      message="The Errata URL returned a HTTP {} status error".format(response.status)
                  )
                  
    def run(self, terms, variables=None, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        rhsa_id = self.get_option("rhsa")

        errata_url = "{}/csaf/{}.json".format(BASE_URL, rhsa_id)
        errata_data = self._get_data(errata_url)

        return [errata_data]
