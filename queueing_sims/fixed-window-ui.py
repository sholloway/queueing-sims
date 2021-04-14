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
# UI
# - Simulation Progress Bar based on Sim Duration
# - Inbound Request Rate
# - Total Requests Submitted
# - Max Threshold
# - Queue Depth
# - Total Requests Processed
###############################################################################

from rich import print
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.console import RenderGroup
from rich.progress import Progress
from rich.table import Table
import simpy

import math
from statistics import mean
import random

console = Console()

# The UOM for time in the simulation is 1 tick = 1 second.
MINUTE = 60 # 1 minute is 60 seconds
DURATION = 60 * 60 * 10 # Seconds * Minutes * Hours
WINDOW_SIZE = MINUTE * 1

# 500 requests/min => 8.333333333333334 Requests/sec
# 1 request = 0.12 Seconds
AVG_REQUEST_ARRIVAL_SPEED = 0.12
MAX_THRESHOLD = 100 # The maximum number of requests that can be processed in the window.

UI_REFRESH_RATE = 10 # The number of simulation ticks to update the UI.

metrics = {
  "current_sim_tick": 0,
  "requests_submitted": 0,
  "requests_processed": 0,
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

def update_ui(env, store, ui_layout, sim_progress, sim_task):
  while True:
    # 1. Update the simulation progress bar.
    previous_tick = metrics["current_sim_tick"]
    metrics["current_sim_tick"] = math.floor(env.now)
    sim_progress.update(sim_task, advance = metrics["current_sim_tick"] - previous_tick)
    # ui_layout["upper"].update(Panel.fit(sim_progress, title="Simulation Progress"))
    ui_layout["upper"].update(sim_progress)
    
    # 2. Determine the number of requests waiting to be processed.
    pending_requests_count = len(store.items)
    pending_requests_msg = f"Pending Requests Count: {pending_requests_count}"

    # 3. Collect the simulation's metrics.
    rate_exceeded_count = len(metrics["threshold_exceeded_wait_times"])
    avg_wait_time = 0
    if rate_exceeded_count > 0:
      avg_wait_time = mean(metrics["threshold_exceeded_wait_times"])


    # 5. Build a table to represent the metrics.
    sim_table = Table("Requests Submitted", "Requests Processed", "Rate Exceeded Count", "Avg Wait Time (s)", 
                      title="Simulation Metrics", box=box.SIMPLE_HEAVY)
    sim_table.add_row(str(metrics['requests_submitted']), 
      str(metrics['requests_processed']), 
      str(rate_exceeded_count), 
      str(avg_wait_time))

    # 6. Update the lower panel.
    ui_layout["lower"].update(RenderGroup(pending_requests_msg,sim_table))

    yield env.timeout(UI_REFRESH_RATE)

def create_ui_layout(sim_progress):
  layout = Layout()
  # Divide the "screen" in to two rows
  layout.split_column(
    Layout(name="upper"),
    Layout(name="lower")
  )
  layout["upper"].size = 1
  # layout["lower"].size = 6
  return layout

def main():
  sim_progress = Progress(expand=False)
  ui_layout = create_ui_layout(sim_progress)
  with Live(ui_layout, refresh_per_second=10, screen=True):
    sim_task = sim_progress.add_task("[red]Running Simulation...", total = DURATION)
    env = simpy.Environment()
    store = simpy.Store(env)
    env.process(generate_requests(env, AVG_REQUEST_ARRIVAL_SPEED, store))
    env.process(fixed_widow_processor(env, WINDOW_SIZE, MAX_THRESHOLD, store))
    env.process(update_ui(env, store, ui_layout, sim_progress, sim_task))
    env.run(until = DURATION)

  # After the simulation is done: Display the final UI
  print(ui_layout)

if __name__ == "__main__":
  main()