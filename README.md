acimigrate is a flask application which will take configuration from a Nexus7000 or 9000 device, and replicate that configuration in
ACI policies where VLAN = EPG = BD

The migration high level logic is as follows

* Interrogate the legacy nexus switches for VLAN/SVI information including name, subnet/gateway, HSRP VMAC
* Configure these as EPG's with a seperate bridge domain per EPG
* Create a contract allowing communication between all of the EPG's migrated. This simulates a common
  deployment scenario (no access-lists present at default gateway)
* Migrate L3 information (optional based on user input) should the default gateways be moved to the fabric
* Identify and unused port channel number on the Nexus side
* Configure selected physical interfaces into a VPC
* Allow migration VLAN's over the trunk


# Installation

The easiest way to use the acimigrate application is to pull the latest docker image from docker hub

```
docker run -d -p 8000:8000 imapex/acimigrate
```

That's it!  Launch your browser and head over to [http://127.0.0.1:8000/]

# Usage

Follow the on-screen wizard to gather the required input, then watch acimigrate do it's magic!

## Assumptions / Prereq

* VPC aggregation topology
  This project assumes that you have a traditional 7K/5K aggregation/access design with VPC's between the 7K and 5K

* HSRP is configured on SVI's

  acimigrate will use the HSRP VMAC address for configuration of the BD mac address in ACI.
  **NOTE:** acimigrate will handle a single HSRP group per SVI, however secondary HSRP addresses are supported.

* Layer 3 migration

  If L3 gateways are to be migrated to the fabric, it is assumed that the External L3Out's have already been configured

* NX-OS device w/ XML API enabled - the 7K aggregation switches must have the XML API enabled

  More details can be found at http://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus7000/sw/programmability/guide/b_Cisco_Nexus_7000_Series_NX-OS_Programmability_Guide/b_Cisco_Nexus_7000_Series_NX-OS_Programmability_Guide_chapter_0110.html

* LACP enabled

  Currently we assume that LACP is already in use on the Nexus 7000.


# TODO / Roadmap

* Complete provisioning of ACI side of migration VPC w/ cleanup
* Better error checking/handling
* Packaging for ACI App Center
