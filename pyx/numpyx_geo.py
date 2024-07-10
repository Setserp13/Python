import numpy as np
import pyx.numpyx as npx
import pyx.mat.mat as mat

class circle():
	def __init__(self, center, radius):
		self.center = np.array(center)
		self.radius = radius

	def angle_of(self, point):
		delta = point - self.center
		return np.arctan2(delta[1], delta[0])

	def get_point(self, theta): return np.array(list(mat.polar_to_cartesian(self.radius, theta)) + [0]) + self.center		

	def get_point01(self, t): return self.get_point(t * 2 * np.pi)

class arc(circle):
	def __init__(self, center, radius, start, end): #start is start angle and end is end angle
		super().__init__(center, radius)
		self.start = start
		self.end = end

	def get_point01(self, t):
		t = mat.clamp01(t)
		return self.get_point(mat.lerp(self.start, self.end, t))

class line():
	def __init__(self, start, end):
		self.start = np.array(start)
		self.end = np.array(end)

	@property
	def length(self): return np.linalg.norm(self.end - self.start)

	@property
	def direction(self): return npx.normalize(self.end - self.start)

	@property
	def midpoint(self): return (self.start + self.end) * 0.5

	@property #in XY-plane
	def normal(self): return np.array([-self.direction[1], self.direction[0]] + list(self.direction[2:]))


class chord(line):
	def __init__(self, start, end, theta):
		super().__init__(start, end)
		self.theta = theta

	@property
	def radius(self): return self.length / (2 * np.sin(self.theta / 2))

	@property
	def distance_to_center(self): return self.radius * np.cos(self.theta / 2)

	@property
	def distance_to_circumference(self): return self.radius - self.distance_to_center

	@property
	def center(self): return self.midpoint + self.normal * self.distance_to_center

	def to_circle(self): return circle(self.center, self.radius)

	def to_arc(self):
		circle = self.to_circle()
		return arc(self.center, self.radius, circle.angle_of(self.start), circle.angle_of(self.end))



def add_symmetrical_handles(vertices, handle_length=.1):
	result = []
	for i in range(len(vertices)):
		u = vertices[i-1] - vertices[i]
		v = vertices[(i+1)%len(vertices)] - vertices[i]
		theta = npx.angle(u, v)
		alpha = (PI - theta) * 0.5
		result += [vertices[i] + rotate(u, -alpha) * handle_length, vertices[i], vertices[i] + rotate(v, alpha) * handle_length]
	result = left_shift(result)
	return result

def truncate(vertices, length=.1):
	result = []
	for i in range(len(vertices)):
		next = vertices[(i+1)%len(vertices)]
		dir = normalize(next - vertices[i])
		result += [vertices[i] + dir * length, next - dir * length]
	return result


def corners(rect): return [rect.denormalize_point(x) for x in [np.array([0,0]), np.array([0,1]), np.array([1,1]), np.array([1,0])]]


