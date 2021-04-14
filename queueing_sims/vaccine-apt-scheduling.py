#!/usr/bin/env python3

###############################################################################
# This is a discrete event simulation of vaccine appointment scheduling.
# 
# The processes is:
# 1. Potential candidates arrive to the site.
# 2. They are placed in a FIFO queue if the site is at capacity.
# 3. Through the queue, a canidate goes through the registration process. 
#     - If they're above a certain age they qualify and are notified they can 
#       schedule an appointment.
#     - If they're not, they exit.
# 4. If they do register an email is sent and they can enter the scheduling process.
# 5. After the scheduling process they leave the site.
#
# Simulation Areas of Interest
# - Number of users on the site at any given time.
# - The min, max, and avg wait time to register.
# - The number of people scheduling.
# - Total Registered
# - Total Qualified
# - Total Scheduled
#
# Model Details
# - Unit of Time: Minutes
# - Recommended number of runs to average across: ???
"""
Thoughts on modeling.
Everything we do in regards to performance is at the minute level. 
Perhaps at each minute, the candidate generator should create X number of 
candiates. X can be specified as a distribution. The average could be 500 for example.

A queue has an inflow and out flow. 

Question: 
If it takes X seconds to create an article, and y seconds to publish it, 
how long will it take to create 30 M articles?
"""
###############################################################################

import simpy
import random

from typing import NamedTuple

class ModelParameters(NamedTuple):
  # Simulation Parameters
  number_of_runs: int = 1 
  sim_duration: int = 60 * 60 * 2 # Seconds * Minutes * Hours

  # Waiting Room Parameters
  candidate_arrival_time: int = 5 # The average amount of time until the next users arrives.
  max_outflow_threshold: int = 10 # Number of users that can leave the waiting room per minute.
  
  # Registration Parameters
  avg_registration_time: int = 5 # Number of minutes spent registering.
  age_threshold: int = 18 # The minimum age the candidate must be to qualify.
  percentage_of_recipeints_that_quit: int = 5 # The percentage of qualified recipients that register but don't schedule.

  #Scheduling Parameters
  avg_scheduling_time: int = 5 # Number of minutes spent registering.

class Candidate:
  def __init__(self, id) -> None:
    self.id = id


class WaitingRoom:
  """
  Leverages a fixed window rate limiter.
  A counter is applied for the window duration. If the number of requests is 
  greater than the max_outflow, then the inbound request is added to a queue.
  """
  def __init__(self, env, window_size:int, max_outflow: int) -> None:
    self.env = env
    self.window_size = window_size
    self.max_outflow = max_outflow

    # Perhaps use 2 stores. 1 for inbound, 1 for outbound.
    # If the rate is low append to outbound.
    # If the rate is high append to inbound
    self.store = simpy.Store(self.env)

  def waiting(self, candidate: Candidate) -> None:
    # This is where I need to put the logic for waiting in the queue.
    print(f"Candidate {candidate.id} is entering the waiting room.")
    
    yield self.env.timeout(1) # What should this be?
    self.store.put(candidate)

  def enter(self, candidate: Candidate) -> None:
    self.env.process(self.waiting(candidate))

  def exit(self):
    """Returns a candidate if one is available."""
    return self.store.get()

class VaccineModel:
  def __init__(self, parameters: ModelParameters, run_iteration: int) -> None:
    self.env = simpy.Environment()
    self.parameters = parameters
    self.run_iteration = run_iteration
    self.candidate_counter = 0

    # Create the resources...
    self.waiting_room = WaitingRoom(self.env, self.parameters.max_outflow_threshold)

  def run(self) -> None:
    ## Set up the procceses
    self.env.process(self._enforce_candidates_waiting_room())
    self.env.process(self._user_registration())
    self.env.run(until = self.parameters.sim_duration)

  def _enforce_candidates_waiting_room(self) -> None:
    """Creates candidates and has them enter the waiting room."""
    while True:
      # A new candiate arrives
      self.candidate_counter += 1
      self.waiting_room.enter(Candidate(self.candidate_counter))
      
      # Determine the arrival rate for the next candiate using an exponential distribution.
      next_candidate_arrival_time = random.expovariate(1.0 / self.parameters.candidate_arrival_time)
      yield self.env.timeout(next_candidate_arrival_time)

  def _user_registration(self) -> None:
    """Canidates leave the waiting room and go through the registration process"""
    while True:
      candidate = yield self.waiting_room.exit()
      print(f"Candidate {candidate.id} has started registration.")


def main():
  parameters = ModelParameters()
  run_results = []
  for sim_run in range(parameters.number_of_runs):
    iteration = sim_run + 1
    sim = VaccineModel(parameters, iteration)
    sim.run()

if __name__ == "__main__":
  main()