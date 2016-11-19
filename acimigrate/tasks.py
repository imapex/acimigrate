import logging
import ipaddress
import random

logger = logging.getLogger(__name__)

logger.info('Loading Tasks')


def migrate(nx, apic, nx2, auto=True,
            layer3=False, n1_int_list=None,
            n2_int_list=None):
    full_migration_dict = nx.migration_dict()
    # TODO - Test not using nx1pc_list,
    # but use nx.pc_list() directly in below while statement
    nx1pc_list = nx.pc_list()
    migration_dict = full_migration_dict['vlans']
    nx1pc = random.randrange(1, 4096)
    nx2pc = nx1pc
    # TODO - Test for condition in nx2, and re-run until both nx1pc and nx2pc are valid
    while not(nx1pc not in nx.vpc_dict["vpc_list"] and nx1pc not in nx1pc_list):
        nx1pc = random.randrange(1, 4096)
    print "********"
    print migration_dict
    print "********"
    result = {}
    for v in migration_dict.keys():
        name = migration_dict[v]['name']
        hsrp = migration_dict[v]['hsrp']
        if auto:
            tenant = apic.create_epg_for_vlan(name)
            if tenant.ok:
                logger.info('Created EPG for vlan {}'.format(name))
                print 'Created EPG for vlan {}'.format(name)
                result[name] = 'SUCCESS'
            else:
                logger.info('Failed to create EPG for vlan {}'.format(name))
                print 'Failed to create EPG for vlan {}'.format(name)
                result[name] = 'FAILED'
            if layer3 and hsrp:
                    count = 0
                    for vip in hsrp['vips']:
                        ip = unicode(vip)
                        subnet = unicode(hsrp['subnets'][count]+"/"+str(hsrp['masks'][count]))
                        if ipaddress.ip_address(ip) in ipaddress.ip_network(subnet):
                            mask = str(hsrp['masks'][count])
                        else:
                            mask = "24"
                        tenant = apic.create_epg_for_vlan(name,
                                                          mac_address=hsrp['vmac'],
                                                          net=vip+'/'+mask)
                        count = count + 1
                        if tenant.ok:
                            logger.info('Layer 3 migration '
                                        'for {} vlan completed'.format(name))
                            print 'Layer 3 migration for {}' \
                                  ' vlan completed'.format(name)
    nx.config_phy_connection(n1_int_list, str(nx1pc))
    result['nx1pc'] = nx1pc
    nx2.config_phy_connection(n2_int_list, str(nx2pc))
    result['nx2pc'] = nx2pc
    return result
