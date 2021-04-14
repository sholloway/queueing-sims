#!/usr/bin/env python3

###############################################################################
# This is a simple example based on this video: 
# https://www.youtube.com/watch?v=jXDjrWKcu6w
# 
# In this example, patients go through a registration process before waiting to 
# see a nurse.
#
# Flow
# People Arriving at the Office -> Registration -> Nurse -> Sink
###############################################################################

import simpy
import random

# Configure the module's parameters.
# Time is in minutes.
AVG_PATIENT_ARRIVAL_TIME = 8
AVG_REGISTRATION_TIME = 2
AVG_EVALUATION_TIME = 5
NUM_RECPTIONISTS = 1
NUM_NURSES = 1

# Patient arrival builder function.
# Responsible for creating new patients.
def patient_builder(env, patient_arrival_time, avg_register_time, 
                    avg_evaluation_time, receptionist, nurse):
  p_id = 1

  # Create patients until the program ends.
  while True:
    # Create an instance of an activity generator function.
    p = activity_generator_ed(env, avg_register_time, avg_evaluation_time, 
                                receptionist, nurse, p_id)

    # Run the activity for this patient.
    env.process(p)

    # Determine the sample time until the next patient arrives at the office.
    # Using exponential distribution.
    # Is this the same as Poisson 
    time_until_next_patient = random.expovariate(1.0 / patient_arrival_time)

    # Wait until the time has passed.
    yield env.timeout(time_until_next_patient)

    p_id += 1 

def activity_generator_ed(env, avg_register_time, avg_evaluation_time, 
                                receptionist, nurse, p_id):
  time_entered_queue_for_registration = env.now

  # Stand in line for the receptionist.
  with receptionist.request() as req:
    # Wait for the receptionist
    yield req

    time_left_queue_for_registration = env.now
    time_in_queue_for_registration = time_left_queue_for_registration - time_entered_queue_for_registration
    print(f"Patient {p_id} waited for registration for {time_in_queue_for_registration} minutes")

    # Determine how long it takes to register this patient.
    patient_registration_time = random.expovariate(1.0 / avg_register_time)

    # Spend time performing the patient registration process.
    yield env.timeout(patient_registration_time)

  # After registration process is complete. The patient waits to see the nurse.
  time_entered_queue_to_see_a_nurse = env.now

  # Wait for a nurse.
  with nurse.request() as req:
    # Wait until a nurse is available.
    yield req

    time_left_queue_for_a_nurse = env.now
    time_spent_in_queue_for_a_nurse = time_left_queue_for_a_nurse - time_entered_queue_to_see_a_nurse
    print(f"Patient {p_id} waited for a nurse for {time_spent_in_queue_for_a_nurse} minutes")

    # Determine how long the patient spends with a nurse.
    patient_evaluation_time = random.expovariate(1.0/avg_evaluation_time)

    # Spend time doing the patient evaluation.
    yield env.timeout(patient_evaluation_time)

def main():
  # Setup the simulation environment
  env = simpy.Environment()

  # Setup the resources
  receptionists = simpy.Resource(env, capacity=NUM_RECPTIONISTS)
  nurses = simpy.Resource(env, capacity=NUM_NURSES)

  # Register the creation of the patient arrivals
  env.process(patient_builder(env, AVG_PATIENT_ARRIVAL_TIME,AVG_REGISTRATION_TIME, AVG_EVALUATION_TIME, receptionists, nurses))

  # Run the simulation
  env.run(until=120)

if __name__ == "__main__":
  main()