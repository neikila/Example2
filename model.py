#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

import xml.etree.ElementTree as ET

from startSettings import StartSettings
from simulation import *
import drawer


def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i


def create_not_cycled_chain_shape(points):
  shapes = []
  for p1, p2 in zip(points[:-1:1], points[1::1]):
    shapes.append(b2EdgeShape(vertices=[p1, p2]))
  return shapes


def create_polygon_shapes(polygons):
  shapes = []
  for polygon in polygons:
    shapes.append(b2PolygonShape(vertices=polygon))
  return shapes


def create_circle_shapes(circles):
  shapes = []
  for circle in circles:
    shapes.append(b2CircleShape(radius=circle.radius, pos=circle.pos))
  return shapes


def create_shapes(body):
  shapes = []
  shapes += create_polygon_shapes(body.polygons)
  shapes += create_circle_shapes(body.circles)
  return shapes


class Throwable(Simulation):
  iteration_number = 0

  def save_iteration_in_xml_tree(self):
    iteration = ET.SubElement(self.trajectory, "iteration")
    iteration.set("num", str(self.iteration_number))

    self.body.GetMassData(self.mass_data)
    center = self.body.GetWorldPoint(self.mass_data.center)
    x = ET.SubElement(iteration, "x")
    x.text = str(center.x)
    
    y = ET.SubElement(iteration, "y")
    y.text = str(center.y)

  def save_final_state(self):
    result = ET.SubElement(self.result_tree, "result")

    mass = ET.SubElement(result, "mass")
    mass.text = str(self.mass_data.mass)

    inertia = ET.SubElement(result, "inertia")
    inertia.text = str(self.mass_data.I)

    sett = self.start_settings

    body = ET.SubElement(result, "body")
    shape = self.shapes[0]
    if shape is b2PolygonShape:
      body = ET.SubElement(body, "polygon")
      body_vertices = shape.vertices
      for vertice in body_vertices:
        temp = self.body.GetWorldPoint(vertice)
        vertice = ET.SubElement(polygon, "vertice")
        x = ET.SubElement(vertice, "x")
        x.text = str(temp.x)
        
        y = ET.SubElement(vertice, "y")
        y.text = str(temp.y)

  def __init__(self, start_settings):

    # Initialising settings
    # It should be the first to execute
    sett = self.start_settings = start_settings

    self.init_world()
    self.world.gravity=b2Vec2(0, -1 * sett.model_settings.g)

    # Ground
    self.world.CreateBody(
          shapes=create_not_cycled_chain_shape(sett.ground_settings.points)
        )

    # Blocks
    self.targets = []
    for block in sett.blocks:
      block_position = block.block_position
      for body in block.bodies:
        if body.is_dynamic == True:
          func = self.world.CreateDynamicBody
        else:
          func = self.world.CreateStaticBody
        block = func(
              position=(
                block_position[0] + body.position[0],
                block_position[1] + body.position[1]
                ),
              angle=body.angle,
              shapes=create_shapes(body),
              shapeFixture=b2FixtureDef(density=1),
              angularVelocity=body.angular_velocity,
              linearVelocity=(
                  body.lin_velocity_amplitude *
                  math.cos(body.lin_velocity_angle),
                  body.lin_velocity_amplitude *
                  math.sin(body.lin_velocity_angle)
                )
            )
        if body.is_target == True:
          self.targets.append(block)

    # Projectile
    body = sett.projectile_settings
    self.shapes = create_shapes(body)
    self.body=self.world.CreateDynamicBody(
          position=body.position, 
          angle=body.angle,
          shapes=self.shapes,
          shapeFixture=b2FixtureDef(density=1),
          angularVelocity=body.angular_velocity,
          linearVelocity=(
              body.lin_velocity_amplitude *
              math.cos(body.lin_velocity_angle),
              body.lin_velocity_amplitude *
              math.sin(body.lin_velocity_angle)
            )
        )
    self.fixtures = self.body.fixtures
    self.mass_data = b2MassData()

    # Create output xml tree
    self.result_tree = ET.Element("data")
    self.trajectory = ET.SubElement(self.result_tree, "trajectory")
    self.finalized = False


  def Keyboard(self, key):
    pass

  def Step(self, settings):
    self.step_world(settings)
    
    self.iteration_number += 1
    if self.iteration_number % 4 == 0 and self.finalized == False:
      self.save_iteration_in_xml_tree()
    self.is_finished()

  # Actions to do in the end
  def finalize(self):
    if self.finalized == False:
      indent(self.result_tree)
      tree = ET.ElementTree(self.result_tree)
      tree.write('OUTPUT.dat')
      self.finalized = True
     
  # Should modelling be stopped
  def is_finished(self):
    if self.finalized == False:
      pos = self.body.position
      left = self.start_settings.ground_settings.get_left()
      right = self.start_settings.ground_settings.get_right()
      bottom = self.start_settings.ground_settings.get_bottom()
     
      if pos[0] < left[0] or pos[0] > right[0] or int(pos[1]) < int(bottom[1]):
        print "Object is out of field"
        self.finalize()
      
      velocity = self.body.linearVelocity
      accuracy = self.start_settings.model_settings.epsilon_lin_velocity
      if velocity.lengthSquared < accuracy ** 2:
        print "Too slow"
        self.finalize()


if __name__=="__main__":
  start_settings = StartSettings()
  world = Throwable(start_settings)
  world.run()
  world.finalize()
