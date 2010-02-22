from world import *
import math
import random
from fast import graphutils, physics
import graphs

class UnitRegistrar(type):
	register = {}
	def __new__(cls, name, bases, dct):
		ret = UnitRegistrar.register[name] = type.__new__(cls, name, bases, dct)
		return ret
		
class Unit(Particle):
	__metaclass__ = UnitRegistrar

	color = (255, 255, 0)
	view_range = 0
	
	def __init__(self):
		Particle.__init__(self)
		self.radius = 5
		self.speed = 30
		self.turningspeed = 2*math.pi/3
		self.iteration_listeners = []
	
	def add_iteration_listener(self, listener):
		self.iteration_listeners.append(listener)
		
	def _pre_think(self):
		for il in self.iteration_listeners:
			il.start_iteration()

	def _post_think(self):
		for il in self.iteration_listeners:
			il.end_iteration()
			
	def think(self, dt, visible_particles):
		self._pre_think()
		pass
		self._post_think()
		
	def render(self, screen):
		last = self.position
		for i in xrange(self.waypoint_len()):
			pygame.draw.line(screen, (200, 200, 250), last, self.waypoint(i).position, 1)
			last = self.waypoint(i).position
			pygame.draw.line(screen, (250, 100, 100), last, last, 1)
		
		pygame.draw.circle(screen, self.color, 
			map(int, self.position), int(self.radius), 1)	
		pygame.draw.line(screen, self.color,
			map(int, self.position), 
			map(int, (self.position.x + math.cos(self.angle)*self.radius, self.position.y + math.sin(self.angle)*self.radius)))
			

class RandomWalker(Unit):
	step_mean = 20
	view_range = 15
	def __init__(self):
		Unit.__init__(self)
	def think(self, dt, view):
		self._pre_think()
		
		if self.waypoint_len() == 0:
			a = random.random()*math.pi*2
			step = random.gauss(self.step_mean, self.step_mean/3)
			self.waypoint_push(self.position + Vec2d(math.cos(a)*step, math.sin(a)*step))
		
		for p in view:
			if (self.waypoint().position - self.position).angle(p.position - self.position) < math.pi/2:
				self.waypoint_clear()
				
		self._post_think()

class Stubborn(Unit):
	def __init__(self):
		Unit.__init__(self)
		self.last_view = ()
	
	def think(self, dt, view):
		self._pre_think()
		
		self.last_view = view
		if not self.goal:
			return
		self.waypoint_clear()
		self.waypoint_push(self.goal)
		
		self._post_think()

	def render(self, screen):
		Unit.render(self, screen)
		
class AStarer(Stubborn):
	view_range = 75
	def __init__(self):
		Stubborn.__init__(self)
		self.last_view = ()
		self.cdist = 10000000
		self.color = (255, 0,0)
		
	def think(self, dt, view):
		self._pre_think()
		
		self.last_view = view
		if not self.goal:
			return
		ccourse = False
		last = self.position
		for i in xrange(self.waypoint_len()):
			for o in view:
				if graphs.linesegdist2(last, self.waypoint(i).position,	o.position) <= (self.radius + o.radius)**2:
					ccourse = True
					break
			last = self.waypoint(i).position
			if ccourse: break

		result = graphs.random_roadmap(self, self.goal, view, graphs.GraphBuilder(self.speed, self.turningspeed))
	
		if ccourse is True:
			self.waypoint_clear()
			
		if result.success is True and (self.waypoint_len() == 0 or result.total_cost < self.cdist):
			self.waypoint_clear()
			for p in result.path:
				self.waypoint_push(Vec2d(*p))
			self.cdist = result.total_cost
			
		self._post_think()	
			
	def render(self, screen):
		pygame.draw.line(screen, (255, 0, 0),
				self.goal + Vec2d(-10,-10), self.goal + Vec2d(10,10), 1)
		pygame.draw.line(screen, (255, 0, 0),
				self.goal + Vec2d(10,-10), self.goal + Vec2d(-10,10), 1)
		Stubborn.render(self, screen)
		pygame.draw.circle(screen, (255, 150, 150), 
			map(int, self.position), int(self.view_range), 1)
		for p in self.last_view:
			pygame.draw.circle(screen, (150, 255, 150),
				map(int, p.position), int(p.radius), 0)

class Arty(AStarer):
	view_range = 75
	def __init__(self):
		Stubborn.__init__(self)
		self.goal = goal
		self.last_view = ()
		self.color = (255, 0,0)
		
	def think(self, dt, view):
		self._pre_think()
		
		if not self.goal:
			return
		self.last_view = view
		path = graphs.ARTBuilder().build(self, self.goal, view, 100)
		self.waypoint_clear()
		if path is not False:
			for p in path:
				self.waypoint_push(p)

		self._post_think()