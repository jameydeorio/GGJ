import pygame, Box2D
import math
from common import *
import physics
from game_state import GameState, state

class Unit(pygame.sprite.Sprite, object):

  def __init__(self):
    super(Unit, self).__init__()

  def doGravity(self):
    grav = -self.pos
    len = grav.Normalize()
    grav *= params.home.gravitational_constant * Home.instance.mass / (len*len)
    self.body.ApplyForce(grav, self.pos)
  
  @property
  def screen_coords(self):
    return GameState.current.toScreen(self.pos)

class Home(Unit):

  class Ent(Unit):

    image = None

    def __init__(self, home):
      super(Home.Ent, self).__init__()

      self.home = home
      #Cooldown for allowing the player to fire SOILORBS
      self.shot_cool = 20
      #shot_angle |[-90, 90]|
      self.shot_angle = 0.0
      self.start_angle = 0.0
      self.cw = True
      

      Home.Ent.image = self.image = Media.media.cannon[1]
      self.c_front = Media.media.cannon[2]
      self.rect = self.image.get_rect()

      state().cannon_group.add(self)
      
    #Returns [x,y] coordinates for the ent moving around the planet
    #Param: angle -- angle of the ent relative to the Home
    #Param: radius ---- the radius...
    @property
    def pos(self):
      rad = math.radians(self.home.angle)
      r = self.home.radius + 1.5
      return vec(math.cos(rad)*r, math.sin(rad)*r)
    @property
    def fire_pos(self):
      rad = math.radians(self.shot_angle + self.home.angle) * self.home.angle_mult
      r = 2.5
      return vec(math.cos(rad)*r, math.sin(rad)*r)

    def update(self):
      self.shot_cool -= 1
    
    def angle_point(self, radius):
       return (400 + int(math.cos(math.radians(self.home.angle))*radius),400 + int(math.sin(math.radians(self.home.angle))*radius))

    def angle_to(self, origin, point):  
      return math.degrees(math.atan2(origin[0]-point[0], origin[1]-point[1]))
        
    @property 
    def cannon_origin(self):
      return (math.cos(math.radians(self.home.angle)), math.sin(math.radians(self.home.angle)))

    def draw(self, screen):
      self.c_back = Media.media.cannon[0] 
      self.c_back = rot_center(self.c_back, -self.home.angle) 
      self.cb = self.c_back.get_rect()
      self.cb.center = self.screen_coords
      #screen.blit(self.c_back, self.cb)


      #pygame.draw.circle(screen, [255, 0, 255], self.screen_coords, 20, 0)
      self.rect = self.image.get_rect()
      self.rect.move_ip(self.screen_coords)

      mutate_pt = self.angle_point(60)
      self.image = pygame.transform.rotozoom(Home.Ent.image, -self.home.angle+(self.shot_angle*-self.home.angle_mult), 1.0)
      ang = -self.home.angle+(self.shot_angle*-self.home.angle_mult)
      self.rect = rot_point_img_rect(screen, Home.Ent.image, self.screen_coords, (400, 400), 0 , ang  )

      #print self.screen_coords, mutate_pt, self.angle_to(mutate_pt, self.screen_coords)
      #pygame.draw.circle(screen, (0,64,255), mutate_pt,  4, 0)

      self.c_front = Media.media.cannon[2]
      self.c_front = rot_center(self.c_front, -self.home.angle)
      self.cf = self.c_front.get_rect()
      self.cf.center = self.screen_coords
      screen.blit(self.c_front, self.cf)

      # super(Home.Ent, self).draw(screen)

    # def shoot(self, vel):
    #   if(Home.instance.mass > params.home.min_mass):
    #     Clod(self.pos, vel, 2.5)
    #   else:
    #     print "Home mass too small to shoot!  hah!"

    def fire(self, angle):
      speed = params.ent.firepower
      vel = vec(math.cos(math.radians(angle)) * speed, math.sin(math.radians(angle)) * speed)
      if(Home.instance.mass > params.home.min_mass):
        Clod(self.pos, vel, 0.5 )

  def __init__(self):
    super(Home, self).__init__()

    self.ent = Home.Ent(self)
    self.angle = 0.0
    self.angle_mult = 1.0
    self.angle_delta = 5.0 
    self.mass = params.home.initial_mass
    self.maxmass = 100.0

    screen = pygame.display.get_surface()
    self.image = Media.media.home
    self.rect = self.image.get_rect()
    self.bg = Media.media.back
    self.bgr = self.bg.get_rect() 
    self.pos = vec(0,0)
    self.body = physics.home_body(self.radius)
    # shape.SetUserData(self)

  instance = None
  image = None

  @property
  def radius(self):
    return Home.mass_to_radius(self.mass)

  @staticmethod
  def mass_to_radius(mass):
    return math.sqrt(float(mass)/math.pi)

  def update(self):
    self.ent.update()
    world.DestroyBody(self.body)
    self.body = physics.home_body(self.radius)

  def draw(self, screen):
    scale = int(170 + 80*(self.mass / self.maxmass))
    scale = 2 * int(self.radius * params.game.px_scale)
    self.image = pygame.transform.smoothscale(Home.image, [scale, scale])
    self.rect = self.image.get_rect()
    self.rect.center = [400,400]
    screen.blit(self.image, self.rect)
    self.ent.draw(screen)

    #pygame.draw.circle(screen, [255,255,0], self.screen_coords, int(self.radius), 0)

  def event(self, key):
    if key[pygame.K_SPACE]:
      self.ent.shot_cool -= 1
      if self.ent.shot_cool < 0:
        fireang = (self.ent.shot_angle *self.angle_mult) + self.angle
        self.ent.fire(fireang)
        self.ent.shot_cool = 30
    if key[ord('s')]:
      if self.ent.shot_angle < 90.0:
        self.ent.shot_angle += 1.0
      print self.ent.shot_angle
    elif key[ord('w')]:
      if self.ent.shot_angle > 0.5:
        self.ent.shot_angle -= 1.0
      print self.ent.shot_angle

    if key[ord('a')]:
      print 'a event called', self.angle
      self.angle_mult = -0.75
      self.angle = self.angle - self.angle_delta 

    elif key[ord('d')]:
      print 'd event called', self.angle
      self.angle_mult = 0.75
      self.angle = self.angle + self.angle_delta

class Clod(Unit):
  def __init__(self, pos, vel, mass):
    super(Clod, self).__init__()
    self.mass = mass
    self.radius = Home.mass_to_radius(mass)
    self.body, self.shape = physics.clod_body(self.radius, pos, vel, mass)
    self.shape.SetUserData(self)
    self.image = Media.media.clod
    self.rect = self.image.get_rect()
    state().clods.add(self)
    Home.instance.mass -= mass

  @property
  def pos(self):
    return self.body.GetPosition()

  def draw(self):
    pass
    # pygame.draw.circle(screen, [255,255,0], self.screen_coords, 4, 0)

  def update(self):
    self.doGravity()
    r = self.pos.Length()
    if(r + self.radius < Home.instance.radius):
      Home.instance.mass += self.mass
      world.DestroyBody(self.body)
      state().clods.remove(self)
      self.shape.ClearUserData()
      del self
    elif(r > params.game.max_distance):
      world.DestroyBody(self.body)
      state().clods.remove(self)
      self.shape.ClearUserData()
      del self
    else:
      self.rect.center = self.screen_coords


class Snake(Unit):

  all = []

  def __init__(self):
    super(Snake, self).__init__()
    state().snakes.add(self)
    Snake.all.append(self)

    spawn_angle = math.pi * random.uniform(0, 2)
    speed = -random.uniform(1, 2)

    vel = polar_vec(speed, spawn_angle / random.uniform(-0.5, 0.5))
    # pos = polar_vec(params.dragon.spawn_distance, spawn_angle)
    pos = vec(10, -10)
    self.body, self.shape = physics.snake_body(pos, vel)
    self.shape.SetUserData(self)
    self.is_hit = False
    self.image = Media.media.snake
    self.rect = self.image.get_rect()

  def take_hit(self):
    self.is_hit = True
    self.body.SetLinearVelocity(self.body.GetLinearVelocity() * 0.2)

  @property
  def pos(self):
    return self.body.GetPosition()
  
  def update(self):
    # self.rect.center = self.screen_coords
    self.doGravity()
    self.rect.center = self.screen_coords

  def draw(self, screen):
    pass


class Dragon(Unit):

  all = []

  def __init__(self):
    super(Dragon, self).__init__()
    state().dragons.add(self)
    Dragon.all.append(self)

    spawn_angle = math.pi * random.uniform(0, 2)
    speed = -random.uniform(1, 2)

    vel = polar_vec(speed, spawn_angle / random.uniform(-0.5, 0.5))

    # pos = polar_vec(params.dragon.spawn_distance, spawn_angle)
    pos = vec(10, -10)
    self.bodies, self.shapes = physics.dragon_body(pos, vel)
    self.body = self.bodies[0]
    for s in self.shapes: s.SetUserData(self)

    self.is_hit = False

    print "\nDragon spawned!\nangle: {init_angle}\nvelocity: {init_velocity}".format(
          init_angle = spawn_angle,
          init_velocity = vel,
          )

  def take_hit(self):
    self.is_hit = True
    self.body.SetLinearVelocity(self.body.GetLinearVelocity() * 0.2)

  @property
  def pos(self):
    return self.body.GetPosition()

  def update(self):
    # self.rect.center = self.screen_coords
    self.doGravity()

  def draw(self, screen):
    for i in range(0, len(self.bodies)-1):
      b = self.bodies[i]
      pos = state().toScreen(b.GetPosition())
      ang = b.GetAngle()
      img = Media.media.dragon[params.dragon.order[i]]

      rect = pygame.Rect((0,0), img.get_size())
      rect.center = pos
      screen.blit(img, rect)
      pygame.draw.rect(screen, (255,0,255), rect, 1)


      ja = params.dragon.joint_attachments[params.dragon.order[i]]
      if(ja[0] is not None):
        a = vec(rect.topleft)
        a += vec(ja[0])
        a = (int(a.x), int(a.y))
        pygame.draw.circle(screen, (255,0,0), a, 5)
      if(ja[1] is not None):
        b = vec(rect.topleft)
        b += vec(ja[1])
        b = (int(b.x), int(b.y))
        pygame.draw.circle(screen, (255,255,0), b, 5)













