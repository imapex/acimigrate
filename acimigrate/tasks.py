import logging

logger = logging.getLogger(__name__)

logger.info('Loading Tasks')
def migrate(nx, apic, auto=True, layer3=False):
    migration_dict = nx.migration_dict()
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
                    for vip in hsrp['vips']:
                        tenant = apic.create_epg_for_vlan(name,
                                                          mac_address=hsrp['vmac'],
                                                          net=vip+'/24') #TODO: need to get mask dynamically
                        if tenant.ok:
                            logger.info('Layer 3 migration for {} vlan completed'.format(name))
                            print 'Layer 3 migration for {} vlan completed'.format(name)
    return result
