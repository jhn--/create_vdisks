#!/usr/bin/env python
import shlex, subprocess

command = "omreport storage pdisk vdisk=0 controller=0 -fmt ssv"
command2 = "awk -F';' '{ if (NR > 5) {print $1} }'"
command3 = "omreport storage pdisk controller=0 -fmt ssv"

def get_pdisks(arg1, arg2):
    get_pdisk_from_existing_vdisks = subprocess.Popen(shlex.split(arg1), stdout=subprocess.PIPE)
    get_pdisk_ids = subprocess.Popen(shlex.split(arg2), stdin=get_pdisk_from_existing_vdisks.stdout, stdout=subprocess.PIPE).communicate()[0]
    get_pdisk_from_existing_vdisks.stdout.close()
    get_pdisk_from_existing_vdisks.wait()
    return get_pdisk_ids

def create_vdisks(arg1):
    command = "omconfig storage controller controller=0 action=createvdisk raid=r0 size=max pdisk="
    command1 = []
    for i in arg1:
        command1.append(command + i)
    for i in command1:
        createvdisk = subprocess.Popen(shlex.split(i))
        createvdisk.wait()

sda_pdisk_id = get_pdisks(command, command2).split()
all_pdisk_id = get_pdisks(command3,command2).split()
cache_and_fast_disks_pdisks = []

for i in all_pdisk_id:
    if i not in sda_pdisk_id:
        cache_and_fast_disks_pdisks.append(i)

create_vdisks(cache_and_fast_disks_pdisks)
