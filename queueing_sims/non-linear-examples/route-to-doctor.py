#!/usr/bin/env python3

###############################################################################
# This is a simple example based on this video: 
# https://www.youtube.com/watch?v=jXDjrWKcu6w
# 
# In this example, patients go through a registration process before waiting to 
# see a nurse.
#
# Flow
# People Arriving at the Office -> Registration -> Nurse (choice) -> 20% -> Specialist Doctor
#                                                                 -> 80% -> General Practitioner Doctor
###############################################################################

import simpy
import random

# Configure the module's parameters.
# Time is in minutes.
AVG_PATIENT_ARRIVAL_TIME = 8
AVG_REGISTRATION_TIME = 2
AVG_EVALUATION_TIME = 5
AVG_SPECIALIST_EVALUATION_TIME = 8
AVG_GP_EVALUATION_TIME = 5

NUM_RECPTIONISTS = 1
NUM_NURSES = 1
NUM_SPECIALISTS = 1
NUM_GP_DOCTORs = 1

# Patient arrival builder function.
# Responsible for creating new patients.
def patient_builder(env, patient_arrival_time, avg_register_time, 
                    avg_evaluation_time, avg_specialist_evaluation_time, 
                    avg_gp_eval_time, receptionist, nurse, 
                    specialist, gp_doctor):
  p_id = 1

  # Create patients until the program ends.
  while True:
    # Create an instance of an activity generator function.
    p = activity_generator(env, avg_register_time, avg_evaluation_time, 
                            avg_specialist_evaluation_time, avg_gp_eval_time,
                            receptionist, nurse,specialist, gp_doctor, p_id)

    # Run the activity for this patient.
    env.process(p)

    # Determine the sample time until the next patient arrives at the office.
    # Using exponential distribution.
    # Is this the same as Poisson 
    time_until_next_patient = random.expovariate(1.0 / patient_arrival_time)

    # Wait until the time has passed.
    yield env.timeout(time_until_next_patient)

    p_id += 1 

def activity_generator(env, avg_register_time, avg_evaluation_time, 
                            avg_specialist_evaluation_time, avg_gp_eval_time,
                            receptionist, nurse,specialist, gp_doctor, p_id):
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

  # Determine which type of doctor the patient will see.
  # Use a uniform distribion to assign a probability to the patient.
  doctor_type_probability = random.uniform(0, 1)

  if doctor_type_probability < 0.2: 
    # 20% of patients see the ACU doctor.
    time_entered_queue_for_specialist = env.now

    with specialist.request() as req:
      # Wait until the specialist is available.
      yield req      
      time_done_waiting_to_see_specialist = env.now
      time_spent_waiting_for_specialist = time_done_waiting_to_see_specialist - time_entered_queue_for_specialist
      print(f"Patient {p_id} waited to see a specialist for {time_spent_waiting_for_specialist} minutes after seeing the nurse.")

      # Determine how long this patient will spend with the specialist.
      evaluation_time = random.expovariate(1.0/avg_specialist_evaluation_time)
      yield env.timeout(evaluation_time)
  else: # 80% of patients see the general practitioner
    #wait for the general practitioner
    time_started_waiting_for_gp = env.now
    with gp_doctor.request() as req:
      yield req # wait until the GP is available.
      time_done_waiting_to_see_gp = env.now
      time_spent_waiting_for_gp = time_done_waiting_to_see_gp - time_started_waiting_for_gp
      print(f"Patient {p_id} waited to see a general practitioner for {time_spent_waiting_for_gp} minutes after seeing the nurse.")
      
      # Determine how long this patient will spend with the specialist.
      evaluation_time = random.expovariate(1.0/avg_gp_eval_time)
      yield env.timeout(evaluation_time)


def main():
  # Setup the simulation environment
  env = simpy.Environment()

  # Setup the resources
  receptionists = simpy.Resource(env, capacity=NUM_RECPTIONISTS)
  nurses = simpy.Resource(env, capacity=NUM_NURSES)
  specialists = simpy.Resource(env, capacity=NUM_SPECIALISTS)
  general_practicioners = simpy.Resource(env, capacity=NUM_GP_DOCTORs)

  # Register the creation of the patient arrivals  
  env.process(patient_builder(env, AVG_PATIENT_ARRIVAL_TIME, AVG_REGISTRATION_TIME, 
                    AVG_EVALUATION_TIME, AVG_SPECIALIST_EVALUATION_TIME, 
                    AVG_GP_EVALUATION_TIME, receptionists, nurses, 
                    specialists, general_practicioners))
  # Run the simulation
  env.run(until=120)

if __name__ == "__main__":
  main()