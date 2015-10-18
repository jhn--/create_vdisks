# create_vdisks

Python script to identify unused physical disks and create virtual disks.

Runs on Python 2.7.

Can be used with Ansible using `command` module.

Example

################################################################################################
- name: Copy dell_autocreate_vdisk.py to node
  copy: src=/etc/ansible/roles/common/files/dell_autocreate_vdisk.py dest=/tmp/dell_autocreate_vdisk.py

- name: Make sure copy is successful
  stat: path=/tmp/dell_autocreate_vdisk.py
  register: dell_autocreate_vdisk

- name: Copy fdisk_choices to node
  copy: src=/etc/ansible/roles/common/files/fdisk_choices dest=/tmp/fdisk_choices

- name: Make sure copy is successful
  stat: path=/tmp/fdisk_choices
  register: fdisk_choices

- name: Create vdisks!
  command: /bin/python /tmp/dell_autocreate_vdisk.py
  when: dell_autocreate_vdisk.stat.exists == True and fdisk_choices.stat.exists == True
################################################################################################