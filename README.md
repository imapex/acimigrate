acimigrate is a flask application which will take configuration from a Nexus7000 or 9000 device, and replicate that configuration in
ACI policies where VLAN = EPG = BD

For L3 migration, HSRP must be configured.  acimigrate will handle a single HSRP group per SVI, however secondary HSRP addresses are supported.

NOTE:  this is for development purposes to be used as a starting point.
