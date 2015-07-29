import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
        '-v', '--visualised', 
        action='store_true', default=False, 
        help = 'visually modelling'
        )
parser.add_argument(
        '-ns', '--nosave', 
        action='store_true', default=False, 
        help = 'not saving html'
        )
parser.add_argument(
        '-sh', '--show', 
        action='store_true', default=False, 
        help = 'in the end show html in browser'
        )
parser.add_argument(
        '-l', '--limit', 
        type=int, default=201,
        help = 'setting limit for iteration amount displayed in html file'
        )
parser.add_argument(
        '-sz', '--size', 
        type=int, default=1200,
        help = 'settings size for maximum between width and height of output picture in html file'
        )

namespace = parser.parse_args()

if namespace.visualised:
  # This is for testing
  # It requiers pybox2d testing scripts (https://github.com/pybox2d/pybox2d/tree/master/examples):
  #  - pygame_framework.py
  #  - framework.py
  #  - settings.py

  # Clearing arguments because pybox2d will raise an error if it get any of arguments mentioned above
  # We are also aren't going to use any of pybox2d arguments
  sys.argv = sys.argv[:1]
  from framework import *
  class Simulation(Framework):
    name = "Throwable" # Name of the class to display
    description = "First example" 
    namespace = namespace

    def init_world(self):
      super(Simulation, self).__init__()

    def step_world(self, settings):
      Framework.Step(self, settings)

else:
  from Box2D import *
  class fwDestructionListener(b2DestructionListener):
    """
    The destruction listener callback:
    "SayGoodbye" is called when a joint or shape is deleted.
    """
    test = None
    def __init__(self, **kwargs):
      super(fwDestructionListener, self).__init__(**kwargs)

    def SayGoodbye(self, object):
      if isinstance(object, b2Joint):
        if self.test.mouseJoint==object:
          self.test.mouseJoint=None
        else:
          self.test.JointDestroyed(object)
      elif isinstance(object, b2Fixture):
        self.test.FixtureDestroyed(object)
        

  class Simulation(b2ContactListener):
    namespace = namespace

    def FixtureDestroyed(self, fixture):
      pass

    def JointDestroyed(self, joint):
      pass

    def init_world(self):
      super(Simulation, self).__init__()
      self.world = b2World(gravity=(0,-10), doSleep=True)
      self.destructionListener = fwDestructionListener(test=self)
      self.world.destructionListener = self.destructionListener
      self.world.contactListener = self

    def step_world(self, settings):
      timeStep = 1.0 / settings.hz
      self.world.Step(
          timeStep, 
          settings.velocity_iterations, 
          settings.position_iterations
          )

    def run(self):
      while not self.finalized:
        self.Step(self.start_settings.model_settings)
