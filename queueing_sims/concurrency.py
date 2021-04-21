#!/usr/bin/env python3

###############################################################################
# Modeling concurrent tasks.
###############################################################################

import simpy

import datetime  
import math
import random

DURATION = datetime.timedelta(hours=1) 
CURRENCY_FACTOR = 5 
AGENT_WAIT_TIME_MIN = 1
AGENT_WAIT_TIME_MAX = 10

def agent(env, agent_id):
  while True:
    print(f"Agent {agent_id} working.")
    time_to_wait = random.randint(AGENT_WAIT_TIME_MIN, AGENT_WAIT_TIME_MAX)
    yield env.timeout(time_to_wait)

env = simpy.Environment()

for agent_id in range(CURRENCY_FACTOR):
  env.process(agent(env, agent_id))

env.run(until=DURATION.total_seconds())
