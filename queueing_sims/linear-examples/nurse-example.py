#!/usr/bin/env python3

###############################################################################
# This is a simple example based on this video: 
# https://www.youtube.com/watch?v=jXDjrWKcu6w
# 
# The simulation is simply a group of patients waiting to see a nurse.
# There is only 1 nurse. 
# The nurse can only see a single patient at a time.
# Patients wait in a proverbial waiting room until their turn.
# The nurse sees patients in the order they arrived (FIFO).
# Patients arrive following an exponential (posson) distribution.
# The amount of time an appointment takes also follows an exponential distribution.
###############################################################################

import simpy
import random

# Patient arrival builder function.
# Responsible for creating new patients.
def patient_builder(env, patient_arrival_time, mean_consult, nurse):
  p_id = 1

  # Create patients until the program ends.
  while True:
    # Create an instance of an activity generator function.
    ca = consultation_activity(env, mean_consult, nurse, p_id)

    # Run the activity for this patient.
    env.process(ca)

    # Determine the sample time until the next patient arrives at the office.
    # Using exponential distribution.
    # Is this the same as Poisson 
    time_until_next_patient = random.expovariate(1.0 / patient_arrival_time)

    # Wait until the time has passed.
    yield env.timeout(time_until_next_patient)

    p_id += 1 

def consultation_activity(env, mean_consult, nurse, p_id):
  time_entered_queue_for_nurse = env.now
  print(f"Patient: {p_id} entered queue at {time_entered_queue_for_nurse}.")

  # Request a consultation with the nurse.
  with nurse.request() as req:
    # Wait until the request can be met.
    # The nurse resource will automatically start 
    # the generator function back up when the resource capacity
    # is available.
    yield req

    # Calculate the time the patient was waiting.
    time_left_queue_for_nurse = env.now
    print(f"Patient: {p_id} left queue at {time_left_queue_for_nurse}.")
    time_in_queue = time_left_queue_for_nurse - time_entered_queue_for_nurse
    print(f" Patient: {p_id} waited for {time_in_queue}")

    # Determine how long the consultation takes.
    consultation_time = random.expovariate(1.0 / mean_consult)

    # Wait until the consultation is over.
    yield env.timeout(consultation_time)

# Setup the simulation environment.
env = simpy.Environment()

# Setup the resources. 
# In this example, there is only one nurse.
# The nurse can only consult with one person at a time,
# so the resource capcity is set to 1.
nurse = simpy.Resource(env, capacity=1)


patient_arrival_time = 5
mean_consult_time = 6

# Register the creation of the patient arrivals
env.process(patient_builder(env, patient_arrival_time, mean_consult_time, nurse))

# Run the simulation
env.run(until=120)