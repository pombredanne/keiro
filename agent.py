import time
import pygame
from functools import wraps
from fast.vector2d import Vec2d
from unit import Unit


class AgentRegistrar(type):
    register = {}

    def __new__(cls, name, bases, dct):
        assert name not in AgentRegistrar.register, 'Multiple agents %r defined!' % name
        ret = AgentRegistrar.register[name] = type.__new__(cls, name, bases, dct)
        return ret


class IterationStats(object):
    """Registers algorithm iteration statistics"""
    def __init__(self):
        self._times = []
        self._start = None

    def start_iteration(self):
        self._start = time.clock()

    def end_iteration(self):
        self._times.append(time.clock() - self._start)
        assert(self._start is not None)
        self._start = None

    def get_max_iterationtime(self):
        return max(self._times)

    def get_min_iterationtime(self):
        return min(self._times)

    def get_avg_iterationtime(self):
        return sum(self._times) / len(self._times)



class Agent(Unit):
    """Base class for all navigational algorithms"""
    __metaclass__ = AgentRegistrar

    view_range = 150

    def __init__(self, parameter):
        super(Agent, self).__init__()
        self.parameter = parameter
        self.color = (100, 100, 255)
        self.travel_length = 0
        self.iterations = IterationStats()

    def render(self, screen):
        #draw a cross over the target
        pygame.draw.aaline(screen, (255, 0, 0),
                self.goal + Vec2d(-10, -10), self.goal + Vec2d(10, 10))
        pygame.draw.aaline(screen, (255, 0, 0),
                self.goal + Vec2d(10, -10), self.goal + Vec2d(-10, 10))

        super(Agent, self).render(screen)
        #pygame.draw.circle(screen, self.color,
        #   map(int, self.position), int(self.radius), 0)

        #draw all waypoints
        last = self.position
        for i in xrange(self.waypoint_len()):
            pygame.draw.aaline(screen, (0, 0, 0), last, self.waypoint(i).position)
            last = self.waypoint(i).position
            pygame.draw.aaline(screen, (0, 0, 0), last, last)

        #draw viewrange
        pygame.draw.circle(screen, (100, 100, 100),
            map(int, self.position), int(self.view_range), 1)

    def init(self, view):
        """Called before simulation starts with the initial information available to the agent

        Allows for agent initialization using information about of the surroundings
        """
        pass

    def _think(self, *args, **kwargs):
        self.iterations.start_iteration()
        self.think(*args, **kwargs)
        self.iterations.end_iteration()

    def think(self, dt, view, debugsurface):
        raise NotImplementedError('An Agent needs to have a brain! Implement the `think()` method')

