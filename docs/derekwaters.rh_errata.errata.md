# derekwaters.rh_errata.errata
Lookup data from Red Hat Errata.

The data provided by the lookupis the CSAF / VEX data returned from the [Red Hat Errata API](https://docs.redhat.com/en/documentation/red_hat_security_data_api/1.0/html/red_hat_security_data_api/overview).

## Requirements
The host that executes this event source requires:
* python >= 3.6

## Parameters
| Parameter | Choices/Default | Comments |
| --------- | --------------- | -------- |
| **rhsa** (string) |  | The RHSA identifier of the Errata to look up |

## Examples
```
---
- name: Lookup details of a Red Hat Errata record
  hosts: all
  vars:
    _rhsa_id: "RHSA-2022:6155"
  
  tasks:
    - name: Lookup the errata data
      ansible.builtin.set_fact:
        _rhsa_data: "{{ lookup('derekwaters.rh_errata.errata', rhsa=_rhsa_id)}}"
```

## Return Values
| Key | Returned | Description |
| --- | -------- | ----------- |
| **data** (dict) | success | A dictionary containing information about the errata as returned from the Red Hat Errata API |

## Authors
* Derek Waters (derek@frisbeeworld.com)