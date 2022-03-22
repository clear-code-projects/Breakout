import pygame,sys,time
from settings import *
from sprites import Player, Ball, Block, Upgrade, Projectile
from surfacemaker import SurfaceMaker
from random import choice, randint

class Game:
	def __init__(self):
		
		# general setup
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
		pygame.display.set_caption('Breakout')

		# background
		self.bg = self.create_bg()

		# sprite group setup
		self.all_sprites = pygame.sprite.Group()
		self.block_sprites = pygame.sprite.Group()
		self.upgrade_sprites = pygame.sprite.Group()
		self.projectile_sprites = pygame.sprite.Group()

		# setup
		self.surfacemaker = SurfaceMaker()
		self.player = Player(self.all_sprites,self.surfacemaker)
		self.stage_setup()
		self.ball = Ball(self.all_sprites,self.player,self.block_sprites)

		# hearts
		self.heart_surf = pygame.image.load('../graphics/other/heart.png').convert_alpha()

		# projectile
		self.projectile_surf = pygame.image.load('../graphics/other/projectile.png').convert_alpha()
		self.can_shoot = True
		self.shoot_time = 0

		# crt
		self.crt = CRT()

		self.laser_sound = pygame.mixer.Sound('../sounds/laser.wav')
		self.laser_sound.set_volume(0.1)

		self.powerup_sound = pygame.mixer.Sound('../sounds/powerup.wav')
		self.powerup_sound.set_volume(0.1)

		self.laserhit_sound = pygame.mixer.Sound('../sounds/laser_hit.wav')
		self.laserhit_sound.set_volume(0.02)

		self.music = pygame.mixer.Sound('../sounds/music.wav')
		self.music.set_volume(0.1)
		self.music.play(loops = -1)

	def create_upgrade(self,pos):
		upgrade_type = choice(UPGRADES)
		Upgrade(pos,upgrade_type,[self.all_sprites,self.upgrade_sprites])

	def create_bg(self):
		bg_original = pygame.image.load('../graphics/other/bg.png').convert()
		scale_factor = WINDOW_HEIGHT / bg_original.get_height()
		scaled_width = bg_original.get_width() * scale_factor
		scaled_height = bg_original.get_height() * scale_factor
		scaled_bg = pygame.transform.scale(bg_original,(scaled_width,scaled_height)) 
		return scaled_bg

	def stage_setup(self):
		# cycle through all rows and columns of BLOCK MAP
		for row_index, row in enumerate(BLOCK_MAP):
			for col_index, col in enumerate(row):
				if col != ' ':
					# find the x and y position for each individual block
					x = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE // 2
					y = TOP_OFFSET + row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE // 2
					Block(col,(x,y),[self.all_sprites,self.block_sprites],self.surfacemaker,self.create_upgrade)

	def display_hearts(self):
		for i in range(self.player.hearts):
			x = 2 + i * (self.heart_surf.get_width() + 2)
			self.display_surface.blit(self.heart_surf,(x,4))

	def upgrade_collision(self):
		overlap_sprites = pygame.sprite.spritecollide(self.player,self.upgrade_sprites,True)
		for sprite in overlap_sprites:
			self.player.upgrade(sprite.upgrade_type)
			self.powerup_sound.play()

	def create_projectile(self):
		self.laser_sound.play()
		for projectile in self.player.laser_rects:
			Projectile(
				projectile.midtop - pygame.math.Vector2(0,30),
				self.projectile_surf,
				[self.all_sprites, self.projectile_sprites])

	def laser_timer(self):
		if pygame.time.get_ticks() - self.shoot_time >= 500:
			self.can_shoot = True

	def projectile_block_collision(self):
		for projectile in self.projectile_sprites:
			overlap_sprites  = pygame.sprite.spritecollide(projectile,self.block_sprites,False)
			if overlap_sprites:
				for sprite in overlap_sprites:
					sprite.get_damage(1)
				projectile.kill()
				self.laserhit_sound.play()

	def run(self):
		last_time = time.time()
		while True:
			
			# delta time
			dt = time.time() - last_time
			last_time = time.time()

			# event loop
			for event in pygame.event.get():
				if event.type == pygame.QUIT or self.player.hearts <= 0:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						self.ball.active = True
						if self.can_shoot:
							self.create_projectile()
							self.can_shoot = False
							self.shoot_time = pygame.time.get_ticks()

			# draw bg
			self.display_surface.blit(self.bg,(0,0))
			
			# update the game
			self.all_sprites.update(dt)
			self.upgrade_collision()
			self.laser_timer()
			self.projectile_block_collision()

			# draw the frame
			self.all_sprites.draw(self.display_surface)
			self.display_hearts()

			# crt styling
			self.crt.draw()

			# update window
			pygame.display.update()

class CRT:
	def __init__(self):
		vignette = pygame.image.load('../graphics/other/tv.png').convert_alpha()
		self.scaled_vignette = pygame.transform.scale(vignette,(WINDOW_WIDTH,WINDOW_HEIGHT))
		self.display_surface = pygame.display.get_surface()
		self.create_crt_lines()

	def create_crt_lines(self):
		line_height = 4
		line_amount = WINDOW_HEIGHT // line_height
		for line in range(line_amount):
			y = line * line_height
			pygame.draw.line(self.scaled_vignette, (20,20,20), (0,y), (WINDOW_WIDTH,y),1)

	def draw(self):
		self.scaled_vignette.set_alpha(randint(60,75))
		self.display_surface.blit(self.scaled_vignette,(0,0))

if __name__ == '__main__':
	game = Game()
	game.run()
