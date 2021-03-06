import os, sys, pygame
from Box2D import *
from pygame.locals import *

from common import *
from game_state import *
import physics
import units
import cProfile

class Game:

  media = None

  def __init__(self):
    pygame.init()

    self.screen_size = [800, 800]

    self.screen = pygame.display.set_mode(self.screen_size)
    self.clock = pygame.time.Clock()
    pygame.display.set_caption('Entropy')

    self.backgd = pygame.Surface(self.screen.get_size())
    self.back_color = [128,128,128]

    physics.b2draw.surface = self.screen

    self.frames = 0
    self.show = pygame.sprite.RenderClear()

    GameState.current = PlayState()

    Game.media = Media()
    Media.media = Game.media

    units.Home.image = Media.media.home

  def play_music_sequence(self):
    if random.randint(1, 3) == 1:
      index = random.randint(0, len(Game.media.music_seqs) - 1)
      if not pygame.mixer.get_busy():
        Game.media.music_seqs[index].play()

  def run_loop(self):

    home = units.Home()
    units.Home.instance = home
    # home_sprites = pygame.sprite.RenderPlain(home)

    def update():
      home.update()
      GameState.current.update()
      physics.worldStep()

    def draw():
      bg = Media.media.back
      bgr = bg.get_rect()
      self.screen.blit(bg, bgr)
      GameState.current.draw(self.screen)


      c_back = Media.media.cannon[0] 
      c_back = rot_center(c_back, -home.angle) 
      cb = c_back.get_rect()
      cb.center =home.ent.screen_coords
      self.screen.blit(c_back, cb)


 
      home.draw(self.screen)
      #HACK
      for d in units.Dragon.all:
        d.draw(self.screen)
    
    def spawn_dragon():
      units.Snake()
    
    spawn_dragon()
    # pygame.time.set_timer(USEREVENT+1, 2000)
    pygame.mixer.music.load(os.path.join('media/music', 'noise.ogg'))
    pygame.mixer.music.set_volume(0.75)
    pygame.mixer.music.play(-1)
    pygame.time.set_timer(USEREVENT+2, 5000)

    while 1:
      self.clock.tick(60)
      self.screen.fill(self.back_color)

      pygame.event.pump()
      key = pygame.key.get_pressed()

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          return
        if event.type == KEYDOWN:
          if event.key == K_ESCAPE:
            return
        if event.type == USEREVENT+2:
          self.play_music_sequence() 
      
      home.event(key)
      update()



      draw()

      pygame.display.flip()

    

def main():
  game = Game()
  game.run_loop()


if __name__ == '__main__':
  main()
  # cProfile.run('main()')
