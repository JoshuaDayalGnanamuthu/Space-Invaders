import pygame
import sys
import random

pygame.init()


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Space Invaders')
        self.icon = pygame.image.load(r'.venv\icons\ufo.png')
        pygame.display.set_icon(self.icon)
        self.clock = pygame.time.Clock()

        self.PlayerImg = pygame.image.load(r'\icons\spaceship.png')
        self.AlienImg = pygame.image.load(r'.venv\icons\alien.png')
        self.BulletImg = pygame.image.load(r'.venv\icons\bullet.png')
        self.SatelliteImg = pygame.image.load(r'.venv\icons\satellite.png')
        self.AsteroidImg = pygame.image.load(r'.venv\icons\meteorite.png')

        self.far_stars = [[random.randint(0, 800), random.randint(0, 600), random.randint(150, 255)] for _ in range(50)]
        self.near_stars = [[random.randint(0, 800), random.randint(0, 600), random.randint(200, 255)] for _ in
                           range(30)]
        self.planets = [(100, 100, 0.5), (600, 200, 0.7)]
        self.shooting_stars = []

        self.score, self.hits, self.max_hits, self.shake_timer = 0, 0, 5, 0
        self.font = pygame.font.SysFont('Consolas', 20, bold=True)
        self.end_font = pygame.font.SysFont('Consolas', 40, bold=True)
        self.game_over = False

    def draw_gradient_background(self) -> None:
        for i in range(600):
            color = (0, 0, 30 + i // 10)
            pygame.draw.line(self.screen, color, (0, i), (800, i))

    def draw_parallax_stars(self) -> None:
        for star in self.far_stars:
            star[1] += 0.5
            star[2] += random.choice([-1, 1])
            star[2] = max(150, min(255, star[2]))
            pygame.draw.circle(self.screen, (star[2], star[2], 255), (star[0], int(star[1])), 1)
            if star[1] > 600:
                star[0] = random.randint(0, 800)
                star[1] = 0

        for star in self.near_stars:
            star[1] += 1.5
            star[2] += random.choice([-1, 1])
            star[2] = max(200, min(255, star[2]))
            pygame.draw.circle(self.screen, (star[2], star[2], star[2]), (star[0], int(star[1])), 2)
            if star[1] > 600:
                star[0] = random.randint(0, 800)
                star[1] = 0

    def draw_satellite(self) -> None:
        for x, y, scale in self.planets:
            img = pygame.transform.rotozoom(self.SatelliteImg, 0, scale)
            self.screen.blit(img, (x, y))

    def update_shooting_stars(self) -> None:
        if random.randint(0, 200) == 0:
            self.shooting_stars.append([random.randint(0, 800), 0])

        for star in self.shooting_stars[:]:
            star[0] += 3
            star[1] += 3
            pygame.draw.line(self.screen, (255, 255, 255), (star[0], star[1]), (star[0] - 10, star[1] - 10), 2)
            if star[1] > 600:
                self.shooting_stars.remove(star)

    def show_stats(self) -> None:
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        hits_text = self.font.render(f'Hits: {self.hits}/{self.max_hits}', True, (255, 100, 100))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(hits_text, (10, 40))

    def end_game(self) -> None:
        self.game_over = True
        end_text = self.end_font.render('Game Over', True, (255, 50, 50))
        score_text = self.font.render(f'Final Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(end_text, (300, 250))
        self.screen.blit(score_text, (330, 300))


class Asteroid:
    def __init__(self, game) -> None:
        self.game = game
        self.x = random.randint(0, 750)
        self.y = random.randint(-600, -50)
        self.speed = random.uniform(1, 3)
        self.width, self.height = 50, 50

    def move(self) -> None:
        self.y += self.speed
        if self.y > 600:
            self.y = random.randint(-600, -50)
            self.x = random.randint(0, 750)

    def draw(self) -> None:
        self.game.screen.blit(self.game.AsteroidImg, (self.x, self.y))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Debris:
    def __init__(self, game, x, y) -> None:
        self.game = game
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = (random.randint(180, 255), random.randint(100, 150), random.randint(100, 150))
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.lifetime = random.randint(20, 40)

    def update(self) -> None:
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        pygame.draw.circle(self.game.screen, self.color, (int(self.x), int(self.y)), self.size)


class Alien:
    def __init__(self, game):
        self.game = game
        self.num_aliens = 3
        self.aliens = [{'x': random.randint(0, 768), 'y': random.randint(50, 150)} for _ in range(self.num_aliens)]

    def update_alien(self, alien_dict, aliens_list, PlayerX, PlayerY, bullets):
        AlienX = alien_dict['x']
        AlienY = alien_dict['y']

        player_collision = (
                    AlienX < PlayerX + 64 and AlienX + 32 > PlayerX and AlienY < PlayerY + 64 and AlienY + 32 > PlayerY)
        bullet_hit = False

        for bullet_pos in bullets[:]:
            bullet_collision = (AlienX < bullet_pos[0] + 32 and AlienX + 32 > bullet_pos[0] and AlienY < bullet_pos[
                1] + 32 and AlienY + 32 > bullet_pos[1])
            if bullet_collision:
                bullets.remove(bullet_pos)
                bullet_hit = True
                self.game.score += 1
                break

        def respawn_alien():
            while True:
                new_x = random.randint(0, 768)
                new_y = random.randint(50, 150)
                too_close = False
                for other in aliens_list:
                    if other is alien_dict:
                        continue
                    if abs(new_x - other['x']) < 100 and abs(new_y - other['y']) < 60:
                        too_close = True
                        break
                if not too_close:
                    alien_dict['x'], alien_dict['y'] = new_x, new_y
                    break

        if AlienY >= 568 or player_collision:
            self.game.hits += 1
            self.game.shake_timer = 15
            respawn_alien()

        elif bullet_hit:
            respawn_alien()

        else:
            alien_dict['y'] += 1

        if self.game.shake_timer > 0:
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            self.game.shake_timer -= 1
            self.game.screen.blit(self.game.AlienImg, (alien_dict['x'] + offset_x, alien_dict['y'] + offset_y))
        else:
            self.game.screen.blit(self.game.AlienImg, (alien_dict['x'], alien_dict['y']))

        return self.game.score, self.game.hits


class Player:
    def __init__(self, game):
        self.game = game
        self.PlayerX = 370
        self.PlayerY = 480

    def play(self) -> None:
        self.game.screen.blit(self.game.PlayerImg, (self.PlayerX, self.PlayerY))


class RestartButton:
    def __init__(self, game) -> None:
        self.game = game
        self.font = pygame.font.SysFont(None, 40)
        self.rect = pygame.Rect(0, 0, 170, 60)
        self.rect.center = (400, 390)

    def draw(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = (0, 220, 0)
        else:
            color = (0, 200, 0)

        pygame.draw.rect(self.game.screen, (255, 255, 255), self.rect, border_radius=12)
        inner_rect = self.rect.inflate(-6, -6)
        pygame.draw.rect(self.game.screen, color, inner_rect, border_radius=10)
        text = self.font.render("RESTART", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        self.game.screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def main() -> None:
    Space_Invaders = Game()
    Spaceship = Player(Space_Invaders)
    Aliens = Alien(Space_Invaders)
    restart_button = RestartButton(Space_Invaders)

    bullets = []
    asteroid_list = [Asteroid(Space_Invaders) for _ in range(5)]
    debris_particles = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if Space_Invaders.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(pygame.mouse.get_pos()):
                    Space_Invaders = Game()
                    Spaceship = Player(Space_Invaders)
                    Aliens = Alien(Space_Invaders)
                    restart_button = RestartButton(Space_Invaders)
                    bullets = []
                    asteroid_list = [Asteroid(Space_Invaders) for _ in range(5)]
                    debris_particles = []

        if not Space_Invaders.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP] and Spaceship.PlayerY - 5 > 0:
                Spaceship.PlayerY -= 5
            if keys[pygame.K_s] or keys[pygame.K_DOWN] and Spaceship.PlayerY + 5 < 536:
                Spaceship.PlayerY += 5
            if keys[pygame.K_a] or keys[pygame.K_LEFT] and Spaceship.PlayerX - 5 > 0:
                Spaceship.PlayerX -= 5
            if keys[pygame.K_d] or keys[pygame.K_RIGHT] and Spaceship.PlayerX + 5 < 736:
                Spaceship.PlayerX += 5

            if keys[pygame.K_SPACE]:
                if len(bullets) == 0 or bullets[-1][1] < Spaceship.PlayerY - 100:
                    bullets.append([Spaceship.PlayerX + 16, Spaceship.PlayerY])

        Space_Invaders.draw_gradient_background()
        Space_Invaders.draw_parallax_stars()
        Space_Invaders.draw_satellite()
        Space_Invaders.update_shooting_stars()

        if Space_Invaders.shake_timer > 0:
            Space_Invaders.shake_timer -= 1

        if not Space_Invaders.game_over:
            for alien_obj in Aliens.aliens:
                Aliens.update_alien(alien_dict=alien_obj, aliens_list=Aliens.aliens, PlayerX=Spaceship.PlayerX,
                                    PlayerY=Spaceship.PlayerY, bullets=bullets)

            for bullet_pos in bullets[:]:
                bullet_pos[1] -= 7
                Space_Invaders.screen.blit(Space_Invaders.BulletImg, (bullet_pos[0], bullet_pos[1]))
                if bullet_pos[1] <= 0:
                    bullets.remove(bullet_pos)

            for asteroid in asteroid_list[:]:
                asteroid.move()
                asteroid.draw()

                for bullet_pos in bullets[:]:
                    bullet_rect = pygame.Rect(bullet_pos[0], bullet_pos[1], 16, 32)
                    if bullet_rect.colliderect(asteroid.rect()):
                        bullets.remove(bullet_pos)
                        asteroid_list.remove(asteroid)
                        asteroid_list.append(Asteroid(Space_Invaders))

                        for _ in range(15):
                            debris_particles.append(Debris(Space_Invaders, asteroid.x + asteroid.width // 2,
                                                           asteroid.y + asteroid.height // 2))
                        break

            for debris in debris_particles[:]:
                debris.update()
                if debris.lifetime <= 0:
                    debris_particles.remove(debris)

            Spaceship.play()
            Space_Invaders.show_stats()

            if Space_Invaders.hits >= Space_Invaders.max_hits:
                Space_Invaders.game_over = True

        if Space_Invaders.game_over:
            Space_Invaders.end_game()
            restart_button.draw()

        pygame.display.update()
        Space_Invaders.clock.tick(60)


if __name__ == '__main__':
    main()