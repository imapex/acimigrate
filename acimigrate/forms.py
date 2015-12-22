#!/usr/bin/env python
from flask_wtf import Form
from wtforms import StringField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired
import logging

logger = logging.getLogger(__name__)
logger.info('Loading Forms')

# class EPGForm(Form):
#     epg1 = SelectField('EPG1')
#     epg2 = SelectField('EPG2')

class ConfigureForm(Form):
    apic_hostname = StringField('Hostname')
    apic_username = StringField('Username')
    apic_password = PasswordField('Password')
    nexus_hostname = StringField('Hostname')
    nexus_username = StringField('Username')
    nexus_password = PasswordField('Password')
    nexus2_hostname = StringField('Hostname')
    nexus2_username = StringField('Username')
    nexus2_password = PasswordField('Password')

class MigrationForm(Form):
    tenant_name = StringField('tenant')
    app_name = StringField('app')
    layer3 = BooleanField('layer3')
    n1pc = StringField('n1pc')
    n2pc = StringField('n2pc')