import design_utils as design

class Task:
	VECTOR = "vector"
	RASTER = "raster"

	def __init__(self, id, name=None, colors=[design.BLACK], speed=100, intensity=0, type=VECTOR, repeat=1):
		self.id = id
		if name:
			self.name = name
		else:
			self.name = id
		self.colors = colors
		self.speed = speed
		self.intensity = intensity
		self.type = type
		self.repeat = repeat


class TaskManager:
	def __init__(self, laser, workspace):
		self.laser = laser
		self.workspace = workspace
		self.tasks = []
		self.activeTask = None

	def getActiveTask(self):
		if self.activeTask:
			activeTask = {
				"id": self.activeTask.id,
				"name": self.activeTask.id,
				"status": "running" if self.laser.isActive() else "stopped" if self.laser.getProgress() < 100 else "finished",
				"progress": self.laser.getProgress()
			}
		else:
			activeTask = {
				"id": 0,
				"name": "---",
				"status": "---",
				"progress": 0
			}

		return activeTask

	def setParams(self, params):
		id = params.get('id', None)
		if not(id): return

		# find task by id
		for task in self.tasks:
			if task.id == id:
				break
		else:
			# create new task
			task = Task(id)
			self.tasks.append(task)

		# set task params
		task.id = params.get('id')
		task.name = params.get('name', task.id)
		task.colors = params.get('colors', [design.BLACK])
		task.speed = float(params.get('speed', 100))
		task.intensity = float(params.get('intensity', 0))
		task.type = params.get('type', Task.VECTOR)
		task.repeat = int(params.get('repeat', 0))

	def run(self, id = None):
		if self.laser.isActive():
			return

		if id is None:
			# process all tasks
			tasks = self.tasks
		else:
			# find task by id
			for task in self.tasks:
				if task.id == id:
					tasks = [task]
					break
			else:
				# id not found
				return

		self.laser.enable()
		for task in tasks:
			self.activeTask = task
			if task.type == Task.VECTOR:
				self.runVectorTask(task)
			else:
				self.runRasterTask(task)
		self.laser.home()

	def runVectorTask(self, task):
		try:
			# get polylines from all drawings in workspace and apply offset to drawing
			drawings = self.workspace.getItems()
			polylines = [ polyline.applyOffset(drawings[k].position) for k in drawings for polyline in drawings[k].polylines]
			print("drawingPolylines", polylines)

			# filter polylines by task color
			print("task.colors",task.colors)
			polylines = list(filter(lambda p: p.color in task.colors, polylines))
			if len(polylines) == 0:
				return

			# connect segmented polylines and reorder from inner to outer
			print("optimize polylines", polylines)
			draw = design.Drawing(polylines, name=task.name)
			draw.optimize(ignoreColor=True)

			# to laser
			if self.laser.isActive():
				return
			print("send to laser")
			self.laser.processVector(draw.polylines,
				originX=self.workspace.homeOff[0]+self.workspace.workspaceOrigin[0],
				originY=self.workspace.homeOff[1]+self.workspace.workspaceOrigin[1],
				feedRate=task.speed,
				repeat=task.repeat) #TODO intensity
		finally:
			pass


