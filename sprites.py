import pygame
from settings import *
from random import choice, randint


class BG(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor):
		super().__init__(groups)
		bg_image = pygame.image.load('graphics/environment/background.png').convert()
		
		full_height = bg_image.get_height() * scale_factor
		full_width = bg_image.get_width() * scale_factor
		full_sized_image = pygame.transform.scale(bg_image,(full_width,full_height))
		
		self.image = pygame.Surface((full_width * 2,full_height))
		self.image.blit(full_sized_image,(0,0))
		self.image.blit(full_sized_image,(full_width,0))

		self.rect = self.image.get_rect(topleft = (0,0))
		self.pos = pygame.math.Vector2(self.rect.topleft)

	def update(self,dt):
		self.pos.x -= 300 * dt
		if self.rect.centerx <= 0:
			self.pos.x = 0
		self.rect.x = round(self.pos.x)

class Ground(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor):
		super().__init__(groups)
		self.sprite_type = 'ground'
		
		# image
		ground_surf = pygame.image.load('graphics/environment/ground.png').convert_alpha()
		self.image = pygame.transform.scale(ground_surf,pygame.math.Vector2(ground_surf.get_size()) * scale_factor)
		
		# position
		self.rect = self.image.get_rect(bottomleft = (0,WINDOW_HEIGHT))
		self.pos = pygame.math.Vector2(self.rect.topleft)

		# mask
		self.mask = pygame.mask.from_surface(self.image)

	def update(self,dt):
		self.pos.x -= 360 * dt
		if self.rect.centerx <= 0:
			self.pos.x = 0

		self.rect.x = round(self.pos.x)

class Plane(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor):
		super().__init__(groups)
		self.sprite_type = 'plane'

		# image 
		self.import_frames(scale_factor)
		self.frame_index = 0
		self.bubble_frame_index = 0
		self.image = self.frames[self.frame_index]

		# rect
		self.rect = self.image.get_rect(midleft = (WINDOW_WIDTH / 20,WINDOW_HEIGHT / 2))
		self.pos = pygame.math.Vector2(self.rect.topleft)

		# movement
		self.gravity = 600
		self.direction = 0
		self.bubble_animation_speed = 0.15

		# mask
		self.mask = pygame.mask.from_surface(self.image)

		# sound
		self.jump_sound = pygame.mixer.Sound('sounds/jump.ogg')
		self.jump_sound.set_volume(0.3)

	def import_frames(self,scale_factor):
		self.frames = []
		for i in range(1):
			#surf = pygame.image.load(f'/Users/przenio/python/flappysammy/graphics/plane/red{i}.png').convert_alpha()
			surf = pygame.image.load(f'graphics/plane/sammy_zombie.png').convert_alpha()
			scaled_surface = pygame.transform.scale(surf,pygame.math.Vector2(surf.get_size())* scale_factor)
			self.frames.append(scaled_surface)

	def import_bubble_swim_particles(self):
		self.bubble_swim_particles = pygame.image.load('graphics/bubbles/bubble.png').convert_alpha()

	def apply_gravity(self,dt):
		self.direction += self.gravity * dt
		self.pos.y += self.direction * dt
		self.rect.y = round(self.pos.y)

	def jump(self):
		self.jump_sound.play()
		self.direction = -400

	def animate(self,dt):
		self.frame_index += 10 * dt
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]			

	def rotate(self):
		rotated_plane = pygame.transform.rotozoom(self.image,-self.direction * 0.06,1)
		self.image = rotated_plane
		self.mask = pygame.mask.from_surface(self.image)

	def update(self,dt):
		self.apply_gravity(dt)
		self.animate(dt)
		self.rotate()

class Obstacle(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor):
		super().__init__(groups)
		self.sprite_type = 'obstacle'

		orientation = choice(('up','down'))
		surf = pygame.image.load(f'graphics/obstacles/{choice((0,1))}.png').convert_alpha()
		self.image = pygame.transform.scale(surf,pygame.math.Vector2(surf.get_size()) * scale_factor)
		
		x = WINDOW_WIDTH + randint(108,168)

		if orientation == 'up':
			y = WINDOW_HEIGHT + randint(20,50)
			self.rect = self.image.get_rect(midbottom = (x,y))
		else:
			y = randint(-50,-20)
			self.image = pygame.transform.flip(self.image,False,True)
			self.rect = self.image.get_rect(midtop = (x,y))

		self.pos = pygame.math.Vector2(self.rect.topleft)

		# mask
		self.mask = pygame.mask.from_surface(self.image)

	def update(self,dt):
		self.pos.x -= 400 * dt
		self.rect.x = round(self.pos.x)
		if self.rect.right <= -100:
			self.kill()

class Bonus(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor):
		super().__init__(groups)
		self.sprite_type = 'bonus'

		surf = pygame.image.load(f'graphics/bonus/bonus.png').convert_alpha()
		self.image = pygame.transform.scale(surf,pygame.math.Vector2(surf.get_size()) * scale_factor)
		
		x = WINDOW_WIDTH + randint(67,127)

		y = WINDOW_HEIGHT - randint(250,650)
		self.rect = self.image.get_rect(midtop = (x,y))
		
			#y = randint(-50,-10)
			#self.image = pygame.transform.flip(self.image,False,True)
			#self.rect = self.image.get_rect(midtop = (x,y))

		self.pos = pygame.math.Vector2(self.rect.topleft)

		# mask
		self.mask = pygame.mask.from_surface(self.image)

	def rotate(self):
		rotated_plane = pygame.transform.rotozoom(self.image,self.direction * 0.06,1)
		self.image = rotated_plane
		self.mask = pygame.mask.from_surface(self.image)

	def update(self,dt):
		self.pos.x -= 250 * dt
		self.rect.x = round(self.pos.x)
		#self.rotate()
		if self.rect.right <= -100:
			self.kill()


class ParticleBubble(pygame.sprite.Sprite):
	def __init__(self,surface):
		super().__init__()

		self.particles = []
		self.display_surface = surface

	def update(self,dt):
		self.pos.x -= 360 * dt
		self.rect.x = round(self.pos.x)
		if self.rect.right <= -50:
			self.kill()

	def emit(self,dt):
		# moves and draws the particles
		if self.particles:
			self.delete_particles()
			for particle in self.particles:
				particle[0][0] -= 360 * dt
				particle[0][1] -= particle[2][1]
				particle[1] -= 0.08
				#particle[3] -= 0.2
				pygame.draw.circle(self.display_surface,pygame.Color('lightseagreen'),particle[0], int(particle[1]))

	def add_particles(self):
		# adds particles
		pos_x = WINDOW_WIDTH - randint(1,400)
		pos_y = WINDOW_HEIGHT - randint(100,200)
		radius = 7
		direction_x = randint(3,5)
		direction_y = randint(1,1)
		particle_circle = [[pos_x,pos_y],radius,[direction_x,direction_y]]
		self.particles.append(particle_circle)

	def delete_particles(self):
		# deletes particles after a certain time
		particle_copy = [particle for particle in self.particles if particle[1] > 0]
		self.particles = particle_copy
