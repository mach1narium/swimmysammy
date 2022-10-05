import pygame, sys, time, asyncio
from os import path
from settings import *
from sprites import BG, Ground, Sammy, Obstacle, ParticleBubble, Bonus
#import scoreunlocked

class Game:
	def __init__(self):
		
		# setup
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
		pygame.display.set_caption('Swimmy Sammy')
		self.clock = pygame.time.Clock()
		self.active = False
		
		# leaderboard
		self.leaderboard = False
		
		
		#self.client = scoreunlocked.Client()  # instantiating the client
		#self.client.connect('mach1narium', 'swimmysammy')
		
		# to get leaderboard from server [returns None if not found or errors occurred]
		#self.client.get_leaderboard()
		
		# sprite groups
		self.all_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()
		self.bonus_sprites = pygame.sprite.Group()
		#self.particles = pygame.sprite.Group()

		# scale factor
		bg_height = pygame.image.load('graphics/environment/background.png').get_height()

		self.scale_factor = WINDOW_HEIGHT / bg_height

		# sprite setup 
		BG(self.all_sprites,self.scale_factor)
		Ground([self.all_sprites,self.collision_sprites],self.scale_factor)
		self.sammy = Sammy(self.all_sprites,self.scale_factor / 12.0)
		self.particle = ParticleBubble(self.display_surface)
		self.particle_sammy = ParticleBubble(self.display_surface)

		# timer
		self.obstacle_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.obstacle_timer,1400)
		self.bonus_timer = pygame.USEREVENT + 2
		pygame.time.set_timer(self.bonus_timer,8400)
		self.particle_timer = pygame.USEREVENT + 3
		pygame.time.set_timer(self.particle_timer,256)
		self.particle_sammy_timer = pygame.USEREVENT + 4
		pygame.time.set_timer(self.particle_sammy_timer,16)
		
		# text
		self.font = pygame.font.Font('graphics/font/BD_Cartoon_Shout.ttf',30)
		self.font_small = pygame.font.Font('graphics/font/BD_Cartoon_Shout.ttf',10)
		self.load_high_score()
		self.score = 0
		self.fps = 0
		self.start_offset = 0

		# menu
		self.menu_surf = pygame.image.load('graphics/ui/menu.png').convert_alpha()
		self.menu_rect = self.menu_surf.get_rect(center = (WINDOW_WIDTH / 2,WINDOW_HEIGHT / 2))
		
		#music
		pygame.mixer.music.load('sounds/music.ogg')
		pygame.mixer.music.set_volume(0.1)
		pygame.mixer.music.play(loops=-1)
		#sound
		self.slurp_sound = pygame.mixer.Sound('sounds/slurp.ogg')
		self.slurp_sound.set_volume(1.9)

	def collisions(self):
		if pygame.sprite.spritecollide(self.sammy,self.collision_sprites,False,pygame.sprite.collide_mask)\
		or self.sammy.rect.top <= 0:
			for sprite in self.collision_sprites.sprites():
				if sprite.sprite_type == 'obstacle':
					sprite.kill()
					
			self.active = False
			self.sammy.kill()

	def collisions_bonus(self):
		if pygame.sprite.spritecollide(self.sammy,self.bonus_sprites,False,pygame.sprite.collide_mask):
			for sprite in self.bonus_sprites.sprites():
				if sprite.sprite_type == 'bonus':
					self.slurp_sound.play()
					sprite.kill()
					self.start_offset -= 10000

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
			self.leaderboard = True
			with open(path.join(self.dir, HS_FILE), 'w') as f:
				f.write(str(self.high_score))
	
		y = WINDOW_HEIGHT / 50

		high_score_surf = self.font.render(str(round(self.high_score)),True,'black')
		high_score_rect = high_score_surf.get_rect(midtop = (WINDOW_WIDTH / 2 ,y))
		self.display_surface.blit(high_score_surf,high_score_rect)

	def display_fps(self):
		self.ver = "alpha build"
		y = WINDOW_HEIGHT / 50

		fps_surf = self.font_small.render(self.ver,True,'grey')
		fps_rect = fps_surf.get_rect(topright = (WINDOW_WIDTH ,y))
		self.display_surface.blit(fps_surf,fps_rect)
		


	async def run(self):
		self.sammy.kill()
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
					
				if event.type == pygame.KEYDOWN and not self.player_active:
					if event.key == pygame.K_BACKSPACE:
						self.player_name = self.player_name[:-1]
					elif event.key == pygame.K_RETURN:
						self.player_active = True
					else:
						self.player_name += event.unicode	
						
				if event.type == pygame.MOUSEBUTTONDOWN and self.player_active == True:
					if self.active:
						self.sammy.jump()
						#self.bubble = ParticleBubble(self.all_sprites,self.scale_factor * 0.3)
					else:
						#print("Current Working Directory " , os.getcwd())
						self.sammy = Sammy(self.all_sprites,self.scale_factor / 9.0)
						self.active = True
						self.start_offset = pygame.time.get_ticks()

				if event.type == self.bonus_timer and self.active:	
					self.bonus = Bonus([self.all_sprites,self.bonus_sprites],self.scale_factor * 0.6)
				if event.type == self.obstacle_timer and self.active:
					self.obstacle = Obstacle([self.all_sprites,self.collision_sprites],self.scale_factor * 1.2)
				if event.type == self.particle_timer:
					self.particle.add_particles()
				if event.type == self.particle_sammy_timer and self.active:
					self.particle_sammy.add_jump_particles(int(self.sammy.pos.y))
			
			
			# game logic
			self.display_surface.fill('black')
			self.all_sprites.update(dt)
			self.all_sprites.draw(self.display_surface)
			self.particle.emit(dt)
			self.display_high_score()
			self.display_score()
			self.display_fps()
			
			#print(self.clock.get_fps())
			#print(pygame.time.get_ticks() - self.start_offset)

			if self.active: 
				self.collisions()
				self.collisions_bonus()
				self.particle_sammy.emit(dt)
			else:
				self.display_surface.blit(self.menu_surf,self.menu_rect)
				
				#Not working in pygame
				if self.leaderboard == True:
					self.client.post_score(name=self.player_name, score=self.high_score,validation_data='<data to validate score>')
					self.leaderboard = False	
			

			pygame.display.update()
			self.clock.tick(FRAMERATE)
			await asyncio.sleep(0)

if __name__ == '__main__':
	game = Game()
	#game.run()
	asyncio.run(game.run())
