
class Workspace:
	def __init__(self, width=100, height=100, originOffset=[0,0]):
		self.drawings = dict()
		self.size = [width, height]
		self.originOffset = originOffset
		self.drawingsOrigin = originOffset[:]

	def update(self):
		print("workspace has been updated -> reload")
		# TODO

	def add(self, drawing):
		self.drawings[drawing.id] = drawing
		self.update()

	def remove(self, id):
		del self.drawings[id]
		if len(self.drawings):
			self.drawingsOrigin = self.originOffset[:]
		self.update()

	def clear(self):
		self.drawings.clear()
		self.drawingsOrigin = self.originOffset[:]
		self.update()
