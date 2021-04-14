import random
import simpy

# Tools in the simpy Toolbox
# - Environments
# - Events
# - Resources
# - Containers
# - Stores


MINS_BETWEEN_APTS = 1
NURSES_PER_SITE = 100
APT_DURATION_MINS = 5
EVENT_DURATION_HRS = 10

# POD Stats
# App Servers: 80
# DB Nodes 16
# DB SKU E
DB_Nodes = 2
CONNECTIONS_PER_NODE = ?

# Recipients can do the following:
#   - Register
#   - Schedule an Appointment
class Recipient:
  def __init__(self, env) -> None:
    self.env = env 
    self.action = env.process(self.run())

  def run(self):
    pass

# Create a Registration Site Resource - 5 minutes time to work. Limit 500
# Create a Scheduling Site Resource - 5 minutes time to work. 
# DB Node had X connections available.

# I'd like to track the number of people in each state (reg, sched).
# I'd like to see how waves impact things.
# Keep in mind, registration and scheduling use the same DB nodes.
# User Creation -> Register -> Scheduler
# User Creation -> Waiting Room -> Scheduler
