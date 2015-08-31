#!/usr/bin/env python
import os
from boto.ec2.connection import EC2Connection
import time
import ConfigParser
 
config = ConfigParser.ConfigParser()
config.read('sukat.cfg')
# Create the EC2 instance
print 'Starting an EC2 instance of type {0} with image {1}'.format(config.get('Sukat', 'instance_type'), config.get('Sukat', 'image'))
conn = EC2Connection(config.get('Sukat', 'ec2_key'), config.get('Sukat', 'ec2_secret'))
reservation = conn.run_instances(config.get('Sukat', 'image'), instance_type=config.get('Sukat', 'instance_type'), key_name=config.get('Sukat', 'key_name'), placement=config.get('Sukat', 'zone'), security_groups=[config.get('Sukat', 'security_groups')])

instance = reservation.instances[0]
time.sleep(10) # Sleep so Amazon recognizes the new instance
while not instance.update() == 'running':
  time.sleep(3) # Let the instance start up
print 'Started the instance: {0}'.format(instance.dns_name)
print 'Starting ssh, exit it to kill instance'
cmd = "ssh -o StrictHostKeyChecking=no -i {0} -CD {1} ubuntu@{2}".format(config.get('Sukat', 'key_path'), config.get('Sukat', 'ssh_dynamic_port'), instance.dns_name)
while os.WEXITSTATUS(os.system(cmd)) == 255:
  time.sleep(1)
print 'Terminating instance'
instance.terminate()
print 'Done'
