#!/usr/bin/env python3

###############################################################################
# An rewrite of the nurse-example.py script using OO.
###############################################################################

import simpy
import random
import pandas as pd

from dataclasses import dataclass
from typing import NamedTuple
from statistics import mean

class Parameters(NamedTuple):
  patient_arrival_time: int
  avg_consult_time: int
  num_nurses: int
  sim_duration: int 
  number_of_runs: int

@dataclass
class Patient:
  id: int
  wait_time_for_nurse: int = 0

class NurseConsultationModel:
  def __init__(self, parameters, run_iteration) -> None:
    self.env = simpy.Environment()
    self.run_iteration = run_iteration
    self.parameters = parameters
    self.patient_counter = 0
    self.nurses = simpy.Resource(self.env, capacity = parameters.num_nurses)
    
    self.average_wait_time = 0
    self.results = pd.DataFrame()
    self.results["P_ID"] = []
    self.results["P_START_WAIT_FOR_NURSE_TIME"] = []
    self.results["P_STOP_WAIT_FOR_NURSE_TIME"] = []
    self.results["P_TOTAL_WAIT_FOR_NURSE_TIME"] = []
    self.results.set_index("P_ID", inplace = True)

  def run(self):
    self.env.process(self._generate_patient_arrivals())
    self.env.run(until = self.parameters.sim_duration)
    self.calculate_avg_waiting_time_to_see_a_nurse()

  def _generate_patient_arrivals(self):
    """Generate patients until the simulation ends."""
    while True:
      self.patient_counter += 1
      # Create a new patient.
      patient = Patient(self.patient_counter)

      # Have the patient start the clinic process.
      self.env.process(self._clinic_proccess(patient))

      # Determine how long until the next patient arrives.
      time_until_next_patient = random.expovariate( 1.0 / self.parameters.patient_arrival_time)
      yield self.env.timeout(time_until_next_patient)

  def _clinic_proccess(self, patient):
    """The process that this simulation is modeling."""
    patient_started_waiting = self.env.now
    print(f"Patient {patient.id} started waiting for a nurse at {patient_started_waiting}")
    
    with self.nurses.request() as req:
      # The patient waits until a nurse is free.
      yield req
      patient_finished_waiting = self.env.now
      print(f"Patient {patient.id} finished waiting at {patient_finished_waiting}")
      patient.wait_time_for_nurse = patient_finished_waiting - patient_started_waiting
      

      # Save metrics to the results dataframe.
      # Note: This is probably a horrible way to do this. 
      # I'm guessing it's better to build an array of NamedTuples or a Dict
      # and then building a dataframe from that in one go.
      metrics = pd.DataFrame({
        "P_ID": [patient.id],
        "P_START_WAIT_FOR_NURSE_TIME": [patient_started_waiting],
        "P_STOP_WAIT_FOR_NURSE_TIME": [patient_finished_waiting],
        "P_TOTAL_WAIT_FOR_NURSE_TIME": [patient.wait_time_for_nurse]
      })

      metrics.set_index("P_ID", inplace=True)
      self.results = self.results.append(metrics)

      # Deterimine how long the patient will spend with the nurse.
      time_with_nurse = random.expovariate(1.0 / self.parameters.avg_consult_time)
      yield self.env.timeout(time_with_nurse)

  def calculate_avg_waiting_time_to_see_a_nurse(self):
    self.average_wait_time = self.results["P_TOTAL_WAIT_FOR_NURSE_TIME"].mean()

class RunResult(NamedTuple):
  run: int
  average_wait_time: int

def main():
  parameters = Parameters(5, 6, 1, 120, 10)
  run_results = []
  for sim_run in range(parameters.number_of_runs):
    run = sim_run + 1
    print(f"Run {run} of {parameters.number_of_runs} -----------------------------------------------------------")
    sim = NurseConsultationModel(parameters, run)
    sim.run()
    
    run_results.append(RunResult(run, sim.average_wait_time))
    waiting_times = list((x.average_wait_time for x in run_results))
    avg_waiting_time = mean(waiting_times)
    print(f"The average time spent waiting for a nurse is {avg_waiting_time} minutes.")

if __name__ == "__main__":
  main()