#!/usr/bin/env python
import shlex, subprocess

controller_list = "omreport storage controller -fmt ssv"
pdisk_list = "omreport storage pdisk controller={0} -fmt ssv"
vdisk_list = "omreport storage vdisk controller={0} -fmt ssv"
pdisk_of_used_vdisks_list = "omreport storage pdisk vdisk={1} controller={0} -fmt ssv"

id_column = "awk -F';' '{ if (NR > 5) {print $1} }'"
device_column = "awk -F';' '{ if (NR > 5) {print $11} }'"

def get_omreport_info(arg1, arg2, arg3 = '0'):
    # Get list of physical disk IDs.
    # Reused to get list of virtual disks ID and device names.
    print "get_omreport_info {0} {1} {2}".format(arg1, arg2, arg3)
    get_list = subprocess.Popen(shlex.split(arg1.format(arg3)), stdout = subprocess.PIPE)
    get_columns = subprocess.Popen(shlex.split(arg2), stdin = get_list.stdout, stdout = subprocess.PIPE).communicate()[0]
    get_list.stdout.close()
    get_list.wait()
    #print get_columns
    return get_columns

def create_vdisks(arg1, arg3 = '0'):
    #get list of disks in /dev/ for partitioning
    #print "create_vdisks {0} {1}".format(arg1, arg3)
    command = "omconfig storage controller action=createvdisk raid=r0 size=max pdisk={0} controller={1}"
    for i in arg1:
        createvdisk = subprocess.Popen(shlex.split(command.format(i, arg3)))
        createvdisk.wait()

def partition_vdisks(arg1):
    #partitioning of virtual disks
    for i in arg1:
        #print "partition_vdisks {0}".format(i)
        command = "/sbin/fdisk {0}".format(i)
        with open('/tmp/fdisk_choices') as f:
            partition_devices = subprocess.Popen(shlex.split(command), stdin = f, stdout = subprocess.PIPE).communicate()[0]
        f.close()

#get list of controller ids
controller_ids = get_omreport_info(controller_list, id_column).split()

#for each controller, the script identify used vdisks - and corresponding pdisks - and left alone, the remaining pdisks are then created as a raid0 vdisk.
for i in controller_ids:
    used_vdisks = get_omreport_info(vdisk_list, id_column, i).split()
    all_pdisk_id = get_omreport_info(pdisk_list,id_column, i).split()

    used_pdisks = []

    for j in used_vdisks:
        pdisk_of_vdisk = subprocess.Popen(shlex.split(pdisk_of_used_vdisks_list.format(i, j)), stdout = subprocess.PIPE)
        id_pdisk_of_vdisk = subprocess.Popen(shlex.split(id_column), stdin = pdisk_of_vdisk.stdout, stdout = subprocess.PIPE).communicate()[0]
        id_pdisk_of_vdisk = id_pdisk_of_vdisk.strip().split()
        for k in id_pdisk_of_vdisk:
            used_pdisks.append(k)
        #print used_pdisks

    cache_and_fast_disks_pdisks = []
    for l in all_pdisk_id:
        if l not in used_pdisks:
            cache_and_fast_disks_pdisks.append(l)
    #print cache_and_fast_disks_pdisks

    create_vdisks(cache_and_fast_disks_pdisks)
    cache_fast_device_names = get_omreport_info(vdisk_list, device_column).split()
    partition_vdisks(cache_fast_device_names)