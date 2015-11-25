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
    apic_hostname = StringField('hostname')
    apic_username = StringField('username')
    apic_password = PasswordField('password')
    nexus_hostname = StringField('hostname')
    nexus_username = StringField('username')
    nexus_password = PasswordField('username')

class MigrationForm(Form):
    tenant_name = StringField('tenant')
    app_name = StringField('app')
    layer3 = BooleanField('layer3')