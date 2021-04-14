import simpy

class Car(object):
  def __init__(self, env) -> None:
    self.env = env
    self.action = env.process(self.run())

  def run(self):
    while True:
      print(f"Start parking and charging at {self.env.now}")
      charge_duration = 5
      yield self.env.process(self.charge(charge_duration))

      print(f"Start driving at {self.env.now}")
      trip_duration = 2
      yield self.env.timeout(trip_duration)

  def charge(self, duration):
    yield self.env.timeout(duration)


def car(env, name, bcs, driving_time, charge_duration):
  # Drive to the battery charging station (bcs)
  yield env.timeout(driving_time)

  #Request on of its charging spots
  print(f"{name} arriving at {env.now}")
  with bcs.request() as req:
    yield req

    #charge the battery
    print(f"{name} starting to charge at {env.now}")
    yield env.timeout(charge_duration)
    print(f"{name} leaving the bcs at {env.now}")



def main():
  env = simpy.Environment()
  bcs = simpy.Resource(env, capacity=2)

  for i in range(4):
    env.process(car(env, f"Car {i}", bcs, i*2, 5))

  env.run()