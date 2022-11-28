from mesa import Agent
import random

class Camino(Agent):
  def __init__(self, unique_id, model, x, y):
    super().__init__(unique_id, model)
    self.dir = [] 

class Pared(Agent):
  def __init__(self, x, y):
    super().__init__(x, y)


class Semaforo(Agent):
  def __init__(self, u_id, model, pos, horiz=True):

    super().__init__(u_id, model)
    self.pos = pos
    self.horiz = horiz
    self.luz = []
    self.ciclo = 1
    self.counter = 0
    self.u_id = u_id

  def status(self):
    if self.luz[0].ciclo == 0:
      self.ciclo = 1
    else:
      self.ciclo = 0

  def check(self):
    self.status()

    direccion = self.model.grid.get_cell_list_contents((self.pos[0], self.pos[1]), True)[0].dir

    if 'D' in direccion:
      self.x = 0
      self.y = 1
    elif 'R' in direccion:
      self.x = -1
      self.y = 0
    elif 'U' in direccion:
      self.x = 0
      self.y = -1
    elif 'L' in direccion:
      self.x = 1
      self.y = 0
             
    vehicle_cell = self.model.grid.get_cell_list_contents((self.pos[0] + self.x, self.pos[1] + self.y), True)

    if self.counter == 3:
      self.ciclo = 0
      self.counter = 0
      self.luz[0].ciclo = 1

    for vehicle in vehicle_cell:
      if type(vehicle) == carros:
        if self.ciclo == 1:
          vehicle.moverse = True
        else:
          vehicle.moverse = False

        self.counter = 0

      else:
        self.counter += 1

class carros(Agent):
  def __init__(self, u_id, model, pos):
    super().__init__(u_id, model)
    self.original_pos = pos
    self.pos = self.original_pos
    self.x = self.pos[0]
    self.y = self.pos[1]
    self.moverse = True
    self.u_id = u_id

  def step(self):
    self.mover()

  def mover(self):
    cell = self.model.grid.get_cell_list_contents((self.x, self.y), True)[0].dir

    if len(cell) > 1 and self.moverse:
      pick = cell[random.randint(0, len(cell)-1)]
      
      if pick == 'R':
        self.x += 1

      elif pick == 'D':
        self.y -= 1

      elif pick == 'L':
        self.x -= 1

      elif pick == 'U':
        self.y += 1

      if self.moverse:
        self.model.grid.move_agent(self, (self.x, self.y))

    else:
      self.checar()
    
  def checar(self):
    cell = self.model.grid.get_cell_list_contents((self.x, self.y), True)[0].dir

    if 'R' in cell and self.moverse:
      if self.model.grid.out_of_bounds((self.x + 1, self.y)):
        self.x = self.original_pos[0]
        self.y = self.original_pos[1]
        self.model.grid.move_agent(self, (self.x, self.y))
        return

      if not (any(isinstance(x, carros) for x in self.model.grid.get_cell_list_contents((self.x + 1, self.y), True))):
        self.x += 1

    elif 'D' in cell and self.moverse:
      if self.model.grid.out_of_bounds((self.x + 1, self.y)):
        self.x = self.original_pos[0]
        self.y = self.original_pos[1]
        self.model.grid.move_agent(self, (self.x, self.y))
        return

      if not (any(isinstance(x, carros) for x in self.model.grid.get_cell_list_contents((self.x, self.y - 1), True))):
        self.y -= 1

    elif 'L' in cell and self.moverse:
      if self.model.grid.out_of_bounds((self.x + 1, self.y)):
        self.x = self.original_pos[0]
        self.y = self.original_pos[1]
        self.model.grid.move_agent(self, (self.x, self.y))
        return

      if not (any(isinstance(x, carros) for x in self.model.grid.get_cell_list_contents((self.x - 1, self.y), True))):
        self.x -= 1

    elif 'U' in cell and self.moverse:
      if self.model.grid.out_of_bounds((self.x + 1, self.y)):
        self.x = self.original_pos[0]
        self.y = self.original_pos[1]
        self.model.grid.move_agent(self, (self.x, self.y))
        return

      if not (any(isinstance(x, carros) for x in self.model.grid.get_cell_list_contents((self.x, self.y + 1), True))):
        self.y += 1
    
    self.model.grid.move_agent(self, (self.x, self.y))

