import logging
import ipaddress

logger = logging.getLogger(__name__)

logger.info('Loading Tasks')
def migrate(nx, apic, auto=True, layer3=False):
    full_migration_dict = nx.migration_dict()
    migration_dict = full_migration_dict['vlans']
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
                            #TODO: Add some better failure logic
                            #TODO: once multiple IP and VIP logic added, need to find proper subnet mask in list
                        tenant = apic.create_epg_for_vlan(name,
                                                          mac_address=hsrp['vmac'],
                                                          net=vip+'/'+mask)
                        count = count + 1
                        if tenant.ok:
                            logger.info('Layer 3 migration for {} vlan completed'.format(name))
                            print 'Layer 3 migration for {} vlan completed'.format(name)
    return result
