#!/usr/bin/env python
__author__ = 'Chad Peterson'
__email__ = 'chapeter@cisco.com'

from acimigrate.Devices import Nexus, APIC
import acitoolkit.acitoolkit as aci



apic_url = "http://10.94.238.68"
apic_username = "admin"
apic_password = "cisco123"

nexus_hostname = "10.94.238.121"
nexus_username = "admin"
nexus_password = "cisco"

nexus2_hostname = "10.94.238.122"
nexus2_username = "admin"
nexus2_password = "cisco"

nexus = Nexus(nexus_hostname, nexus_username, nexus_password)
nexus2 = Nexus(nexus2_hostname, nexus2_username, nexus2_password)
apic = APIC(apic_url, apic_username, apic_password)


# aci_switches = apic.list_switches()
#fabric_interfaces = apic.get_fabric_interfaces()
#
# dict = {}
# for switch in aci_switches:
#     if switch.role == 'leaf':
#         switch_int_list = apic.get_switch_interfaces(switch.node)
#         print switch.name
#         print('=' * len(switch.name))
#
#         for interface in switch_int_list:
#             print interface.attributes['id']

aci_switch_dict = {}
aci_switches = apic.list_switches()
for aci_switch in aci_switches:
    if aci_switch.role == 'leaf':
        switch_int_list = apic.get_switch_interfaces(aci_switch.node)
        int_list = []
        for int in switch_int_list:
            int_list.append(int.attributes['id'])
        aci_switch_dict[aci_switch.name] = int_list

print aci_switch_dict
#apic.get_switch_interfaces()