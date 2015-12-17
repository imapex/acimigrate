#!/usr/bin/env python
import xml.etree.ElementTree as ET
from ncclient import manager
import acitoolkit.acitoolkit as aci

class APIC(object):
    """
    Class used for creating a connection to ACI fabric
    """

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session = aci.Session(self.url, self.username, self.password, verify_ssl=False)
        self.session.login()
        self.tenant = None
        self.app = None
        self.physdom = None
        self.context = None
        self.contract = None

    def migration_vlan_pool(self, vlan=None):
        topMo = cobra.model.infra("")
        fvnsVlanInstP = cobra.model.fvns.VlanInstP(topMo, name=self.physdom+'-pool', allocMode=u'static')
        raise NotImplemented

    def migration_physdom(self, domain_name):
        self.physdom = domain_name
        topMo = cobra.model.pol.Uni("")
        physDomP = cobra.model.phys.DomP(topMo, name=domain_name)
        infraRsVlanNs = cobra.model.infra.RsVlanNs(physDomP, tDn=u'uni/infra/vlanns-[{}-pool]-static'.format(domain_name))
        raise NotImplemented

    def migration_tenant(self, tenant_name, app_name, provision=True):
        self.tenant = aci.Tenant(tenant_name)
        self.app = aci.AppProfile(app_name, self.tenant)
        self.context = aci.Context('default', self.tenant)

        self.contract = aci.Contract('allow-any', self.tenant)
        entry1 = aci.FilterEntry('default',
                                 applyToFrag='no',
                                 arpOpc='unspecified',
                                 etherT='unspecified',
                                 parent=self.contract)
        if provision:
            self.session.push_to_apic(self.tenant.get_url(), self.tenant.get_json())
        else:
            self.tenant.get_json()
        return self.tenant

    def add_physdom(self, epg):

        attach_dom = {"fvRsDomAtt":{"attributes":{"tDn":"uni/phys-StaticPhyDomain",  ## change tDn to match your physdom
                                                  "status":"created"}}}
        return attach_dom

    def create_epg_for_vlan(self, vlan, mac_address=None, net=None, provision=True):
        epg = aci.EPG(vlan, self.app)
        bd = aci.BridgeDomain(vlan, self.tenant)

        if net:
            subnet = aci.Subnet('subnet-' + vlan, parent=bd)
            subnet.set_addr(net)
            bd.set_unicast_route('yes')
        else:
            bd.set_unicast_route('no')

        if mac_address:
            bd.set_mac(mac_address)

        bd.set_unknown_mac_unicast('flood')
        bd.set_arp_flood('yes')
        bd.add_context(self.context)
        epg.add_bd(bd)
        epg.provide(self.contract)
        epg.consume(self.contract)
        if provision:
            resp = self.session.push_to_apic(self.tenant.get_url(), self.tenant.get_json())
        else:
            print self.tenant.get_json()

        # TODO: attach domain to EPG
        # TODO: add static path binding
        return resp


class Nexus(object):
    """
    Class for gleaning useful information from an NX-OS device

    """
    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = 22
        self.hostkey_verify = False
        self.device_params = {'name': 'nexus'}
        self.allow_agent = False
        self.look_for_keys = False
        self.manager = manager.connect(host=self.host,
                                       port=22,
                                       username=self.user,
                                       password=self.passwd,
                                       hostkey_verify=False,
                                       device_params={'name': 'nexus'},
                                       allow_agent=False,
                                       look_for_keys=False)

    exec_conf_prefix = """
      <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <configure xmlns="http://www.cisco.com/nxos:1.0:vlan_mgr_cli">
          <__XML__MODE__exec_configure>
    """

    exec_conf_postfix = """
              </__XML__MODE__exec_configure>
            </configure>
          </config>
            """

    cmd_vlan_conf_snippet= """
                <vlan>
                  <vlan-id-create-delete>
                    <__XML__PARAM_value>%s</__XML__PARAM_value>
                    <__XML__MODE_vlan>
                      <name>
                        <vlan-name>%s</vlan-name>
                      </name>
                      <state>
                        <vstate>active</vstate>
                      </state>
                      <no>
                        <shutdown/>
                      </no>
                    </__XML__MODE_vlan>
                  </vlan-id-create-delete>
                </vlan>
    """

    cmd_vlan_int_snippet = """
              <interface>
                <ethernet>
                  <interface>%s</interface>
                  <__XML__MODE_if-ethernet-switch>
                    %s
                  </__XML__MODE_if-ethernet-switch>
                </ethernet>
              </interface>
    """

    cmd_no_vlan_int_snippet = """
          <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <configure xmlns="http://www.cisco.com/nxos:1.0:vlan_mgr_cli">
              <__XML__MODE__exec_configure>
              <interface>
                <ethernet>
                  <interface>%s</interface>
                  <__XML__MODE_if-ethernet-switch>
                    <switchport>
                      <trunk>
                        <allowed>
                          <vlan>
                            <__XML__BLK_Cmd_switchport_trunk_allowed_allow-vlans>
                              <remove-vlans>%s</remove-vlans>
                            </__XML__BLK_Cmd_switchport_trunk_allowed_allow-vlans>
                          </vlan>
                        </allowed>
                      </trunk>
                    </switchport>
                  </__XML__MODE_if-ethernet-switch>
                </ethernet>
              </interface>
              </__XML__MODE__exec_configure>
            </configure>
          </config>
    """
    cmd_vlan_common = """
                <switchport>
                  <trunk>
                    <allowed>
                      <vlan>
                        <add>
                        <__XML__BLK_Cmd_switchport_trunk_allowed_allow-vlans>
                          <add-vlans>%s</add-vlans>
                        </__XML__BLK_Cmd_switchport_trunk_allowed_allow-vlans>
                        </add>
                      </vlan>
                    </allowed>
                  </trunk>
                </switchport>
                """

    cmd_vlan_pc_snippet = """
          <interface>
            <Port-Channel>
              <interface>%s</interface>
              <__XML__MODE_if-eth-port-channel-switch>
                %s
              </__XML__MODE_if-eth-port-channel-switch>
            </ethernet>
          </interface>
    """

    filter_show_vlan_brief_snippet =  """
          <show xmlns="http://www.cisco.com/nxos:1.0:vlan_mgr_cli">
            <vlan>
              <brief/>
            </vlan>
          </show> """

    @staticmethod
    def format_mac_address(mac):
        """
        Re-format IOS mac addresses
        :param mac: string mac address in 0000.0000.0000 format
        :return: string 00:00:00:00:00
        """
        return '{0}:{1}:{2}:{3}:{4}:{5}'.format(mac[:2],
                                                mac[2:4],
                                                mac[5:7],
                                                mac[7:9],
                                                mac[10:12],
                                                mac[12:14])

    @property
    def vlan_dict(self):
        query = '''
              <show>
                <vlan/>
              </show>
        '''

        ncdata = str(self.manager.get(('subtree', query)))
        root = ET.fromstring(ncdata)
        namespace_map = {'vlans': 'http://www.cisco.com/nxos:1.0:vlan_mgr_cli'}
        vlan_dict = {}

        for c in root.iter():
            vlans = c.findall('vlans:ROW_vlanbrief', namespace_map)
            for v in vlans:
                vlanid = v.find('vlans:vlanshowbr-vlanid-utf', namespace_map).text
                vlan_name = v.find('vlans:vlanshowbr-vlanname', namespace_map).text
                vlan_dict[vlanid] = vlan_name

        return vlan_dict

    @property
    def svi_dict(self):
        query = '''
            <show>
              <ip>
                <interface/>
            </show>
        '''

        ncdata = str(self.manager.get(('subtree', query)))
        root = ET.fromstring(ncdata)
        svi_ns_map = {'groups': 'http://www.cisco.com/nxos:1.0:ip'}
        svi_dict = {}

        for c in root.iter():
            svi_intfs = (c.findall('groups:ROW_intf', svi_ns_map))
            for i in svi_intfs:
                subnet_list = []
                mask_list = []
                intf = i.find('groups:intf-name', svi_ns_map).text
                subnet = i.find('groups:subnet', svi_ns_map).text
                subnet_list.append(subnet)
                mask = i.find('groups:masklen', svi_ns_map).text
                mask_list.append(mask)
                #TODO: Get secondary IP addresses and masks

                svi_dict[intf] = {'subnets' : subnet_list, 'masks' : mask_list}
        #print "svi_dict: " , svi_dict
        return svi_dict


    @property
    def hsrp_dict(self):
        query = '''
                  <show>
                    <hsrp>
                        <detail/>
                    </hsrp>
                  </show>
                      '''
        ncdata = str(self.manager.get(('subtree', query)))
        root = ET.fromstring(ncdata)
        hsrp_ns_map = {'groups': 'http://www.cisco.com/nxos:1.0:hsrp_engine'}
        hsrp_dict = {}

        for c in root.iter():
            hsrp_intfs = (c.findall('groups:ROW_grp_detail', hsrp_ns_map))
            for i in hsrp_intfs:
                vip_list = []
                intf = i.find('groups:sh_if_index', hsrp_ns_map).text
                vip = i.find('groups:sh_vip', hsrp_ns_map).text
                vip_list.append(vip)
                mac = i.find('groups:sh_vmac', hsrp_ns_map).text

                # Check for secondary HSRP addresses
                secondaries = i.find('groups:TABLE_grp_vip_sec', hsrp_ns_map)
                if secondaries is not None:
                    for sec in secondaries.iter():
                        ips = sec.findall('groups:sh_vip_sec', hsrp_ns_map)
                        for ip in ips:
                            vip_list.append(ip.text)

                hsrp_dict[intf] = {'vmac': self.format_mac_address(mac),
                                   'vips': vip_list}
        return hsrp_dict

    def enable_vlan(self, vlanid, vlanname):
        confstr = self.cmd_vlan_conf_snippet % (vlanid, vlanname)
        confstr = self.exec_conf_prefix + confstr + self.exec_conf_postfix
        self.manager.edit_config(target='running', config=confstr)

    def enable_vlan_on_trunk_int(self, interface, vlanid):
        switchport = self.cmd_vlan_common % vlanid
        if '/' in interface:
            confstr = self.cmd_vlan_int_snippet % (interface, switchport)
        else:
            confstr = self.cmd_vlan_pc_snippet % (interface, switchport)
        confstr = self.exec_conf_prefix + confstr + self.exec_conf_postfix
        self.manager.edit_config(target='running', config=confstr)

    def enable_vlan_on_trunk_pc(self, interface, vlanid):
        switchport = self.cmd_vlan_common % vlanid
        confstr = self.cmd_vlan_pc_snippet % (interface,
                                              switchport)

        confstr = self.exec_conf_prefix + confstr + self.exec_conf_postfix
        self.manager.edit_config(target='running', config=confstr)

    def disable_vlan_on_trunk_int(self, interface, vlanid):
        confstr = self.cmd_no_vlan_int_snippet % (interface, vlanid)
        print confstr
        self.manager.edit_config(target='running', config=confstr)

    def build_xml(self, cmd):
        args = cmd.split(' ')
        xml = ""
        for a in reversed(args):
            xml = """<%s>%s</%s>""" % (a,xml,a)
        return xml

    def run_cmd(self, cmd):
        xml = self.build_xml(cmd)
        ncdata = str(self.manager.get(('subtree', xml)))
        return ncdata


    def migration_dict(self):
        """
        Merges Nexus.vlan_dict and Nexus.hsrp_dict

        """
        migrate_dict = {}
        #print self.svi_dict.values()
        for v in self.vlan_dict.keys():
            migrate_dict[v] = {'name': self.vlan_dict[v]}
            if 'Vlan{0}'.format(v) in self.hsrp_dict.keys():
                migrate_dict[v]['hsrp'] = self.hsrp_dict['Vlan{0}'.format(v)]
                migrate_dict[v]['hsrp'].update(self.svi_dict['Vlan{0}'.format(v)])
            else:
                migrate_dict[v]['hsrp'] = None
        #print migrate_dict
        return migrate_dict

    def cdp_neighbors(self):
        query = self.build_xml('show cdp neighbor')
        ncdata = str(self.manager.get(('subtree', query)))
        root = ET.fromstring(ncdata)
        neighbors = {}
        cdp_ns_map = {'mod': 'http://www.cisco.com/nxos:1.0:cdpd'}
        for c in root.iter(tag='{http://www.cisco.com/nxos:1.0:cdpd}ROW_cdp_neighbor_brief_info'):
            neighbor = c.find('mod:device_id', cdp_ns_map).text
            myintf = c.find('mod:intf_id', cdp_ns_map).text
            neigh_intf = c.find('mod:port_id', cdp_ns_map).text
            platform = c.find('mod:platform_id', cdp_ns_map).text
            neighbor = neighbor.split('(')[0]

            neighbors[neighbor] = {'local_intf': myintf,
                                   'neighbor_intf': neigh_intf,
                                   'platform': platform,
                                   }
        return neighbors