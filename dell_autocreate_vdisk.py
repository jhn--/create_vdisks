#!/usr/bin/env python
import shlex, subprocess

pdisk_list = "omreport storage pdisk controller=0 -fmt ssv"
vdisk_list = "omreport storage vdisk controller=0 -fmt ssv"

id_column = "awk -F';' '{ if (NR > 5) {print $1} }'"
device_column = "awk -F';' '{ if (NR > 6) {print $11} }'"

def get_vdisks_ids(arg1, arg2):
    #gets list of virtual disk IDs
    get_vdisks_list = subprocess.Popen(shlex.split(arg1), stdout = subprocess.PIPE)
    get_vdisks_ids = subprocess.Popen(shlex.split(arg2), stdin = get_vdisks_list.stdout, stdout = subprocess.PIPE).communicate()[0]
    get_vdisks_list.stdout.close()
    get_vdisks_list.wait()
    return get_vdisks_ids

def get_pdisks_ids(arg1, arg2):
    #gets list of physical disk IDs
    get_pdisks_list = subprocess.Popen(shlex.split(arg1), stdout = subprocess.PIPE)
    get_pdisk_ids = subprocess.Popen(shlex.split(arg2), stdin = get_pdisks_list.stdout, stdout = subprocess.PIPE).communicate()[0]
    get_pdisks_list.stdout.close()
    get_pdisks_list.wait()
    return get_pdisk_ids

def get_vdisks_device_names(arg1, arg2):
    #get list of device names of virtual disks
    get_vdisks_list = subprocess.Popen(shlex.split(arg1), stdout = subprocess.PIPE)
    vdisks_device_names_list = subprocess.Popen(shlex.split(arg2), stdin = get_vdisks_list.stdout, stdout = subprocess.PIPE).communicate()[0]
    get_vdisks_list.stdout.close()
    get_vdisks_list.wait()
    return vdisks_device_names_list

def create_vdisks(arg1):
    #get list of disks in /dev/ for partitioning
    command = "omconfig storage controller controller=0 action=createvdisk raid=r0 size=max pdisk="
    command1 = []
    for i in arg1:
        command1.append(command + i)
    for i in command1:
        createvdisk = subprocess.Popen(shlex.split(i))
        createvdisk.wait()

def partition_vdisks(arg1):
    #partitioning of virtual disks
    for i in arg1:
        command = "/sbin/fdisk " + i
        with open('/tmp/fdisk_choices') as f:
            partition_devices = subprocess.Popen(shlex.split(command), stdin = f, stdout = subprocess.PIPE).communicate()[0]
        f.close()
        command = "/sbin/fdisk "

vdisk_ids_inused = get_vdisks_ids(vdisk_list, id_column).split()

pdisk_ids_inused = []

for i in vdisk_ids_inused:
    _list_of_pdisks_based_on_vdisks_inused = "omreport storage pdisk vdisk={0} controller=0 -fmt ssv".format(i)
    pdisk_of_vdisk = subprocess.Popen(shlex.split(_list_of_pdisks_based_on_vdisks_inused), stdout = subprocess.PIPE)
    id_pdisk_of_vdisk = subprocess.Popen(shlex.split(id_column), stdin = pdisk_of_vdisk.stdout, stdout = subprocess.PIPE).communicate()[0]
    id_pdisk_of_vdisk = id_pdisk_of_vdisk.strip().split()
    for j in id_pdisk_of_vdisk:
        pdisk_ids_inused.append(j)

all_pdisk_id = get_pdisks_ids(pdisk_list,id_column).split()

cache_and_fast_disks_pdisks = []
for k in all_pdisk_id:
    if k not in pdisk_ids_inused:
        cache_and_fast_disks_pdisks.append(k)

create_vdisks(cache_and_fast_disks_pdisks)

cache_fast_device_names = get_vdisks_device_names(vdisk_list, device_column).split()

partition_vdisks(cache_fast_device_names)