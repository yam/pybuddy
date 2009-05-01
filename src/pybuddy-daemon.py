#!/usr/bin/python
#
# pybuddy
# python ibuddy daemon - http://code.google.com/p/pybuddy
#
# Jose.Carlos.Luna@gmail.com
# luis.peralta@gmail.com
#
# Most of the code comes from http://cuntography.com/blog/?p=17
# Which is based on http://scott.weston.id.au/software/pymissile/

import sys
import socket
import os
import pwd
import logging
from ConfigParser import RawConfigParser

from pybuddy import *
from macro import *
from config import *

#######################################
# MAIN program
#######################################
if __name__ == "__main__":

  log = logging.getLogger('pybuddy')

  #Default config
  config = RawConfigParser(
    { 'port': 8888,
      'address': '127.0.0.1',
      'user': 'nobody',
      'loglevel': 'info',
      'logfile': 'console',
      'usbproduct': 0002,
      }
    )
  config._sections = {'network':{}, 'system':{}}

  config_files = [ "~/.pybuddy.cfg",
                   "/etc/pybuddy/pybuddy.cfg",
                   "/usr/local/etc/pybuddy.cfg"
                   ]

  #Parse config
  if len(sys.argv) > 1:
    config_files.append(sys.argv[1])
  
  config_read = config.read(config_files)

  if config.get("system", "logfile") != "console":
    logging.basicConfig(
      filename=config.get("system", "logfile"),
      format='%(asctime)s %(levelname)-8s %(message)s',
      )
  else:
    logging.basicConfig(
      stream=sys.stderr,
      format='%(asctime)s %(levelname)-8s %(message)s',
      )


  if config.get("system", "loglevel") == "debug":
    log.setLevel(logging.DEBUG)
  elif config.get("system", "loglevel") == "info":
    log.setLevel(logging.INFO)


  if config_read:
    log.info("Read config file: %s", config_read[0])


  #Initialize device
  log.info("Starting search...")
  try:
    buddy=BuddyDevice(0, int(config.get("system", "usbproduct")))
  except NoBuddyException, e:
    log.error("Not found!")
    sys.exit(1)


  #Daemonize
  log.info("Starting daemon...")
  if os.fork()==0:
    os.setsid()
  else:
    sys.exit(0)

  #Create server socket
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind((config.get("network", "address"), int(config.get("network", "port"))))

  #Drop privileges
  try:
    uid = pwd.getpwnam(config.get("system", "user"))[2]
  except KeyError:
    log.error("Username %s not found, exiting...", config.get("system", "user"))
    sys.exit(1)
  os.setuid(uid)

  #Main message loop
  while 1:
    try:
      message, address = s.recvfrom(8192)
      log.debug("Got data from %s", address)
      decode_buddy(buddy, message)

    except (KeyboardInterrupt, SystemExit):
      raise

  
