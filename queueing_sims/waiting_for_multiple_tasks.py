#!/usr/bin/env python3

###############################################################################
# Modeling concurrent tasks.
###############################################################################

import simpy

import datetime  
import math
import random

DURATION = datetime.timedelta(hours=1) 
WINDOW = 60 # The number of simulation "ticks" a window is.
AVG_TASKS_PER_WINDOW = 10 # The number of tasks that is performed at the same time in a window.
TASK_RATE = 1.0 / AVG_TASKS_PER_WINDOW

def concurrent_work(env):
  count = 0
  while True:
    tasks = []
    concurrent_count = math.ceil(random.expovariate(TASK_RATE))
    for index in range(concurrent_count):
      count += 1 
      tasks.append(env.process(task(env, count)))
    yield env.all_of(tasks)
    print(f"Finished batch with {concurrent_count}")

def task(env, index):
  print(f"starting task {index}")
  task_time = math.ceil(random.expovariate(1000))
  yield env.timeout(task_time) # This waits for all tasks to finish.
  print(f"finished task {index}")

env = simpy.Environment()
env.process(concurrent_work(env))
env.run(until=DURATION.total_seconds())