#!/usr/bin/env python3

import simpy

DURATION = 60 * 60 * 1 # Seconds * Minutes * Hours
MINUTE = 60

def ticker(env, speed):
  while True:
    print (f"Tick: {env.now}")
    yield env.timeout(speed)

env = simpy.Environment()
env.process(ticker(env, MINUTE))
env.run(until = DURATION)