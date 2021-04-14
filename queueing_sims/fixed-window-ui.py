#!/usr/bin/env python3

###############################################################################
# A simulation of a fixed window rate limiter.
# For a window of time (e.g. 60 seconds) cap requests at a maximum threshold.
# All requests that exceed the threshold go in a queue.
#
# This is an extension of the fixed-window.py simulation. It adds:
# - The ability to track the queue depth.
# - A simple CLI UI for observing the simulation behavior.
#
# Considerations
# - A warm up period?..
# - Migrate to OO implementation.
#
# UI
# - Simulation Progress Bar based on Sim Duration
# - Inbound Request Rate
# - Total Requests Submitted
# - Max Threshold
# - Queue Depth
# - Total Requests Processed
###############################################################################

import simpy
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

import math
from statistics import mean
import random

# The UOM for time in the simulation is 1 tick = 1 second.
MINUTE = 60 # 1 minute is 60 seconds
DURATION = 60 * 60 * 1 # Seconds * Minutes * Hours
WINDOW_SIZE = MINUTE * 1

# 500 requests/min => 8.333333333333334 Requests/sec
# 1 request = 0.12 Seconds
AVG_REQUEST_ARRIVAL_SPEED = 0.12
MAX_THRESHOLD = 500 # The maximum number of requests that can be processed in the window.


metrics = {
  "requests_submitted": 0,
  "requests_processed":0,
  "threshold_exceeded_wait_times": []
}

def generate_requests(env, avg_arrival_speed, store):
  while True:
    # print("Generator: Request Submitted")
    store.put(1) #Generate a request.
    metrics['requests_submitted'] += 1
    wait_for_next_request_time = random.expovariate(avg_arrival_speed)
    yield env.timeout(avg_arrival_speed)

def fixed_widow_processor(env, window_size, max_threshold, store):
  """
  Consumes resources from a store, but limits the rate based on a fixed window.
  """
  window_start, window_end = find_window(env.now, window_size)
  request_counter = 0 # Tracks the number of requests in the current window.
  while True:
    # Process a request
    # This will wait here until something is actually available.
    yield store.get()

    request_counter += 1
    now = env.now
    metrics["requests_processed"] += 1

    # Has the window ended? If so, calculate the new window and reset the counter.
    if now > window_end:
      request_counter = 0
      window_start,window_end = find_window(now, window_size)

    # Has the maximum threshold been exceeded? If so, wait until the window is over.
    if request_counter > max_threshold:
      request_counter = 0
      wait = window_end - now
      if (wait > 0):
        # print(f"Subscriber: Rate exceeded, resting for {wait}")
        metrics["threshold_exceeded_wait_times"].append(wait)
        yield env.timeout(wait)

def find_window(now: int, window_size: int ) -> tuple[int, int]:
  offset, extra = divmod(math.floor(now), window_size)
  window_start = offset * window_size 
  window_end = window_start + window_size 
  return window_start, window_end

def main():
  env = simpy.Environment()
  store = simpy.Store(env)
  env.process(generate_requests(env, AVG_REQUEST_ARRIVAL_SPEED, store))
  env.process(fixed_widow_processor(env, WINDOW_SIZE, MAX_THRESHOLD, store))
  env.run(until = DURATION)

  print(f"Requests Submitted: {metrics['requests_submitted']}")
  print(f"Requests Processed: {metrics['requests_processed']}")

  rate_exceeded_count = len(metrics["threshold_exceeded_wait_times"])
  print(f"Rate Exceeded Count: {rate_exceeded_count}")
  if rate_exceeded_count > 0:
    avg_wait_time = mean(metrics["threshold_exceeded_wait_times"])
    print(f"Avg Wait Time: {avg_wait_time}")

  for i in metrics["threshold_exceeded_wait_times"]:
    print(i)

if __name__ == "__main__":
  main()