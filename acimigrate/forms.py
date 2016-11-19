#!/usr/bin/env python
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
import logging

logger = logging.getLogger(__name__)
logger.info('Loading Forms')


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
    n1i1 = StringField('n1i1')
    n1i2 = StringField('n1i2')
    n2i1 = StringField('n2i1')
    n2i2 = StringField('n2i2')
