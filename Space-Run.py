import pygame
import random
import tkinter as tk
from tkinter import simpledialog
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["space_run"]
players_collection = db["players"]


pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Run Game 2.0")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


background_img = pygame.image.load(r'C:\Users\kamle\.vscode\Space Run 2.0\background.png')
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))  


font = pygame.font.SysFont('pixel', 30)  


player_img = pygame.image.load(r'C:\Users\kamle\.vscode\Space Run 2.0\player.png')  
player_img = pygame.transform.scale(player_img, (50, 50))  

asteroid_img = pygame.image.load(r'C:\Users\kamle\.vscode\Space Run 2.0\obstacle.png')  
asteroid_img = pygame.transform.scale(asteroid_img, (50, 50))  


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = asteroid_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 50)
        self.rect.y = -50
        self.speed = random.randint(3, 6)  

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = -50
            self.rect.x = random.randint(0, WIDTH - 50)
            self.speed = random.randint(3, 6)  


def save_player_score(name, score):
    player = {"name": name, "score": score}
    players_collection.insert_one(player)


def start_timer():
    countdown_font = pygame.font.SysFont('pixel', 50)  
    countdown_time = 3  
    running = True
    while running:
        screen.fill(WHITE)
        countdown_text = countdown_font.render(f"Starting in {countdown_time}", True, BLACK)
        screen.blit(countdown_text, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(1000)  
        countdown_time -= 1
        if countdown_time < 0:
            running = False


def display_scoreboard():
    screen.fill(WHITE)
    scoreboard_font = pygame.font.SysFont('pixel', 30)
    title_text = scoreboard_font.render("Scoreboard", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - 80, 50))

    
    players = players_collection.find().sort("score", -1).limit(10)  

    y_offset = 100
    for player in players:
        score_text = scoreboard_font.render(f"{player['name']} - {player['score']}", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - 100, y_offset))
        y_offset += 40

    
    back_text = scoreboard_font.render("Press ESC to go back", True, BLACK)
    screen.blit(back_text, (WIDTH // 2 - 100, y_offset + 50))

    pygame.display.flip()

    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False


def login():
    root = tk.Tk()
    root.withdraw()  
    player_name = simpledialog.askstring("Player Name", "Enter your name:", parent=root)
    if player_name:
        show_menu(player_name)
    else:
        print("Player name is required")


def show_menu(player_name):
    menu_font = pygame.font.SysFont('pixel', 50)
    running = True
    while running:
        screen.fill(WHITE)
        title_text = menu_font.render("Space Run 2.0", True, BLACK)
        start_text = menu_font.render("Press ENTER to Start", True, BLACK)
        scoreboard_text = menu_font.render("Press S to View Scoreboard", True, BLACK)

        screen.blit(title_text, (WIDTH // 2 - 150, HEIGHT // 4))
        screen.blit(start_text, (WIDTH // 2 - 150, HEIGHT // 2))
        screen.blit(scoreboard_text, (WIDTH // 2 - 180, HEIGHT // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  
                    run_game(player_name)
                    running = False
                if event.key == pygame.K_s:  
                    display_scoreboard()


def run_game(player_name):
    clock = pygame.time.Clock()
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    asteroids = pygame.sprite.Group()
    score = 0

    
    for _ in range(5):
        asteroid = Asteroid()
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

    
    start_timer()

    running = True
    paused = False  
    while running:
        screen.blit(background_img, (0, 0))  

        keys = pygame.key.get_pressed()  

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  
                    paused = not paused  
                if event.key == pygame.K_ESCAPE:  
                    running = False  

        if paused:
            
            paused_text = font.render("PAUSED", True, BLACK)
            screen.blit(paused_text, (WIDTH // 2 - 60, HEIGHT // 2))
        else:
            
            player.update(keys)
            for asteroid in asteroids:
                asteroid.update()

            
            if pygame.sprite.spritecollide(player, asteroids, False):
                running = False
                save_player_score(player_name, score)  

            all_sprites.draw(screen)

            
            score += 1
            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    login()
