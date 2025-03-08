import pygame
import random
MAX_BULLET_RANGE = 800  



pygame.init()


WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CS project")


clock = pygame.time.Clock()
FPS = 60


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (100, 200, 255)
LIGHT_RED = (255, 100, 100)
LIGHT_GREEN = (100, 255, 100)
LIGHT_PURPLE = (200, 100, 255)
ORANGE = (255, 100, 0)
DARK_GREEN = (0, 200, 0)
DARK_RED = (200, 0, 0)


GRAVITY = 0.8
PLAYER_ACC = 0.6
PLAYER_FRICTION = -0.12
MAX_ENEMIES_CHASING = 5  


camera_x = 0


PLAYER_IMG = pygame.Surface((30, 40))
PLAYER_IMG.fill((50, 150, 255))  

PLAYER_HIT_IMG = pygame.Surface((30, 40))
PLAYER_HIT_IMG.fill(LIGHT_BLUE)

BULLET_IMG = pygame.Surface((10, 5))
BULLET_IMG.fill((0, 0, 0))  

ENEMY_IMG = pygame.Surface((30, 40))
ENEMY_IMG.fill((255, 50, 50))  

ENEMY_HIT_IMG = pygame.Surface((30, 40))
ENEMY_HIT_IMG.fill(LIGHT_RED)

RANGED_ENEMY_IMG = pygame.Surface((30, 40))
RANGED_ENEMY_IMG.fill((150, 50, 255))  

RANGED_ENEMY_HIT_IMG = pygame.Surface((30, 40))
RANGED_ENEMY_HIT_IMG.fill(LIGHT_PURPLE)

DUPLICATING_ENEMY_IMG = pygame.Surface((20, 30))
DUPLICATING_ENEMY_IMG.fill((50, 255, 50))  

DUPLICATING_ENEMY_HIT_IMG = pygame.Surface((20, 30))
DUPLICATING_ENEMY_HIT_IMG.fill(LIGHT_GREEN)

ENEMY_BULLET_IMG = pygame.Surface((10, 5))
ENEMY_BULLET_IMG.fill(ORANGE)  

enemies_chasing_player = 0


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = PLAYER_IMG
        self.hit_image = PLAYER_HIT_IMG
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT - 100)  
        self.pos = pygame.math.Vector2(100, HEIGHT - 100)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self.health = 100
        self.facing = 1  
        self.jump_count = 0  
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 300 
        self.weapon = 1  
        self.hit = False
        self.hit_time = 0  
        self.hit_duration = 100  

    def move(self):
        self.acc = pygame.math.Vector2(0, GRAVITY)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            self.facing = -1
        if keys[pygame.K_RIGHT]:
            self.acc.x = PLAYER_ACC
            self.facing = 1

        
        self.acc.x += self.vel.x * PLAYER_FRICTION

       
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        self.rect.midbottom = self.pos  

    def jump(self):
        if self.jump_count < 2:
            self.vel.y = -15  
            self.jump_count += 1
            self.on_ground = False

    def update(self):
        self.move()
        
        if self.hit and pygame.time.get_ticks() - self.hit_time > self.hit_duration:
            self.hit = False
            self.image = self.original_image

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.facing, self.weapon)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def switch_weapon(self):
        self.weapon += 1
        if self.weapon > 3:
            self.weapon = 1
        
        if self.weapon == 1:
            self.shoot_delay = 300
        elif self.weapon == 2:
            self.shoot_delay = 600
        elif self.weapon == 3:
            self.shoot_delay = 150

    def heal(self, amount):
        self.health += amount
        if self.health > 100:
            self.health = 100

    def take_damage(self, amount):
        if not self.hit:  
            self.health -= amount
            self.hit = True
            self.hit_time = pygame.time.get_ticks()
            self.image = self.hit_image

    def kill(self):
        self.health = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((100, 200, 100))  
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, stationary=False, can_jump=False, patrol_range=None, platform=None):
        super().__init__()
        self.original_image = ENEMY_IMG
        self.hit_image = ENEMY_HIT_IMG
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self.start_pos = pygame.math.Vector2(x, y)
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, GRAVITY)
        self.health = 300  
        self.on_ground = False
        self.stationary = stationary
        self.can_jump = can_jump
        self.jump_timer = 0  
        self.patrol_direction = 1
        self.platform = platform
        if patrol_range is not None:
            self.patrol_range = patrol_range
        else:
            self.patrol_distance = 50
            self.patrol_range = (self.start_pos.x - self.patrol_distance, self.start_pos.x + self.patrol_distance)
        self.is_chasing = False  
        self.hit = False
        self.hit_time = 0
        self.hit_duration = 100  

    def update(self):
        if not self.stationary:
            self.detect_player()
        else:
            self.patrol()
        self.apply_physics()
        if self.hit and pygame.time.get_ticks() - self.hit_time > self.hit_duration:
            self.hit = False
            self.image = self.original_image

    def detect_player(self):
        global enemies_chasing_player
        distance = player.pos.x - self.pos.x
        proximity = abs(distance) < WIDTH / 2 
        if proximity:
            if not self.is_chasing and enemies_chasing_player < MAX_ENEMIES_CHASING:
                self.is_chasing = True
                enemies_chasing_player += 1
            if self.is_chasing:
                self.chase_player()
            else:
                self.patrol()
        else:
            if self.is_chasing:
                self.is_chasing = False
                enemies_chasing_player = max(0, enemies_chasing_player - 1)
            self.patrol()

    def chase_player(self):
        distance = player.pos.x - self.pos.x
        self.acc.x = (PLAYER_ACC - 0.2) * (1 if distance > 0 else -1)  

    def patrol(self):
        if self.pos.x <= self.patrol_range[0]:
            self.patrol_direction = 1
        elif self.pos.x >= self.patrol_range[1]:
            self.patrol_direction = -1
        self.acc.x = (PLAYER_ACC - 0.4) * self.patrol_direction

    def apply_physics(self):
        self.acc.x += self.vel.x * PLAYER_FRICTION

        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        self.rect.midbottom = self.pos  
        
        if not self.stationary:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:
                self.pos.y = hits[0].rect.top + 1
                self.vel.y = 0
                self.on_ground = True
                self.jump_count = 0  
            else:
                self.on_ground = False
        else:
            
            self.vel.y = 0
            self.acc.y = 0
            self.pos.y = self.platform.rect.top + 1
            self.rect.midbottom = self.pos

       
        if self.can_jump and not self.stationary and self.on_ground:
            self.jump_timer += 1
            if self.jump_timer > 120:  
                self.vel.y = -12  
                self.jump_timer = 0

    def take_damage(self, amount):
        self.health -= amount
        self.hit = True
        self.hit_time = pygame.time.get_ticks()
        self.image = self.hit_image

    def kill(self):
        global enemies_chasing_player
        if self.is_chasing:
            self.is_chasing = False
            enemies_chasing_player = max(0, enemies_chasing_player - 1)
        super().kill()


class RangedEnemy(Enemy):
    def __init__(self, x, y, stationary=False, can_jump=False, patrol_range=None, platform=None):
        super().__init__(x, y, stationary, can_jump, patrol_range, platform)
        self.original_image = RANGED_ENEMY_IMG
        self.hit_image = RANGED_ENEMY_HIT_IMG
        self.image = self.original_image
        self.shoot_delay = 1600  
        self.last_shot = pygame.time.get_ticks()
        self.is_chasing = False  

    def update(self):
        if not self.stationary:
            self.patrol()
        else:
            self.patrol()
        self.apply_physics()
        self.shoot()
        
        if self.hit and pygame.time.get_ticks() - self.hit_time > self.hit_duration:
            self.hit = False
            self.image = self.original_image

    def shoot(self):
        now = pygame.time.get_ticks()
        if abs(player.pos.x - self.pos.x) < 400 and now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            direction = 1 if player.pos.x > self.pos.x else -1
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, direction)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def take_damage(self, amount):
        self.health -= amount
        self.hit = True
        self.hit_time = pygame.time.get_ticks()
        self.image = self.hit_image


class DuplicatingEnemy(Enemy):
    initial_total = 0  

    def __init__(self, x, y):
        super().__init__(x, y, stationary=False, can_jump=False)
        self.original_image = DUPLICATING_ENEMY_IMG
        self.hit_image = DUPLICATING_ENEMY_HIT_IMG
        self.image = self.original_image
        self.health = 20
        self.speed = PLAYER_ACC*1.1  
        self.patrol_distance = 30
        self.patrol_range = (self.start_pos.x - self.patrol_distance, self.start_pos.x + self.patrol_distance)
        self.duplication_timer = 2000  
        self.last_duplication_time = pygame.time.get_ticks()

    def update(self):
        self.detect_player()
        self.apply_physics()
        self.duplicate()
        
        if self.hit and pygame.time.get_ticks() - self.hit_time > self.hit_duration:
            self.hit = False
            self.image = self.original_image

    def duplicate(self):
        now = pygame.time.get_ticks()
        if now - self.last_duplication_time > self.duplication_timer:
            if len(duplicating_enemies) < DuplicatingEnemy.initial_total:
                new_enemy = DuplicatingEnemy(self.pos.x + random.choice([-30, 30]), self.pos.y)
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)
                duplicating_enemies.add(new_enemy)
                self.last_duplication_time = now

    def take_damage(self, amount):
        self.health -= amount
        self.hit = True
        self.hit_time = pygame.time.get_ticks()
        self.image = self.hit_image

    def kill(self):
        global enemies_chasing_player
        if self.is_chasing:
            self.is_chasing = False
            enemies_chasing_player = max(0, enemies_chasing_player - 1)
        super().kill()
        duplicating_enemies.remove(self)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1, weapon=1):
        super().__init__()
        if weapon == 1:
            self.image = pygame.Surface((10, 5))
            self.image.fill((0, 0, 0))  
            self.damage = 40
            self.speed = 18
        elif weapon == 2:
            self.image = pygame.Surface((15, 7))
            self.image.fill(DARK_RED)  
            self.damage = 80
            self.speed = 12
        elif weapon == 3:
            self.image = pygame.Surface((7, 3))
            self.image.fill(DARK_GREEN)  
            self.damage = 20
            self.speed = 15
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.start_pos = pygame.math.Vector2(x, y)  
        self.vel = pygame.math.Vector2(self.speed * direction, 0)

    def update(self):
        self.rect.x += self.vel.x
        if self.rect.right < 0 or self.rect.left > WIDTH * 5:
            self.kill()
        distance_traveled = abs(self.rect.centerx - self.start_pos.x)
        if distance_traveled > MAX_BULLET_RANGE:
            self.kill()
        
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1):
        super().__init__()
        self.image = ENEMY_BULLET_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel = pygame.math.Vector2(12 * direction, 0)

    def update(self):
        self.rect.x += self.vel.x
        
        if self.rect.right < 0 or self.rect.left > WIDTH * 5:
            self.kill()


all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
duplicating_enemies = pygame.sprite.Group()


player = Player()
all_sprites.add(player)


ground_platforms = [
    (0, HEIGHT - 30, 500, 40),
    (500, HEIGHT - 60, 500, 60),
    (1000, HEIGHT - 40, 500, 50),
    (1500, HEIGHT - 70, 500, 70),
    (2000, HEIGHT - 50, 500, 60),
]


platform_list = [
    *ground_platforms,
    (300, HEIGHT - 200, 150, 20),
    (800, HEIGHT - 250, 150, 20),
    (1300, HEIGHT - 200, 150, 20),
    (1800, HEIGHT - 250, 150, 20),
]

for plat in platform_list:
    p = Platform(*plat)
    all_sprites.add(p)
    platforms.add(p)


    enemy_type = random.choice(['ranged', 'regular'])
    if enemy_type == 'ranged':
        enemy = RangedEnemy(random.randint(1000, WIDTH * 3), HEIGHT - 100)
    else:
        enemy = Enemy(random.randint(1000, WIDTH * 3), HEIGHT - 100, can_jump=True)
    all_sprites.add(enemy)
    enemies.add(enemy)


for plat in platforms:
    if plat.rect.y < HEIGHT - 100:
        enemy_type = random.choice(['ranged', 'regular'])
        patrol_range = (plat.rect.left, plat.rect.right)
        if enemy_type == 'ranged':
            enemy = RangedEnemy(plat.rect.centerx, plat.rect.top + 1, stationary=True, patrol_range=patrol_range, platform=plat)
        else:
            enemy = Enemy(plat.rect.centerx, plat.rect.top + 1, stationary=True, patrol_range=patrol_range, platform=plat)
        all_sprites.add(enemy)
        enemies.add(enemy)


number_of_duplicating_enemies = 15  
for i in range(number_of_duplicating_enemies):
    enemy = DuplicatingEnemy(random.randint(800, WIDTH * 3), HEIGHT - 100)
    all_sprites.add(enemy)
    enemies.add(enemy)
    duplicating_enemies.add(enemy)

DuplicatingEnemy.initial_total = number_of_duplicating_enemies  


running = True
game_over = False
game_won = False
while running:
    clock.tick(FPS)

    if not game_over and not game_won:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_s:
                    player.switch_weapon()

        
        all_sprites.update()

        
        hits = pygame.sprite.spritecollide(player, platforms, False)
        if hits:
            player.pos.y = hits[0].rect.top + 1
            player.vel.y = 0
            player.on_ground = True
            player.jump_count = 0  
        else:
            player.on_ground = False

        
        if player.rect.top > HEIGHT:
            player.kill() 
            game_over = True

        
        enemy_hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy in enemy_hits:
            for bullet in enemy_hits[enemy]:
                enemy.take_damage(bullet.damage)
            if enemy.health <= 0:
                enemy.kill()
                if isinstance(enemy, DuplicatingEnemy):
                    duplicating_enemies.remove(enemy)
                else:
                    player.heal(2) 

      
        player_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if player_hits:
            player.take_damage(12)
            if player.health <= 0:
                game_over = True

        
        enemy_collision = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in enemy_collision:
            if isinstance(enemy, DuplicatingEnemy):
                player.take_damage(1.5) 
            else:
                player.take_damage(3) 
            if player.health <= 0:
                game_over = True

       
        camera_x = player.rect.centerx - WIDTH // 2

        
        if len(enemies) == 0:
            game_won = True

       
        SCREEN.fill(WHITE)
        for sprite in all_sprites:
            SCREEN.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

       
        font = pygame.font.Font(None, 36)
        health_text = font.render(f'Health: {int(player.health)}', True, BLACK)
        SCREEN.blit(health_text, (10, 10))

        weapon_text = font.render(f'Weapon: {player.weapon}', True, BLACK)
        SCREEN.blit(weapon_text, (10, 50))

        pygame.display.flip()

    elif game_over:
       
        SCREEN.fill(BLACK)
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, WHITE)
        SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height()))
        text = font.render("Press R to Restart", True, WHITE)
        SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + text.get_height()))
        pygame.display.flip()

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    enemies_chasing_player = 0
                    player = Player()
                    all_sprites = pygame.sprite.Group()
                    platforms = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()
                    bullets = pygame.sprite.Group()
                    enemy_bullets = pygame.sprite.Group()
                    duplicating_enemies = pygame.sprite.Group()

                    all_sprites.add(player)

                    for plat in platform_list:
                        p = Platform(*plat)
                        all_sprites.add(p)
                        platforms.add(p)

                    
                    for i in range(6):
                        enemy_type = random.choice(['ranged', 'regular'])
                        if enemy_type == 'ranged':
                            enemy = RangedEnemy(random.randint(1000, WIDTH * 3), HEIGHT - 100)
                        else:
                            enemy = Enemy(random.randint(1000, WIDTH * 3), HEIGHT - 100, can_jump=True)
                        all_sprites.add(enemy)
                        enemies.add(enemy)

                    for plat in platforms:
                        if plat.rect.y < HEIGHT - 100:
                            enemy_type = random.choice(['ranged', 'regular'])
                            patrol_range = (plat.rect.left, plat.rect.right)
                            if enemy_type == 'ranged':
                                enemy = RangedEnemy(plat.rect.centerx, plat.rect.top + 1, stationary=True, patrol_range=patrol_range, platform=plat)
                            else:
                                enemy = Enemy(plat.rect.centerx, plat.rect.top + 1, stationary=True, patrol_range=patrol_range, platform=plat)
                            all_sprites.add(enemy)
                            enemies.add(enemy)

                    number_of_duplicating_enemies = 16
                    for i in range(number_of_duplicating_enemies):
                        enemy = DuplicatingEnemy(random.randint(800, WIDTH * 3), HEIGHT - 100)
                        all_sprites.add(enemy)
                        enemies.add(enemy)
                        duplicating_enemies.add(enemy)

                    DuplicatingEnemy.initial_total = number_of_duplicating_enemies 
                    enemies_chasing_player = 0 

                    game_over = False

    elif game_won:
        SCREEN.fill(BLACK)
        font = pygame.font.Font(None, 74)
        text = font.render("You Won!", True, WHITE)
        SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height()))
        text = font.render("Press R to Restart", True, WHITE)
        SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + text.get_height()))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    enemies_chasing_player = 0
                    player = Player()
                    all_sprites = pygame.sprite.Group()
                    platforms = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()
                    bullets = pygame.sprite.Group()
                    enemy_bullets = pygame.sprite.Group()
                    duplicating_enemies = pygame.sprite.Group()

                    all_sprites.add(player)

                    for plat in platform_list:
                        p = Platform(*plat)
                        all_sprites.add(p)
                        platforms.add(p)

                   
                    for i in range(8):
                        enemy_type = random.choice(['ranged', 'regular'])
                        if enemy_type == 'ranged':
                            enemy = RangedEnemy(random.randint(1000, WIDTH * 3), HEIGHT - 100)
                        else:
                            enemy = Enemy(random.randint(1000, WIDTH * 3), HEIGHT - 100, can_jump=True)
                        all_sprites.add(enemy)
                        enemies.add(enemy)

                    for plat in platforms:
                        if plat.rect.y < HEIGHT - 100:
                            enemy_type = random.choice(['ranged', 'regular'])
                            patrol_range = (plat.rect.left, plat.rect.right)
                            if enemy_type == 'ranged':
                                enemy = RangedEnemy(plat.rect.centerx, plat.rect.top + 1, stationary=True, patrol_range=patrol_range, platform=plat)
                            else:
                                enemy = Enemy(plat.rect.centerx, plat.rect.top + 1, stationary=True, patrol_range=patrol_range, platform=plat)
                            all_sprites.add(enemy)
                            enemies.add(enemy)

                    number_of_duplicating_enemies = 14
                    for i in range(number_of_duplicating_enemies):
                        enemy = DuplicatingEnemy(random.randint(800, WIDTH * 3), HEIGHT - 100)
                        all_sprites.add(enemy)
                        enemies.add(enemy)
                        duplicating_enemies.add(enemy)

                    DuplicatingEnemy.initial_total = number_of_duplicating_enemies  
                    enemies_chasing_player = 0  
                    game_won = False

pygame.quit()
