# derekwaters.rh_errata.errata_events
Handle Red Hat Errata events.

The data attached to an event is the CSAF / VEX data returned from the [Red Hat Errata API](https://docs.redhat.com/en/documentation/red_hat_security_data_api/1.0/html/red_hat_security_data_api/overview).

## Requirements
The host that executes this event source requires:
* python >= 3.6

## Parameters
| Parameter | Choices/Default | Comments |
| --------- | --------------- | -------- |
| **interval** (int) | 60 | Interval at which the event source will poll the API (in seconds) |

## Examples
```
---
- name: Handle Red Hat Errata publications
  hosts: all
  sources:
    - name: Red Hat Errata API
      derekwaters.rh_errata.errata_events:
        interval: 60
  rules:
    - name: Handle critical vulnerability errata
      condition: >
        event.body.data.severity == 'critical'
      actions:
        - debug:
            var: event.body.data.RHSA
```

## Return Values
| Key | Returned | Description |
| --- | -------- | ----------- |
| **data** (dict) | success | A dictionary containing information about the errata as returned from the Red Hat Errata API |

## Authors
* Derek Waters (derek@frisbeeworld.com)