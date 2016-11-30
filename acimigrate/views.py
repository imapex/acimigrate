#!/usr/bin/env python
from functools import wraps
from flask import render_template, request, redirect
from forms import ConfigureForm, MigrationForm
from acimigrate import app
from acimigrate.Devices import Nexus, APIC
from tasks import migrate
import logging

logger = logging.getLogger(__name__)
logger.info('Loading Views')
configured = False

apic = None
nexus = None
nexus2 = None


@app.route("/setup", methods=('GET', 'POST'))
def setup():
    form = ConfigureForm()
    return render_template('phase1.html', form=form)


def configuration_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not configured:
            return redirect('/setup')
        else:
            return f(*args, **kwargs)
    return decorated_function


@app.route("/", methods=['GET', 'POST'])
@configuration_required
def index():
    return render_template('phase1.html')


@app.route("/doconfigure", methods=('GET', 'POST'))
def updateconfig():
    global apic, nexus, nexus2, configured
    form = MigrationForm()
    args = dict()
    print request.form
    args['apic_hostname'] = request.form['apic_hostname']
    args['apic_username'] = request.form['apic_username']
    args['apic_password'] = request.form['apic_password']
    args['apic_url'] = 'http://' + args['apic_hostname']

    args['nexus_hostname'] = request.form['nexus_hostname']
    args['nexus_username'] = request.form['nexus_username']
    args['nexus_password'] = request.form['nexus_password']

    args['nexus2_hostname'] = request.form['nexus2_hostname']
    args['nexus2_username'] = request.form['nexus2_username']
    args['nexus2_password'] = request.form['nexus2_password']

    # Get credentials from form
    nexus = Nexus(args['nexus_hostname'],
                  args['nexus_username'],
                  args['nexus_password'])
    nexus2 = Nexus(args['nexus2_hostname'],
                   args['nexus2_username'],
                   args['nexus2_password'])
    apic = APIC(args['apic_url'],
                args['apic_username'],
                args['apic_password'])
    configured = True

    # TODO - move below to a function somewhere else
    aci_switch_dict = {}
    aci_switches = apic.list_switches()
    for aci_switch in aci_switches:
        if aci_switch.role == 'leaf':
            switch_int_list = apic.get_switch_interfaces(aci_switch.node)
            int_list = []
            for int in switch_int_list:
                int_list.append(int.attributes['id'])
            aci_switch_dict[aci_switch.name] = int_list

    # print aci_switch_dict
    return render_template('phase2.html',
                           data=nexus.migration_dict()['vlans'],
                           form=form,
                           n1interfaces=nexus.free_interfaces(),
                           n2interfaces=nexus2.free_interfaces(),
                           aci_switch_list=aci_switch_dict,
                           )


@app.route("/migrate", methods=('GET', 'POST'))
def domigrate():
    global nexus, apic, nexus2
    print request.form
    if 'layer3' in request.form:
        l3 = True
    else:
        l3 = False
    TENANT_NAME = request.form['tenant_name']
    APP_NAME = request.form['app_name']
    # Get Nexus 1 interfaces from form
    n1i1 = request.form['n1i1']
    n1i2 = request.form['n1i2']
    n1_int_list = [n1i1, n1i2]

    # Get Nexus 2 interfaces from form
    n2i1 = request.form['n2i1']
    n2i2 = request.form['n2i2']
    n2_int_list = [n2i1, n2i2]
    # TODO - remove repetes from n1_int_list and n2_int_list
    # TODO - need to add ACI interfaces from for and pass to migration function
    leafs = request.form.getlist('leaves')
    print leafs
    aci_interface_dict = {}
    for leaf in leafs:
        int1 = request.form.getlist('{}-int1'.format(leaf))
        int2 = request.form.getlist('{}-int2'.format(leaf))
        aci_interface_dict[leaf] = [int1, int2]


    print "aci inteface dict {}".format(aci_interface_dict)

    apic.migration_tenant(TENANT_NAME, APP_NAME)
    apic.aci_interface_dict = aci_interface_dict
    result = migrate(nexus,
                     apic,
                     nexus2,
                     auto=True,
                     layer3=l3,
                     # TODO Nexus Interface lists should be attached to Nx object??
                     n1_int_list=n1_int_list,
                     n2_int_list=n2_int_list,
                     )
    return render_template('completed.html', data=result)
