from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from flask import Flask, render_template, request, jsonify
import os
from agentes import Semaforo, carros, Pared, Camino 
app = Flask(__name__, static_url_path='')

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))


jsonString = "["

class Trafico(Model):
  example = [
    ((0, 10), (21, 10)),
    ((20, 11), (-1, 11)),

    ((10, 20), (10, -1)),
    ((11, 0), (11, 21)),
  ]

  def __init__(self, n_agents_per_iter=4, max_agents=10, road_list=example, width=21, height=21):
    self.grid = MultiGrid(width, height, True)
    self.schedule = RandomActivation(self)

    self.n_agents_per_iter = n_agents_per_iter
    self.iter = 0

    self.max_agents = max_agents
    self.n_agents = 0

    self.vehicles = []
    self.lights = []

    # Paredes
    for x in range(width):
      for y in range(height):
        wall = Pared(x, y)
        self.grid.place_agent(wall, (x, y))

    # Camino
    for road in road_list:
      start, end = road
      calcX = end[0] - start[0]
      calcY = end[1] - start[1]
      goes = ''
      cond = None

      if not calcX == 0:
        if calcX > 0:
          goes = 'R'
          cond = 0
        else:
          goes = 'L'
          cond = 1
      elif not calcY == 0:
        if calcY > 0:
          goes = 'U'
          cond = 0
        else:
          goes = 'D'
          cond = 1

      x = start[0]
      y = start[1]
      while x != end[0]:
        cell = self.grid.get_cell_list_contents((x, y), True)

        if any(isinstance(elem, Pared) for elem in cell):
          self.grid.remove_agent(cell[0])

        if any(isinstance(elem, Camino) for elem in cell):
          cell[0].dir.append(goes)
        else:
          r = Camino(0, self, x, y)
          r.dir.append(goes)
          self.grid.place_agent(r, (x, y))

        if cond == 0:
          x += 1
        else:
          x -= 1

      while y != end[1]:
        cell = self.grid.get_cell_list_contents((x, y), True)

        if any(isinstance(elem, Pared) for elem in cell):
          self.grid.remove_agent(cell[0])

        if any(isinstance(elem, Camino) for elem in cell):
          cell[0].dir.append(goes)
        else:
          r = Camino(1, self, x, y)
          r.dir.append(goes)
          self.grid.place_agent(r, (x, y))

        if cond == 0:
          y += 1
        else:
          y -= 1
    
    self.grid.get_cell_list_contents((10, 0), True)[0].dir[0] = 'R'
    self.grid.get_cell_list_contents((19, 10), True)[0].dir[0] = 'U'
    self.grid.get_cell_list_contents((0, 11), True)[0].dir[0] = 'D'
    self.grid.get_cell_list_contents((11, 20), True)[0].dir[0] = 'L'

    # Semaforos
    self.traff = (9, 10)
    self.traffic_light = Semaforo(0, self, self.traff, True)
    self.grid.place_agent(self.traffic_light, self.traff)

    self.traff2 = (10, 12)
    self.traffic_light2 = Semaforo(1, self, self.traff2, False)
    self.grid.place_agent(self.traffic_light2, self.traff2)

    self.traff3 = (12, 11)
    self.traffic_light3 = Semaforo(0, self, self.traff3, True)
    self.grid.place_agent(self.traffic_light3, self.traff3)

    self.traff4 = (11, 9)
    self.traffic_light4 = Semaforo(1, self, self.traff4, False)
    self.grid.place_agent(self.traffic_light4, self.traff4)

    self.traffic_light.luz.append(self.traffic_light2)
    self.traffic_light2.luz.append(self.traffic_light) 
    self.traffic_light3.luz.append(self.traffic_light2)
    self.traffic_light4.luz.append(self.traffic_light) 

    self.lights.append(self.traffic_light)
    self.lights.append(self.traffic_light2)
    self.lights.append(self.traffic_light3)
    self.lights.append(self.traffic_light4)

    # Carros
    pos = [(1,10), (3,10), (10,19)]
    for i in range(3):
      self.vehicle_pos = pos[i]
      self.vehicle = carros(i, self, self.vehicle_pos)
      self.grid.place_agent(self.vehicle, self.vehicle_pos)
      self.vehicles.append(self.vehicle)
    
    # Start
    self.running = True

  def generate_random_cars(self):
    pos = [(0, 10), (19, 11), (10, 20), (11, 0)]

    if self.iter == 5:
      for i in range(self.n_agents_per_iter):
        if self.n_agents == self.max_agents:
          print('limite')
          continue
        else:
          cell = self.grid.get_cell_list_contents(pos[i], True)
          if not any(isinstance(elem, carros) for elem in cell):
            self.vehicle = carros(i, self, pos[i])
            self.grid.place_agent(self.vehicle, pos[i])
            self.vehicles.append(self.vehicle)
            self.n_agents += 1
            print('add')
      self.iter = 0
    else:
      self.iter += 1
  
  def step(self):
    self.generate_random_cars()
    ps = []
    for vehicle in self.vehicles:
      
      vehicle.mover()

      xy = vehicle.pos
      p = [xy[0],xy[1],0]
      ps.append(p)

    for light in self.lights:
      light.check()
    self.formatJSON()

    self.schedule.step()
    return ps


  def run_model(self, n):
    for i in range(n):
      self.step()
      #print(jsonString)

    temp = jsonString[0:-1] + "]"
    print(temp)

  def formatJSON(self):
      global jsonString
      count = 0
      stringJSON = '{ "TrafficLights":['
      for trafficLight in self.lights:
        stringJSON += '{ "TrafficLightsId":' + str(trafficLight.u_id) + ', "Luz":' + str(trafficLight.ciclo) + ', "Position":{"x":' + str(trafficLight.x)+', "y": 0, "z":'+ str(trafficLight.y)+ '}}'
        if count < len(self.lights)-1:
          stringJSON += ","
        count += 1
      stringJSON += '], "Cars":['
      count = 0
      for vehicle in self.vehicles:
        stringJSON += '{ "CarId":' + str(vehicle.u_id) + ',"Position":{"x":'+str(vehicle.x)+', "y": 0, "z":'+str(vehicle.y)+ '}}'
        if count < len(self.vehicles)-1:
          stringJSON += ","
        count += 1
      
      #stringJSON += '], "DeletedCars": [' + ','.join(self.idRemovedVehicles) + ']},'
      stringJSON += ']}'

      jsonString += stringJSON
      return stringJSON

@app.route('/')
def root():
    global jsonString
    modelo = Trafico()
    modelo.run_model(10)
    temp = jsonString[0:-1] + "]"
    return jsonify(temp)
    #return jsonify([{"message":"Pruebas Tec, from IBM Cloud!"}])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)


