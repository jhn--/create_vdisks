#!/usr/bin/env python
import shlex, subprocess

command = "omreport storage pdisk vdisk=0 controller=0 -fmt ssv"
command2 = "awk -F';' '{ if (NR > 5) {print $1} }'"
command3 = "omreport storage pdisk controller=0 -fmt ssv"

command4 = "omreport storage vdisk controller=0 -fmt ssv"
command5 = "awk -F';' '{ if (NR > 6) {print $11} }'"

def get_pdisks(arg1, arg2):
    get_pdisk_from_existing_vdisks = subprocess.Popen(shlex.split(arg1), stdout=subprocess.PIPE)
    get_pdisk_ids = subprocess.Popen(shlex.split(arg2), stdin=get_pdisk_from_existing_vdisks.stdout, stdout=subprocess.PIPE).communicate()[0]
    get_pdisk_from_existing_vdisks.stdout.close()
    get_pdisk_from_existing_vdisks.wait()
    return get_pdisk_ids

def get_vdisks(arg1, arg2):
    #get list of disks in /dev/ for partitioning
    get_vdisks_list = subprocess.Popen(shlex.split(arg1), stdout=subprocess.PIPE)
    device_names = subprocess.Popen(shlex.split(arg2), stdin=get_vdisks_list.stdout, stdout=subprocess.PIPE).communicate()[0]
    get_vdisks_list.stdout.close()
    get_vdisks_list.wait()
    return device_names

def create_vdisks(arg1):
    #get list of disks in /dev/ for partitioning
    command = "omconfig storage controller controller=0 action=createvdisk raid=r0 size=max pdisk="
    command1 = []
    for i in arg1:
        command1.append(command + i)
    for i in command1:
        createvdisk = subprocess.Popen(shlex.split(i))
        createvdisk.wait()

def fdisks(arg1):
    for i in arg1:
        command = "/sbin/fdisk " + i
        print command
        with open('/tmp/fdisk_choices') as f:
            partition_devices = subprocess.Popen(shlex.split(command), stdin=f, stdout=subprocess.PIPE).communicate()[0]
        f.close()
        command = "/sbin/fdisk "

sda_pdisk_id = get_pdisks(command, command2).split()
print sda_pdisk_id

all_pdisk_id = get_pdisks(command3,command2).split()
print all_pdisk_id

cache_and_fast_disks_pdisks = []
for i in all_pdisk_id:
    if i not in sda_pdisk_id:
        cache_and_fast_disks_pdisks.append(i)
print cache_and_fast_disks_pdisks

create_vdisks(cache_and_fast_disks_pdisks)

cache_fast_device_names = get_vdisks(command4, command5).split()

create_paritions = fdisks(cache_fast_device_names)
