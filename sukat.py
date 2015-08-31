#!/usr/bin/env python
from __future__ import print_function
import os
import subprocess
import sys
import time
import ConfigParser 
from boto.ec2.connection import EC2Connection
#Borrows from Takaitra: http://www.takaitra.com/posts/384

def print_dot():
  print ('.', end='',)
  sys.stdout.flush()

config = ConfigParser.ConfigParser()
config.read('sukat.cfg')
# Create the EC2 instance
print ('Starting an EC2 instance of type {0} with image {1}'.format(config.get('Sukat', 'instance_type'), config.get('Sukat', 'image')))
conn = EC2Connection(config.get('Sukat', 'ec2_key'), config.get('Sukat', 'ec2_secret'))
reservation = conn.run_instances(config.get('Sukat', 'image'), instance_type=config.get('Sukat', 'instance_type'), key_name=config.get('Sukat', 'key_name'), placement=config.get('Sukat', 'zone'), security_groups=[config.get('Sukat', 'security_groups')])

instance = reservation.instances[0]
time.sleep(10) # Sleep so Amazon recognizes the new instance
while not instance.update() == 'running':
  time.sleep(3) # Let the instance start up
print ('Started the instance: {0}'.format(instance.dns_name))
print ('Starting ssh with tunnel port {0}'.format(config.get('Sukat', 'ssh_dynamic_port')), end="")
cmd = "ssh -o StrictHostKeyChecking=no -i {0} -CNfD {1} ubuntu@{2}".format(config.get('Sukat', 'key_path'), config.get('Sukat', 'ssh_dynamic_port'), instance.dns_name)

process = None
fnull = open(os.devnull, 'w')
try:
  while True:
    process = subprocess.Popen(cmd, shell=True, stdout=fnull, stderr=fnull)
    while process.poll() == None:
      time.sleep(0.5)
      print_dot()
    if int(process.poll()) == 255:
      #Error case for SSH connection errors, which are typical before the instance is ready
      time.sleep(0.5)
      print_dot()
      next
    else:
      break
  raw_input("\nEverything is ready. Press enter once you don't need the tunnel anymore.")
except Exception as e:
  print ("Something went wrong: " + str(e))
finally:
  print ('Terminating instance')
  instance.terminate()
print ('Done')

