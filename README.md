# Red Hat Errata EDA Source

[![Build Status](https://github.com/derekwaters/rh_errata/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/derekwaters/rh_errata/actions/workflows/ci.yml)

An EDA Event Source for published Red Hat Errata notifications via the Red Hat Errata API.

## Included Content

The following set of content is included within this collection:


### Event Sources 

| Name  | Description |
| ----- | ----------- |
| [derekwaters.rh_errata.errata_events](https://github.com/derekwaters/rh_errata/blob/main/docs/derekwaters.rh_errata.errata_events.rst) | Monitor the Red Hat Errata API for new Errata events. |

### Lookup Plugins 

| Name  | Description |
| ----- | ----------- |
| [derekwaters.rh_errata.errata](https://github.com/derekwaters/rh_errata/blob/main/docs/derekwaters.rh_errata.errata.rst) | Lookup details on a specific Red Hat Errata. |

## Usage

The following is an example of how to use the Red Hat Errata Event Source Plugin within an Ansible Rulebook:

```yaml
- name: Listen for newly published Red Hat Errata
  hosts: all
  sources:
    - name: Red Hat Errata API
      derekwaters.rh_errata.errata_events:
        interval: 60
  rules:
    - name: Notify
      condition: event.body.data.severity == "critical"
      action:
        debug:                      
```


The following is an example of how to use the Red Hat Errata Lookup Plugin within an Ansible Playbook:

```yaml
- name: Lookup details of a Red Hat Errata record
  hosts: all
  vars:
    _rhsa_id: "RHSA-2022:6155"
  
  tasks:
    - name: Lookup the errata data
      ansible.builtin.set_fact:
        _rhsa_data: "{{ lookup('derekwaters.rh_errata.errata', rhsa=_rhsa_id)}}"
```

## Building a Decision Environment that includes this library
The instructions provided here are for Automation Platform 2.6

Install `ansible-builder` on a Linux box (preferably Fedora or RHEL)
```
dnf install ansible-builder
```

Install `podman` so that `ansible-builder` can build the image (otherwise it only generates the Containerfile)
```
dnf install podman
```

Create an `ansible-builder` source file to generate the Decision Environment and call it `eda-de-openshift-aap26.yaml`
```yaml
version: 3

images:
  base_image:
    name: 'registry.redhat.io/ansible-automation-platform-26/de-minimal-rhel9:latest'

dependencies:
  galaxy:
    collections:
      - ansible.eda
      - derekwaters.rh_errata
  python_interpreter:
    package_system: "python311"
  system:
    - pkgconfig [platform:rpm]
    - systemd-devel [platform:rpm]
    - gcc [platform:rpm]
    - python3.11-devel [platform:rpm]

options:
  package_manager_path: /usr/bin/microdnf

additional_build_steps:
  append_final:
  # This is a workaround for the bug: https://issues.redhat.com/browse/AAP-32856
    - ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.11/site-packages:/usr/local/lib64/python3.11/site-packages
```

Build the image
```
ansible-builder build -f eda-de-openshift-aap26.yaml --container-runtime podman -v3 --squash all --prune-images -t eda-de-openshift-aap26:0.1.0
```

## License

GPL 2.0 or later