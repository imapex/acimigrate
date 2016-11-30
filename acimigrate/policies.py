#!/usr/bin/env python
import cobra.mit.access
import cobra.mit.naming
import cobra.mit.request
import cobra.mit.session
import cobra.model.fabric
from cobra.internal.codec.xmlcodec import toXMLStr

def commit(md, obj):
    """
    Commit a cobra configuration

    :param md: cobra MoDirectory object
    :param obj: cobra object to be commited
    :return:
    """
    c = cobra.mit.request.ConfigRequest()
    c.addMo(obj)
    return md.commit(c)

def create_10G_link_policy(md, name):
    topMo = md.lookupByDn('uni/infra')
    fabricHIfPol = cobra.model.fabric.HIfPol(topMo,
                                             ownerKey=u'',
                                             name=name,
                                             descr=u'',
                                             ownerTag=u'',
                                             autoNeg=u'on',
                                             speed=u'10G',
                                             linkDebounce=u'100')
    return commit(md, topMo)


def create_cdp_policy(md, name):
    """
    Creates a policy w/ CDP enabled given a name
    :param md: cobra.mit.access.MoDirectory object
    :param name: str name for the policy
    :return:
    """
    topMo = md.lookupByDn('uni/infra')
    cdpIfPol = cobra.model.cdp.ifpol.IfPol(topMo,
                                     name=name,
                                     adminSt=u'enabled'
                                     )
    return commit(md, topMo)


def create_lacp_policy(md, name):
    topMo = md.lookupByDn('uni/infra')
    lacpLagPol = cobra.model.lacp.LagPol(topMo,
                                         ownerKey=u'',
                                         name=name,
                                         descr=u'',
                                         minLinks=u'1',
                                         ctrl=u'fast-sel-hot-stdby,graceful-conv,susp-individual',
                                         maxLinks=u'16',
                                         mode=u'active',
                                         ownerTag=u'')
    return commit(md, topMo)

def create_vpc_policy_group(md, name):
    topMo = md.lookupByDn('uni/infra')

    # build the request using cobra syntax
    infraAccBndlGrp = cobra.model.infra.AccBndlGrp(topMo, lagT=u'node', name=name)
    infraRsHIfPol = cobra.model.infra.RsHIfPol(infraAccBndlGrp, tnFabricHIfPolName=u'10g-link-policy')
    infraRsLacpPol = cobra.model.infra.RsLacpPol(infraAccBndlGrp, tnLacpLagPolName=u'alpha_lacp_profile')
    infraRsCdpIfPol = cobra.model.infra.RsCdpIfPol(infraAccBndlGrp, tnCdpIfPolName=u'cdp-enabled')
    return commit(md, name)

ls = cobra.mit.session.LoginSession('http://10.94.140.72', 'admin', 'ins3965!')
md = cobra.mit.access.MoDirectory(ls)
md.login()

create_10G_link_policy(md, 'foo-link')
create_cdp_policy(md, 'foo-cdp')
create_lacp_policy(md, 'foo-lacp')