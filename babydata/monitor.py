#!/usr/bin/python3

import os
from syslog import syslog
from scapy.all import *
from urllib.parse import urlencode
from urllib.request import urlopen
from time import time

class Action:
   def __init__(self, kind):
      self.kind = kind
   def __enter__(self):
      self.result = urlopen(os.getenv("FORM"), urlencode({os.getenv("ENTRY"): self.kind}).encode('ascii'))
      return self.result
   def __exit__(self, type, value, traceback):
      self.result.close()

(FEED,WET_DIAPER,POOP_DIAPER,AWAKE,ASLEEP) = ("Feed","Wet Diaper","Poop Diaper","Awake","Asleep")

def default_action(pkt, name):
   syslog("ARP Probe from: %s (%s): No action taken." % (pkt[ARP].hwsrc, name))

def rate_limit(timeout, func):
   last = 0
   def limiter(pkt, name):
      nonlocal last
      now = time()
      if (last + timeout) > now:
         syslog("%s action blocked, rate limited. Unblocked in %d seconds." % (name, timeout - (now - last),))
      else:
         last = now
         func(pkt, name)
   return limiter

def make_action(kind):
   def action(pkt, name):
      with Action(kind) as result:
         if result.getcode() != 200:
            syslog("Button %s pressed, error submitting form: %s" % (name, result.info()))
         else:
            syslog("Button %s pressed, recorded %s." % (name, kind))
   return action

MAP = defaultdict(lambda: ('unknown', default_action))
MAP['f0:27:2d:e5:48:f0'] = ("Glad", rate_limit(60, make_action(WET_DIAPER)))
MAP['f0:27:2d:1e:dc:ed'] = ("Cottonelle", rate_limit(60, make_action(POOP_DIAPER)))
MAP['a0:02:dc:75:19:92'] = ("Greenies", rate_limit(60, make_action(FEED)))
MAP['a0:02:dc:8a:23:29'] = ("Revitalift 0", rate_limit(60, make_action(AWAKE)))
MAP['74:75:48:12:b9:56'] = ("Revitalift 1", rate_limit(60, make_action(ASLEEP)))

def display_arp(pkt):
   (name, action) = MAP[pkt[ARP].hwsrc]
   return action(pkt, name)

# filter - https://en.wikipedia.org/wiki/Berkeley_Packet_Filter
#sniff(prn=display_arp, filter="arp and src host 0.0.0.0", store=0, count=0)
# a0:02:dc:8a:23:29 appears to remember its ip, so can't filter on src host 0.0.0.0
sniff(prn=display_arp, filter="arp", store=0, count=0)
