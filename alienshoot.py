import json
import pygame
import random
from sys import exit
from threading import Timer
import pymunk

# Standard Initial Setup
pygame.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jet Fighter")


class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def reset_plane(self):

        self.plane_angle = 0
        self.plane_surface_1 = pygame.image.load('assets/images/plane/Fly_1.png').convert_alpha()
        self.plane_surface_2 = pygame.image.load('assets/images/plane/Fly_2.png').convert_alpha()
        self.plane_flying = [self.plane_surface_1,
                             self.plane_surface_2]  # Switch between these two surfaces in the animation loop
        self.plane_flying_index = 0
        self.rect = self.plane_flying[self.plane_flying_index].get_rect(center=(200, HEIGHT / 2))

        # Plane shooting sprites
        self.plane_shooting_surface_1 = pygame.image.load('assets/images/plane/Shoot_1.png').convert_alpha()
        self.plane_shooting_surface_2 = pygame.image.load('assets/images/plane/Shoot_2.png').convert_alpha()
        self.plane_shooting_surface_3 = pygame.image.load('assets/images/plane/Shoot_3.png').convert_alpha()
        self.plane_shooting_surface_4 = pygame.image.load('assets/images/plane/Shoot_4.png').convert_alpha()
        self.plane_shooting_surface_5 = pygame.image.load('assets/images/plane/Shoot_5.png').convert_alpha()
        self.plane_shooting_list = [self.plane_shooting_surface_1, self.plane_shooting_surface_2,
                                    self.plane_shooting_surface_3, self.plane_shooting_surface_4,
                                    self.plane_shooting_surface_5]
        self.plane_shooting_index = 0

        # Used to create a pause between shooting
        self.last = pygame.time.get_ticks()
        self.bullet_cooldown = 100

        self.plane_speed = 10
        # self.plane_gravity = 0
        self.plane_shooting = False


    def animation(self):
        # Increase the index to eventually change indexes to the next surface and then reset it back to zero.
        self.plane_flying_index += 0.1
        if self.plane_flying_index >= len(self.plane_flying):
            self.plane_flying_index = 0

        if self.plane_shooting:
            self.plane_shooting_index += 0.3
            if self.plane_shooting_index >= len(self.plane_shooting_list):
                self.plane_shooting_index = 0

    def display_plane(self):

        self.rotated_plane = pygame.transform.rotozoom(self.plane_flying[int(self.plane_flying_index)],
                                                       self.plane_angle, 1)

        if self.plane_shooting:
            self.rotated_plane = pygame.transform.rotozoom(self.plane_shooting_list[int(self.plane_shooting_index)],
                                                           self.plane_angle, 1)
        screen.blit(self.rotated_plane, self.rect)

    def shoot(self):
        self.plane_shooting = True  # Changes the sprites to the shooting sprites in display_plane()
        # Create bullet and add it to the bullet sprite group which is updated in the main loop
        # Fire gun only if cooldown has been 0.3 seconds since last
        now = pygame.time.get_ticks()
        if now - self.last >= self.bullet_cooldown:
            self.last = now
            weapons_group.add(Bullet(self.rect.right, self.rect.centery + 23))
            score.bullets_fired(1)

    # Set to false on each loop in the main loop. This is only set to true when the space bar is pressed so our
    # planes shooting animation can trigger
    def set_shooting(self, shooting):
        self.plane_shooting = shooting

    # Can call this method to change the rotation of the plane when moving
    def rotate_plane(self, direction):
        self.plane_angle += direction
        if self.plane_angle <= -20:
            self.plane_angle = -20
        if self.plane_angle >= 20:
            self.plane_angle = 20

    def move_plane(self, keys):
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.centery += self.get_plane_speed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.centery -= self.get_plane_speed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.centerx -= self.get_plane_speed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.centerx += self.get_plane_speed()

    def machine_gun_fire(self, keys):
        # Spray bullets
        if machine_gun_ammunition:
            if keys[pygame.K_SPACE]:
                self.shoot()
                machine_gun_ammunition.pop() # Remove bullet from list when fired


    def get_plane_speed(self):
        return self.plane_speed

    def set_plane_speed(self, speed):
        self.plane_speed = speed

    def update(self):
        self.animation()
        self.display_plane()
        self.set_shooting(False)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/images/bullet.png').convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.bullet_speed = 20

        self.x_pos = x
        self.y_pos = y

    def update(self):
        # pygame.draw.circle(screen, pygame.Color('Black'), ( self.x_pos, self.y_pos), 5)
        # self.x_pos += 20

        self.rect.x += self.bullet_speed
        if self.rect.x > WIDTH - 50:  # Destroy the bullet object once its at the edge of the screen
            self.kill()
        screen.blit(self.image, self.rect)

class Machine_gun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed = 5

        self.image = pygame.transform.scale(pygame.image.load('assets/images/machine_gun.png').convert_alpha(), (140,70))
        self.rect = self.image.get_rect(midright=(random.randint(WIDTH//2 + self.image.get_rect().width, WIDTH), -10))
        # self.rect = self.image.get_rect(midleft=(WIDTH + 10, random.randint(70, HEIGHT - 30)))


    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT + 50:  # Destroy object once left the screen
            self.kill()
            print("MACHINE GUN GO BANG BANG")



class Flying_Saucer(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.transform.rotozoom(pygame.image.load('assets/images/enemies/flying_saucer.png').convert_alpha(), 16,
                                      1), (200, 150))
        self.rect = self.image.get_rect(midleft=(WIDTH + random.randint(1, 10000), random.randint(70, HEIGHT - 30)))
        self.flying_saucer_speed = speed

    def update(self):
        self.rect.x -= self.flying_saucer_speed
        if self.rect.x < -200:  # Destroy object once left the screen
            self.kill()
            score.enemies_escaped(1)
            score.subtract_score(3)

# Monster Chases Player
class Monster(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


        self.speed = random.randint(5, 15)
        self.image = pygame.transform.scale(pygame.image.load('assets/images/enemies/monster.png').convert_alpha(), (200, 150))
        self.rect = self.image.get_rect(center=(WIDTH + random.randint(1, 10000), random.randint(70, HEIGHT - 30)))

    def update(self):
        # Find direction vector (dx, dy) between enemy and player.
        dirvect = pygame.math.Vector2(plane.rect.x - self.rect.x, plane.rect.y - self.rect.y)
        dirvect.normalize()
        # Move along this normalized vector towards the player at current speed.
        dirvect.scale_to_length(self.speed)
        self.rect.move_ip(dirvect)

        if self.rect.x < -200:
            self.kill()
            score.enemies_escaped(1)
            score.subtract_score(3)


# Called when Plane hits a health pack. Displays the health above the player and moves it upwards off the screen
# Could make this lower its opacity as it moves upwards at some point
class Health_Update_Display(pygame.sprite.Sprite):
    def __init__(self, points, color, x, y):
        super().__init__()

        self.x = x
        self.y = y
        self.points = points # Needs to be int
        self.color = color # Needs to be tuple
        self.speed = 3
        self.points_font = pygame.font.SysFont('Ariel', 50, True, False)
        self.points_surface = self.points_font.render("+" + str(self.points), False, self.color)
        self.rect = self.points_surface.get_rect(center=(self.x, self.y))



    def update(self):
        screen.blit(self.points_surface, self.rect)
        self.rect.y -= self.speed
        if self.rect.y < -100:
            self.kill()


class Score(object):
    def __init__(self):
        super().__init__()

        # Machine Gun Bullet Display
        self.bullet_font = pygame.font.SysFont('Arial', 50, True, False)
        self.bullet_surface = self.bullet_font.render(str(len(machine_gun_ammunition)), False, (255, 0, 0))
        self.bullet_font_rect = self.bullet_surface.get_rect(midleft=(30, HEIGHT - 40))

        # Dictionary for the JSON file to save high score and stats
        self.data = {
            'high_score': 0,
            'enemies_escaped': 0,
            'bullets_fired': 0,
            'total_health_lost': 0,
            'health_packs_acquired': 0,
            'total_health_gained': 0,
            'enemies_killed': 0
        }
        try:
            with open('High_Score.txt') as score_file:
                self.data = json.load(score_file)
        except:
            print("No file created yet. Will be created on game close :)")

    def reset_score(self):
        self.score = 0
        self.score_font = pygame.font.SysFont('Arial', 50, True, False)
        self.score_surface = self.score_font.render(f'Score {str(self.score)}', False, (0, 0, 0))
        self.score_rect = self.score_surface.get_rect(center=(WIDTH / 2, 50))

        self.high_score_font = pygame.font.SysFont('Arial', 25, True, False)
        self.high_score_surface = self.high_score_font.render(f'High Score {self.data["high_score"]}', False,
                                                              (255, 0, 0))
        self.high_score_rect = self.high_score_surface.get_rect(topleft=(5, 5))

        # Stats Tracking
        self.enemies_escaped_ = self.data["enemies_escaped"]
        self.bullets_fired_ = self.data["bullets_fired"]
        self.total_health_lost_ = self.data["total_health_lost"]
        self.health_packs_acquired_ = self.data["health_packs_acquired"]
        self.total_health_gained_ = self.data["total_health_gained"]
        self.enemies_killed_ = self.data["enemies_killed"]

    def update_score(self, points):
        self.score += points
        self.score_surface = self.score_font.render(f'Score {str(self.score)}', False, (0, 0, 0))
        # Only update the high score if it is higher than the current score. Update happens via the dictionary for saving on game close
        if self.score > self.data["high_score"]:
            self.data["high_score"] = self.score
            self.high_score_surface = self.high_score_font.render(f'High Score {self.data["high_score"]}', False,
                                                                  (0, 255, 0))

    # Called in main game instance
    def display_machine_gun_bullets(self):
        if machine_gun_ammunition:
            self.bullet_surface = self.bullet_font.render(str(len(machine_gun_ammunition)), False, (255, 0, 0))
            screen.blit(self.bullet_surface, self.bullet_font_rect)


    def subtract_score(self, points):
        if self.score > 0 and self.score - points > 0:
            self.score -= points
            self.score_surface = self.score_font.render(f'Score {str(self.score)}', False, (0, 0, 0))
        else:
            game_state.set_game_state("game_over_screen")


    def get_enemies_escape(self):
        return self.enemies_escaped_

    def get_bullets_fired(self):
        return self.bullets_fired_

    def get_health_lost(self):
        return self.total_health_lost_

    def get_health_packs(self):
        return self.health_packs_acquired_

    def get_total_health_gained(self):
        return self.total_health_gained_

    def get_enemies_killed(self):
        return self.enemies_killed_

    # Called on game close
    def save_high_score(self):
        with open('High_Score.txt', 'w') as score_file:
            json.dump(self.data, score_file)
        score_file.close()

    def enemies_escaped(self, escaped):
        self.enemies_escaped_ += escaped
        self.data["enemies_escaped"] += escaped
        print(f'Enemies escaped: {self.enemies_escaped_}')

    def bullets_fired(self, fired):
        self.bullets_fired_ += fired
        self.data["bullets_fired"] += fired
        print(f'Bullets Fired: {self.bullets_fired_}')

    def health_lost(self, lost):
        self.total_health_lost_ += lost
        self.data["total_health_lost"] += lost
        print(f'Total Health Lost: {self.total_health_lost_}')

    def health_packs(self, packs):
        self.health_packs_acquired_ += packs
        self.data["health_packs_acquired"] += packs
        print(f'Health Packs Acquired: {self.health_packs_acquired_}')

    def total_health_gained(self, gained):
        self.total_health_gained_ += gained
        self.data["total_health_gained"] += gained
        print(f'Total Health Gained: {self.total_health_gained_}')

    def enemies_killed(self, killed):
        self.enemies_killed_ += killed
        self.data["enemies_killed"] += killed
        print(f'Enemies killed: {self.enemies_killed_}')

    def display_score(self):
        screen.blit(self.score_surface, self.score_rect)  # Current Score
        screen.blit(self.high_score_surface, self.high_score_rect)  # High Score


class Background(object):
    def __init__(self):
        super().__init__()
        # Images/Surfaces
        self.background_speed = 1
        self.background_surface = pygame.image.load('assets/images/clouds.png').convert_alpha()
        self.background_rect = self.background_surface.get_rect(topleft=(0, 0))
        self.background_rect2 = self.background_surface.get_rect(topleft=(WIDTH, 0))

    # Move the background
    def update(self):
        self.background_x_pos = self.background_rect.midright[
            0]  # Get the X position of the mid right of background one
        self.background2_x_pos = self.background_rect2.midright[
            0]  # Get the X position of the mid right of background two

        # Move them to the left
        self.background_rect.centerx -= self.background_speed
        self.background_rect2.centerx -= self.background_speed
        # When the right side of either backgrounds reaches the left side of the screen, move the backgrounds left side
        # to the right side of the screen
        if self.background_x_pos <= 1:
            self.background_rect = self.background_surface.get_rect(topleft=(WIDTH, 0))
        if self.background2_x_pos <= 1:
            self.background_rect2 = self.background_surface.get_rect(topleft=(WIDTH, 0))

        screen.blit(self.background_surface, self.background_rect)
        screen.blit(self.background_surface, self.background_rect2)


class HealthBar(object):
    def __init__(self):
        super().__init__()

        self.healthbar_total = plane.rect.width
        self.current_health = self.healthbar_total

    def reset_health(self):
        self.healthbar_total = plane.rect.width
        self.current_health = self.healthbar_total

    def get_current_health(self):
        return self.current_health

    def hit(self, damage):
        if self.current_health > 0:
            self.current_health -= damage
            if self.current_health <= 0:
                game_state.set_game_state("game_over_screen")


    def add_health(self, health_pack):
        if self.current_health < self.healthbar_total:  # Only add health if the current health is not 100%
            if self.current_health + health_pack > self.healthbar_total:  # If adding health goes over the max health then subtract it accordingly. This could also be done by just setting health to the max.
                test = (self.healthbar_total - self.current_health) - health_pack
                print(f"HEALTH APPLIED: {test}")
                self.current_health += (self.healthbar_total - self.current_health) - health_pack
            self.current_health += health_pack
            print(f"HEALTH APPLIED {health_pack}")

    def display(self):
        # Health bar, Black border, Green ontop of a red rectangle
        pygame.draw.rect(screen, (0, 0, 0), (plane.rect.x, plane.rect.y - 20, self.healthbar_total, 10), 4)
        pygame.draw.rect(screen, (255, 0, 0), (plane.rect.x, plane.rect.y - 20, self.healthbar_total, 10))
        pygame.draw.rect(screen, (0, 255, 0), (plane.rect.x, plane.rect.y - 20, self.current_health, 10))


# Coloured Healthpacks inherit from this main Parent Sprite Class
class HealthPacks(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.healthpack_color = ""

    # Used to update healthbar correctly when player collides with healthpack
    def get_health_pack_color(self):
        return self.healthpack_color

    def get_random_health_pack(self):
        rand = random.randint(1, 3)
        if rand == 1:
            healthpack = HealthPackGreen()
            self.healthpack_color = "green"
            return healthpack

        elif rand == 2:
            healthpack = HealthPackYellow()
            self.healthpack_color = "yellow"
            return healthpack
        else:
            healthpack = HealthPackRed()
            self.healthpack_color = "red"
            return healthpack

    def update(self):
        self.rect.y += 2.5
        if self.rect.top > HEIGHT + 100:
            self.kill()


class HealthPackGreen(HealthPacks):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('assets/images/healthpack_green.png').convert_alpha(),
                                            (50, 50))
        self.rect = self.image.get_rect(
            midbottom=(random.randint(900, WIDTH), 0))  # Spawn in the last quarter of the screen

    def get_x_and_y(self):
        return self.rect.x, self.rect.y

class HealthPackYellow(HealthPacks):
    def __init__(self):
        super().__init__()

        self.image = pygame.transform.scale(pygame.image.load('assets/images/healthpack_yellow.png').convert_alpha(),
                                            (50, 50))
        self.rect = self.image.get_rect(midbottom=(
            random.randint(500, WIDTH), 0))  # Spawn inbetween one quarter of the screen to the third of the screen

    def get_x_and_y(self):
        return self.rect.x, self.rect.y

class HealthPackRed(HealthPacks):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('assets/images/healthpack_red.png').convert_alpha(),
                                            (50, 50))
        self.rect = self.image.get_rect(midbottom=(random.randint(950, WIDTH), 0))

    def get_x_and_y(self):
        return self.rect.x, self.rect.y


class Collisions():
    def __init__(self):
        super().__init__()

    # Plane runs into top or sides
    def border_collisions(self):
        # Plane Border Collisions
        if plane.rect.top - 20 <= 0: plane.rect.top = 20
        if plane.rect.bottom > HEIGHT: plane.rect.bottom = HEIGHT
        if plane.rect.left <= 0: plane.rect.left = 0
        if plane.rect.right >= WIDTH: plane.rect.right = WIDTH

    # Plane shoots enemy
    def bullets_and_enemies(self):
        for weapon in weapons_group:
            for enemy in enemies_group:
                # Update this with the l33t collisions detections from Clear Code channel
                if enemy.rect.left <= weapon.rect.right - 100 and enemy.rect.top + 50 <= weapon.rect.bottom and enemy.rect.bottom - 50 >= weapon.rect.top:
                    particles_group.add(Explosions(enemy.rect.x, enemy.rect.y))
                    enemy.kill()
                    weapon.kill()
                    score.enemies_killed(1)
                    score.update_score(1)

    # Enemy hits plane
    def enemy_and_plane(self):
        for enemy in enemies_group:
            if enemy.rect.left <= plane.rect.right - 100 and enemy.rect.right >= plane.rect.left + 80 and enemy.rect.top + 80 <= plane.rect.bottom and enemy.rect.bottom - 50 >= plane.rect.top:
                enemy.kill()
                score.subtract_score(1)
                score.health_lost(25)
                healthbar.hit(25)
                particles_group.add(Explosions(enemy.rect.x, enemy.rect.y))

    def machine_gun(self):
        if pygame.sprite.spritecollide(plane, machine_gun_group, True):
            for num in range(0, 250): # Ammount of bullets to add
                machine_gun_ammunition.append(Bullet(plane.rect.x, plane.rect.y)) # Populate the machine gun with 50 bullets


    # Plane collides with Healthpack
    def health_packs(self):
        if pygame.sprite.spritecollide(plane, health_group, True):
            if health.get_health_pack_color() == "green":
                healthbar.add_health(15)
                score.update_score(5)
                score.total_health_gained(15)
                health_update_display.add(Health_Update_Display(15, 'Green', plane.rect.x, plane.rect.y))
            if health.get_health_pack_color() == "yellow":
                healthbar.add_health(10)
                score.total_health_gained(10)
                score.update_score(2)
                health_update_display.add(Health_Update_Display(10, 'Yellow', plane.rect.x, plane.rect.y))
            if health.get_health_pack_color() == "red":
                score.update_score(2)
                score.total_health_gained(5)
                healthbar.add_health(5)
                health_update_display.add(Health_Update_Display(5, 'Red', plane.rect.x, plane.rect.y))
            score.health_packs(1)

class Explosions(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.particles = []
        self.colors = [pygame.Color('Red'), pygame.Color('Yellow'), pygame.Color('Orange')]
        self.random_color = random.randint(0, 2)
        # self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]
        self.pos_x = pos_x
        self.pos_y = pos_y

        Timer(0.3, self.kill).start()  # Explosion Timer

    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0][0] += particle[1][0]  # pos_x += direction_x
                particle[0][1] += particle[1][1]  # pos_y += direction_y
                particle[2] -= 1  # Shrink Speed
                particle[1][1] += 0.0  # Gravity
                pygame.draw.circle(screen, self.colors[self.random_color],
                                   [int(particle[0][0]), int(particle[0][1])],
                                   int(particle[2]))  # screen, color, position, radius
                # if particle[2] <= 0:
                #      self.particles.remove(particle)

    def add_particles(self):

        # self.pos_x = plane.rect.x
        # self.pos_y = plane.rect.y
        self.direction_x = random.randint(-100, 100) / 10 - 1
        self.direction_y = random.randint(-100, 100) / 10 - 1
        self.radius = random.randint(10, 40)

        self.particle_circle = [[self.pos_x, self.pos_y], [self.direction_x, self.direction_y], self.radius]
        self.particles.append(self.particle_circle)

    def delete_particles(self):
        self.particles_copy = [particle for particle in self.particles if particle[2] > 0]
        self.particles = self.particles_copy

    def update(self):
        self.add_particles()
        self.emit()


# Smoke emiting from plane. Could use explosion class but just wanted to get this working first
class Smoke():
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.particles = []
        # self.colors = [pygame.Color('Red'), pygame.Color('Yellow'), pygame.Color('Orange')]
        # self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]
        self.pos_x = pos_x
        self.pos_y = pos_y

    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0][0] += particle[1][0]  # pos_x += direction_x
                particle[0][1] += particle[1][1]  # pos_y += direction_y
                particle[2] -= 0.1  # Shrink Speed
                particle[1][1] += 0.0  # Gravity
                pygame.draw.circle(screen, pygame.Color('Black'),
                                   [int(particle[0][0]), int(particle[0][1])],
                                   int(particle[2]))  # screen, color, position, radius
                # if particle[2] <= 0:
                #      self.particles.remove(particle)

    def add_particles(self, pos_x, pos_y):

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.direction_x = random.randint(-5, 10) / 10 - 1
        self.direction_y = -2
        self.radius = random.randint(4, 6)

        self.particle_circle = [[self.pos_x, self.pos_y], [self.direction_x, self.direction_y], self.radius]
        self.particles.append(self.particle_circle)

    def delete_particles(self):
        self.particles_copy = [particle for particle in self.particles if particle[2] > 0]
        self.particles = self.particles_copy

    def update(self):
        # self.add_particles()
        self.emit()


class Title_menu():
    def __init__(self):
        self.title_font = pygame.font.SysFont('Ariel', 50, True, False) # Jet Fighter Title Font
        self.options_font = pygame.font.SysFont('Ariel', 40, True, False) # Options Font

        # Jet Fighter
        self.title_surface = self.title_font.render('JET FIGHTER', False, (0, 0, 0, 0))
        self.title_rect = self.title_surface.get_rect(center=(WIDTH / 2, 200))

        # Play
        self.play_surface = self.options_font.render('Play', False, (0, 0, 0, 0))
        self.play_rect = self.play_surface.get_rect(center=(WIDTH / 2, self.title_rect.bottom + 50))

        # How to play
        self.how_to_play_surface = self.options_font.render('How To Play', False, (0, 0, 0, 0))
        self.how_to_play_rect = self.how_to_play_surface.get_rect(center=(WIDTH / 2, self.play_rect.bottom + 50))

        # High Scores
        self.high_scores_surface = self.options_font.render('High Scores', False, (0, 0, 0, 0))
        self.high_scores_rect = self.high_scores_surface.get_rect(center=(WIDTH / 2, self.how_to_play_rect.bottom + 50))

        # Stats
        self.stats_surface = self.options_font.render('Stats', False, (0, 0, 0, 0))
        self.stats_rect = self.stats_surface.get_rect(center=(WIDTH / 2, self.high_scores_rect.bottom + 50))

        # Quit
        self.quit_surface = self.options_font.render('Quit', False, (0, 0, 0, 0))
        self.quit_rect = self.quit_surface.get_rect(center=(WIDTH / 2, self.stats_rect.bottom + 50))

    def display_title_screen(self):
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.play_surface, self.play_rect)
        screen.blit(self.how_to_play_surface, self.how_to_play_rect)
        screen.blit(self.high_scores_surface, self.high_scores_rect)
        screen.blit(self.stats_surface, self.stats_rect)
        screen.blit(self.quit_surface, self.quit_rect)

class How_to_play_menu():
    def __init__(self):
        self.title_font = pygame.font.SysFont('Ariel', 50, True, False)
        self.instructions_font = pygame.font.SysFont('Ariel', 40, True, False)
        self.title_surface = self.title_font.render('HOW TO PLAY', False, (0, 0, 0, 0))
        self.title_rect = self.title_surface.get_rect(center=(WIDTH / 2, 200))

        self.arrow_keys_surface = self.instructions_font.render("Use the arrow keys to move", False, (0, 0, 0, 0))
        self.arrow_keys_rect = self.arrow_keys_surface.get_rect(center=(WIDTH / 2, self.title_rect.bottom + 50))

        self.shoot_surface = self.instructions_font.render("Press space to shoot", False, (0, 0, 0, 0))
        self.shoot_rect = self.shoot_surface.get_rect(center=(WIDTH / 2, self.arrow_keys_rect.bottom + 50))

        self.score_surface = self.instructions_font.render("Keep the score above zero", False, (0, 0, 0, 0))
        self.score_rect = self.score_surface.get_rect(center=(WIDTH / 2, self.shoot_rect.bottom + 50))

        self.escape_surface = self.instructions_font.render("Try not to let enemies escape", False, (0, 0, 0, 0))
        self.escape_rect = self.escape_surface.get_rect(center=(WIDTH / 2, self.score_rect.bottom + 50))

        self.health_surface = self.instructions_font.render("Health packs increase score as well as add health", False, (0, 0, 0, 0))
        self.health_rect = self.health_surface.get_rect(center=(WIDTH / 2, self.escape_rect.bottom + 50))

        # Back Button
        self.back_surface = self.instructions_font.render("Back", False, (0, 0, 0, 0))
        self.back_rect = self.back_surface.get_rect(center=(WIDTH / 2, self.health_rect.bottom + 50))

    def display_how_to_play_menu(self):
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.arrow_keys_surface, self.arrow_keys_rect)
        screen.blit(self.shoot_surface, self.shoot_rect)
        screen.blit(self.score_surface, self.score_rect)
        screen.blit(self.escape_surface, self.escape_rect)
        screen.blit(self.health_surface, self.health_rect)
        screen.blit(self.back_surface, self.back_rect)


class High_score_menu():
    def __init__(self):
        self.title_font = pygame.font.SysFont('Ariel', 50, True, False)
        self.title_surface = self.title_font.render('HIGH SCORES', False, (0, 0, 0, 0))
        self.title_rect = self.title_surface.get_rect(center=(WIDTH / 2, 200))

    def display_high_score_menu(self):
        screen.blit(self.title_surface, self.title_rect)

class Stats_menu():
    def __init__(self):
        self.title_font = pygame.font.SysFont('Ariel', 50, True, False)
        self.options_font = pygame.font.SysFont('Ariel', 40, True, False)
        self.title_surface = self.title_font.render('STATS', False, (0, 0, 0, 0))
        self.title_rect = self.title_surface.get_rect(center=(WIDTH / 2, 200))

        # Bullets Fired
        self.bullets_fired_surface = self.options_font.render(f'Bullets Fired: {score.get_bullets_fired()}', False,(0, 0, 0, 0))
        self.bullets_fired_rect = self.bullets_fired_surface.get_rect(center=(WIDTH / 2, self.title_rect.bottom + 50))

        # Enemies Killed
        self.enemies_killed_surface = self.options_font.render(f'Enemies Killed: {score.get_enemies_killed()}', False, (0, 0, 0, 0))
        self.enemies_killed_rect = self.enemies_killed_surface.get_rect(center=(WIDTH / 2, self.bullets_fired_rect.bottom + 50))

        # Enemies Escaped
        self.enemies_escaped_surface = self.options_font.render(f'Enemies Escaped: {score.get_enemies_escape()}', False,(0, 0, 0, 0))
        self.enemies_escaped_rect = self.enemies_escaped_surface.get_rect(center=(WIDTH / 2, self.enemies_killed_rect.bottom + 50))

        # Health Packs Acquired
        self.health_packs_acquired_surface = self.options_font.render(f'Health Packs Acquired: {score.get_health_packs()}', False,(0, 0, 0, 0))
        self.health_packs_acquired_rect = self.health_packs_acquired_surface.get_rect(center=(WIDTH / 2, self.enemies_escaped_rect.bottom + 50))

        # Total Health Gained
        self.total_health_gained_surface = self.options_font.render(f'Total Health Gained: {score.get_total_health_gained()}', False, (0, 0, 0, 0))
        self.total_health_gained_rect = self.total_health_gained_surface.get_rect(center=(WIDTH / 2, self.health_packs_acquired_rect.bottom + 50))

        # Total Health Lost
        self.total_health_lost_surface = self.options_font.render(f'Total Health Lost: {score.get_health_lost()}', False, (0, 0, 0, 0))
        self.total_health_lost_rect = self.total_health_lost_surface.get_rect(center=(WIDTH / 2, self.total_health_gained_rect.bottom + 50))

        # Back Button
        self.back_surface = self.options_font.render("Back", False, (0, 0, 0, 0))
        self.back_rect = self.back_surface.get_rect(center=(WIDTH / 2, self.total_health_lost_rect.bottom + 50))


    def display_high_score_menu(self):
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.bullets_fired_surface, self.bullets_fired_rect)
        screen.blit(self.enemies_killed_surface, self.enemies_killed_rect)
        screen.blit(self.enemies_escaped_surface, self.enemies_escaped_rect)
        screen.blit(self.health_packs_acquired_surface, self.health_packs_acquired_rect)
        screen.blit(self.total_health_gained_surface, self.total_health_gained_rect)
        screen.blit(self.total_health_lost_surface, self.total_health_lost_rect)
        screen.blit(self.back_surface, self.back_rect)


class Game_over_screen():
    def __init__(self):
        self.title_font = pygame.font.SysFont('Ariel', 50, True, False) # Game Over Font
        self.options_font = pygame.font.SysFont('Ariel', 40, True, False)  # Options Font
        # Game Over
        self.title_surface = self.title_font.render('GAME OVER', False, (0, 0, 0, 0))
        self.title_rect = self.title_surface.get_rect(center=(WIDTH / 2, 200))

        self.play_again_surface = self.options_font.render('Play Again', False, (0, 0, 0, 0))
        self.play_again_rect = self.play_again_surface.get_rect(center=(WIDTH / 2, self.title_rect.bottom + 100))

        self.main_menu_surface = self.options_font.render('Main Menu', False, (0, 0, 0, 0))
        self.main_menu_rect = self.main_menu_surface.get_rect(center=(WIDTH / 2, self.play_again_rect.bottom + 50))


        self.quit_surface = self.options_font.render('Quit', False, (0, 0, 0, 0))
        self.quit_rect = self.quit_surface.get_rect(center=(WIDTH / 2, self.main_menu_rect.bottom + 50))


    def display_game_over_screen(self):
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.play_again_surface, self.play_again_rect)
        screen.blit(self.main_menu_surface, self.main_menu_rect)
        screen.blit(self.quit_surface, self.quit_rect)


class Game_State():
    def __init__(self):
        self.state = "title_menu"

    def set_game_state(self, state):
        self.state = state

    def main_game(self):
        screen.fill((0, 0, 0))
        pygame.mouse.set_visible(False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                score.save_high_score()
                pygame.quit()
                exit()

            # Need to add a method in the plane class to spray bullets or shoot single shots and link it to this statement.
            # Shoot single bullet
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    plane.shoot()
                if event.key == pygame.K_ESCAPE:
                    self.state = "title_menu"
                    enemies_group.empty()  # Remove enemy objects
                    score.reset_score()  # Resets score to zero
                    plane.reset_plane()
                    healthbar.reset_health()
                    health_group.empty()
                    machine_gun_group.empty()
                    machine_gun_ammunition.clear()


            # Spawn random enemies
            if event.type == spawn_enemy:
                enemies_group.add(Flying_Saucer(random.randint(5, 10)))
                random_enemy_spawn_time = random.randint(1000, 3500)  # Set new spawn time each time an enemy is spawned
                pygame.time.set_timer(spawn_monster, random_enemy_spawn_time)

            # Spawn Health Pack
            if event.type == spawn_health_pack:
                health_group.add(health.get_random_health_pack())

            # Add particles to the particle list
            if event.type == SMOKE_EVENT:
                smoke.add_particles(plane.rect.x + 10, plane.rect.y + 50)

            # Spawn Machine Gun
            if event.type == spawn_machine_gun:
                machine_gun_group.add(Machine_gun())


            # Spawn Monster
            if event.type == spawn_monster:
                enemies_group.add(Monster())
                random_monster_spawn_time = random.randint(5000, 30000)  # Set new spawn time each time an enemy is spawned
                pygame.time.set_timer(spawn_monster, random_monster_spawn_time)


        # Plane movement
        plane.move_plane(pygame.key.get_pressed())
        plane.machine_gun_fire(pygame.key.get_pressed())

        background.update()

        collisions.border_collisions()
        collisions.bullets_and_enemies()
        collisions.enemy_and_plane()
        collisions.health_packs()
        collisions.machine_gun()

        score.display_score()
        # Enemies
        enemies_group.draw(
            screen)  # These are not blitted to screen within their class update method because if I make multiple enemies then it is easier to just use this draw method for the entire sprite group
        enemies_group.update()

        # Health Packs
        health_group.draw(screen)
        health_group.update()

        # Player
        player_group.update()
        # Bullets
        weapons_group.update()
        # Points display
        health_update_display.update()


        machine_gun_group.update()
        machine_gun_group.draw(screen)

        # Display Machine Gun bullets when bullets in the list
        score.display_machine_gun_bullets()


        healthbar.display()

        particles_group.update()

        smoke.emit()
        pygame.display.update()

    def title_menu(self):
        screen.fill((0, 0, 0))
        pygame.mouse.set_visible(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                score.save_high_score()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.x_pos, self.y_pos = pygame.mouse.get_pos()
                # High Scores Button
                if self.x_pos < title_menu.high_scores_rect.right and self.x_pos > title_menu.high_scores_rect.left and self.y_pos > title_menu.high_scores_rect.top and self.y_pos < title_menu.high_scores_rect.bottom:
                    self.state = "high_score_menu"
                # Quit Button
                if self.x_pos < title_menu.quit_rect.right and self.x_pos > title_menu.quit_rect.left and self.y_pos > title_menu.quit_rect.top and self.y_pos < title_menu.quit_rect.bottom:
                    pygame.quit()
                    score.save_high_score()
                    exit()
                # Play Button
                if self.x_pos < title_menu.play_rect.right and self.x_pos > title_menu.play_rect.left and self.y_pos > title_menu.play_rect.top and self.y_pos < title_menu.play_rect.bottom:
                    self.state = "main_game"
                # Stats
                if self.x_pos < title_menu.stats_rect.right and self.x_pos > title_menu.stats_rect.left and self.y_pos > title_menu.stats_rect.top and self.y_pos < title_menu.stats_rect.bottom:
                    self.state = "stats_menu"
                # How to play
                if self.x_pos < title_menu.how_to_play_rect.right and self.x_pos > title_menu.how_to_play_rect.left and self.y_pos > title_menu.how_to_play_rect.top and self.y_pos < title_menu.how_to_play_rect.bottom:
                    self.state = "how_to_play_menu"

        background.update()

        title_menu.display_title_screen()
        pygame.display.update()

    def high_score_menu(self):
        screen.fill((0, 0, 0))
        pygame.mouse.set_visible(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                score.save_high_score()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.state = "title_menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.state = "title_menu"

        background.update()
        high_score_menu.display_high_score_menu()
        pygame.display.update()

    def stats_menu(self):
        screen.fill((0, 0, 0))
        pygame.mouse.set_visible(True)
        stats_menu = Stats_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                score.save_high_score()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.x_pos, self.y_pos = pygame.mouse.get_pos()
                if self.x_pos < stats_menu.back_rect.right and self.x_pos > stats_menu.back_rect.left and self.y_pos > stats_menu.back_rect.top and self.y_pos < stats_menu.back_rect.bottom:
                    self.state = "title_menu"
        background.update()
        stats_menu.display_high_score_menu()
        pygame.display.update()


    def how_to_play_menu(self):
        pygame.mouse.set_visible(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                score.save_high_score()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                #self.state = "title_menu"
                self.x_pos, self.y_pos = pygame.mouse.get_pos()
                if self.x_pos < how_to_play_menu.back_rect.right and self.x_pos > how_to_play_menu.back_rect.left and self.y_pos > how_to_play_menu.back_rect.top and self.y_pos < how_to_play_menu.back_rect.bottom:
                    self.state = "title_menu"

            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         self.state = "title_menu"

        background.update()
        how_to_play_menu.display_how_to_play_menu()
        pygame.display.update()

    def game_over_screen(self):
        #screen.fill((0, 0, 0))
        pygame.mouse.set_visible(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                score.save_high_score()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.x_pos, self.y_pos = pygame.mouse.get_pos()
                if self.x_pos < game_over_screen.play_again_rect.right and self.x_pos > game_over_screen.play_again_rect.left and self.y_pos > game_over_screen.play_again_rect.top and self.y_pos < game_over_screen.play_again_rect.bottom:
                    self.state = "main_game"
                if self.x_pos < game_over_screen.main_menu_rect.right and self.x_pos > game_over_screen.main_menu_rect.left and self.y_pos > game_over_screen.main_menu_rect.top and self.y_pos < game_over_screen.main_menu_rect.bottom:
                    self.state = "title_menu"
                if self.x_pos < game_over_screen.quit_rect.right and self.x_pos > game_over_screen.quit_rect.left and self.y_pos > game_over_screen.quit_rect.top and self.y_pos < game_over_screen.quit_rect.bottom:
                    score.save_high_score()
                    pygame.quit()
                    exit()

        background.update()
        game_over_screen.display_game_over_screen()
        pygame.display.update()


    def state_manager(self):
        if self.state == "main_game":
            self.main_game()
        if self.state == "title_menu":
            self.title_menu()
        if self.state == "high_score_menu":
            self.high_score_menu()
        if self.state == "stats_menu":
            self.stats_menu()
        if self.state == "game_over_screen":
            enemies_group.empty()  # Remove enemy objects
            score.reset_score()  # Resets score to zero
            plane.reset_plane()
            healthbar.reset_health()
            health_group.empty()
            machine_gun_group.empty()
            machine_gun_ammunition.clear()
            self.game_over_screen()
        if self.state == "how_to_play_menu":
            self.how_to_play_menu()


machine_gun_ammunition = []
machine_gun_group = pygame.sprite.Group()
# Spawn Machine gun timer
spawn_machine_gun = pygame.USEREVENT + 4
pygame.time.set_timer(spawn_machine_gun, random.randint(10000, 20000)) # Make this random once it works

health = HealthPacks()
random_enemy_spawn_time = 1000
spawn_enemy = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_enemy, random_enemy_spawn_time)


# Monster Spawn TEST
random_monster_spawn_time = random.randint(1000, 5000)
spawn_monster = pygame.USEREVENT +6
pygame.time.set_timer(spawn_monster, random_monster_spawn_time)


# Health pack spawning
spawn_health_pack = pygame.USEREVENT + 2
# pygame.time.set_timer(spawn_health_pack, 1000)
pygame.time.set_timer(spawn_health_pack, random.randint(10000, 20000))
# plane width 130


# Need to decrease the timer time to increase smoke
SMOKE_EVENT = pygame.USEREVENT + 3
pygame.time.set_timer(SMOKE_EVENT, 50)

# Score
score = Score()
score.reset_score()

#Points Group
health_update_display = pygame.sprite.Group()

collisions = Collisions()

# Menu Objects
game_state = Game_State()
title_menu = Title_menu()
high_score_menu = High_score_menu()
stats_menu = Stats_menu()
game_over_screen = Game_over_screen()
how_to_play_menu = How_to_play_menu()

# Plane
plane = Plane()
plane.reset_plane()
player_group = pygame.sprite.GroupSingle(plane)
# Bullet Group
weapons_group = pygame.sprite.Group()
# Enemies
enemies_group = pygame.sprite.Group()
# Background
background = Background()

# Particles Group
particles_group = pygame.sprite.Group()

# Smoke
smoke = Smoke(plane.rect.x, plane.rect.y)

# Health Bar
healthbar = HealthBar()

# Health Items
health_group = pygame.sprite.Group()

# Main Game Loop
while True:
    game_state.state_manager()

    clock.tick(120)
