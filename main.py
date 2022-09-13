import pygame, sys, time, asyncio
from os import path
from settings import *
from sprites import BG, Ground, Plane, Obstacle, ParticleBubble, Bonus

class Game:
	def __init__(self):
		
		# setup
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
		pygame.display.set_caption('Flappy Sammy')
		self.clock = pygame.time.Clock()
		self.active = False

		# sprite groups
		self.all_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()
		self.particles = pygame.sprite.Group()

		# scale factor
		#bg_height = pygame.image.load('/Users/przenio/python/flappysammy/graphics/environment/background.png').get_height()
		bg_height = pygame.image.load('graphics/environment/background.png').get_height()

		self.scale_factor = WINDOW_HEIGHT / bg_height

		# sprite setup 
		BG(self.all_sprites,self.scale_factor)
		Ground([self.all_sprites,self.collision_sprites],self.scale_factor)
		self.plane = Plane(self.all_sprites,self.scale_factor / 12.0)
		#self.bubble = ParticleBubble(self.all_sprites,self.scale_factor / 3.5)

		# timer
		self.obstacle_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.obstacle_timer,1400)
		self.bonus_timer = pygame.USEREVENT + 2
		pygame.time.set_timer(self.bonus_timer,8400)
		
		# text
		self.font = pygame.font.Font('graphics/font/BD_Cartoon_Shout.ttf',30)
		self.load_high_score()
		self.score = 0
		self.fps = 0
		self.start_offset = 0

		# menu
		self.menu_surf = pygame.image.load('graphics/ui/menu.png').convert_alpha()
		self.menu_rect = self.menu_surf.get_rect(center = (WINDOW_WIDTH / 2,WINDOW_HEIGHT / 2))
		
		#music
		pygame.mixer.music.load('sounds/music.ogg')
		pygame.mixer.music.play(-1)

	def collisions(self):
		if pygame.sprite.spritecollide(self.plane,self.collision_sprites,False,pygame.sprite.collide_mask)\
		or self.plane.rect.top <= 0:
			for sprite in self.collision_sprites.sprites():
				if sprite.sprite_type == 'obstacle':
					sprite.kill()
				elif sprite.sprite_type == 'bonus':
					sprite.kill()
					self.start_offset -= 10000
					return
			self.active = False
			self.plane.kill()

	def display_score(self):
		if self.active:
			self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
			y = WINDOW_HEIGHT / 10
		else:
			y = WINDOW_HEIGHT / 2 + (self.menu_rect.height / 1.5)

		score_surf = self.font.render(str(self.score),True,'grey')
		score_rect = score_surf.get_rect(midtop = (WINDOW_WIDTH / 2,y))
		self.display_surface.blit(score_surf,score_rect)

	def load_high_score(self):
		self.dir = path.dirname(path.abspath(__file__))
		with open(path.join(self.dir, HS_FILE), 'r') as f:
			try:
				self.high_score = int(f.read())
			except:
				self.high_score = 0

	def display_high_score(self):
		if self.score > self.high_score:
			self.high_score = self.score
			with open(path.join(self.dir, HS_FILE), 'w') as f:
				f.write(str(self.high_score))
	
		y = WINDOW_HEIGHT / 50

		high_score_surf = self.font.render(str(round(self.high_score)),True,'black')
		high_score_rect = high_score_surf.get_rect(midtop = (WINDOW_WIDTH / 2 ,y))
		self.display_surface.blit(high_score_surf,high_score_rect)

	def display_fps(self):
		self.fps = (self.clock.get_fps())
		y = WINDOW_HEIGHT / 60

		fps_surf = self.font.render(str(round(self.fps)),True,'black')
		fps_rect = fps_surf.get_rect(topright = (WINDOW_WIDTH ,y))
		self.display_surface.blit(fps_surf,fps_rect)

	async def run(self):
		self.plane.kill()
		last_time = time.time()
		while True:
			
			# delta time
			dt = time.time() - last_time
			last_time = time.time()
			
			# event loop
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					if self.active:
						self.plane.jump()
						#self.bubble = ParticleBubble(self.all_sprites,self.scale_factor * 0.3)
					else:
						#print("Current Working Directory " , os.getcwd())
						self.plane = Plane(self.all_sprites,self.scale_factor / 9.0)
						self.active = True
						self.start_offset = pygame.time.get_ticks()

				if event.type == self.obstacle_timer and self.active:
					self.obstacle = Obstacle([self.all_sprites,self.collision_sprites],self.scale_factor * 1.2)
				if event.type == self.bonus_timer and self.active:	
					self.bonus = Bonus([self.all_sprites,self.collision_sprites],self.scale_factor * 0.6)
			
			
			# game logic
			self.display_surface.fill('black')
			self.all_sprites.update(dt)
			self.all_sprites.draw(self.display_surface)
			self.display_high_score()
			self.display_score()
			#self.display_fps()
			#print(self.clock.get_fps())
			#print(pygame.time.get_ticks() - self.start_offset)

			if self.active: 
				self.collisions()
			else:
				self.display_surface.blit(self.menu_surf,self.menu_rect)

			pygame.display.update()
			#self.clock.tick(FRAMERATE)
			await asyncio.sleep(0)

if __name__ == '__main__':
	game = Game()
	#game.run()
	asyncio.run(game.run())
