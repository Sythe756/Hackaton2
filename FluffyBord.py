import pygame
from pygame.locals import *
import pygame.mixer
import random
import os 
from dbInfo import db_host, db_name, db_user, db_password
import psycopg2




pygame.init()
pygame.mixer.init()

db_conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)
cursor = db_conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS high_scores (
        username varchar(255) PRIMARY KEY,
        score integer
    )
    """
)
db_conn.commit()


cursor.execute("SELECT MAX(score) FROM high_scores")
row = cursor.fetchone()
if row:
    highscore = row[0]
else:
    highscore = 0

pygame.display.set_caption('Enter Your Username')
clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 845

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

textbox_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 20, 300, 40)
user_input = ""

#fonts
font = pygame.font.SysFont('Bauhaus 93',60)

#color
white = (255,255,255)
black = (0,0,0)
#variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
pause = False
music_paused = False
music_muted = False
input_active = False


#high scores



#game music
game_music = pygame.mixer.music.load('assets/bg_music.mp3')


#load images
bg = pygame.image.load('assets/bg.png')
ground_img = pygame.image.load('assets/ground.png')


#functions

def draw_text(text,font,text_col,x,y):
	img = font.render(text,True,text_col)
	screen.blit(img,(x,y))

def game_over_screen():
    screen.fill(black)  # Fill the screen with black background
    draw_text("Game Over", font, white, int(screen_width -  675), int(screen_height / 4))
    draw_text("Score: " + str(score), font, white, int(screen_width -  675), int(screen_height / 2))
    draw_text("Highscore: " + str(highscore), font, white, int(screen_width -  675), int(screen_height / 2.5))
    draw_text("Press R to Restart", font, white, int(screen_width -  675), int(screen_height * 3 / 4))
    draw_text("Press Q to Quit", font, white, int(screen_width - 675), int(screen_height * 3 / 4) + 60)
    pygame.display.update()

def Paused():
    screen.fill(black)
    draw_text("Highscore: " + str(highscore), font, white, int(screen_width -  675), int(screen_height / 4))
    draw_text("Pause", font, white, int(screen_width -  675), int(screen_height / 2))
    draw_text("Score: " + str(score), font, white,int(screen_width -  675), int(screen_height * 3 / 4))
    draw_text("Press 'P' to Resume", font, white, int(screen_width - 675), int(screen_height * 3 / 4) + 60)

#Classes
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'assets/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
            # gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            # jump
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.clicked:
                self.clicked = True
                self.vel = -10
            if not keys[pygame.K_SPACE]:
                self.clicked = False

            # animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

def update_high_score(username, score):
    cursor.execute("SELECT score FROM high_scores WHERE username = %s", (username,))
    existing_score = cursor.fetchone()

    if existing_score is None or score > existing_score[0]:
        cursor.execute("INSERT INTO high_scores (username, score) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET score = EXCLUDED.score", (username, score))
        db_conn.commit()

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/pipe.png')
        self.rect = self.image.get_rect()
        # pos1 is top, -1 is the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
        pipe_group.add(self)
        
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

# Start playing the background music
pygame.mixer.music.play(-1)

run = True










while run:
    clock.tick(fps)

    if pause == False:  # Check if the game is not paused
        # draw background
        screen.blit(bg, (0, 0))

        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)

        # draw the ground
        screen.blit(ground_img, (ground_scroll, 768))
        
        # Resume music if it was paused
        if music_paused:
            pygame.mixer.music.unpause()
            music_paused = False

        # score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and pass_pipe == False:
                pass_pipe = True
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False

        draw_text(str(score), font, white, int(screen_width / 2), 20)

        # look for collision
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True

        # check if bird has hit the ground
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

        if game_over:
            game_over_screen()
            pygame.display.update()

            # Check for user input to restart or quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart the game
                        game_over = False
                        bird_group.empty()
                        pipe_group.empty()
                        flappy = Bird(100, int(screen_height / 2))
                        bird_group.add(flappy)
                        score = 0
                        pass_pipe = False
                        last_pipe = pygame.time.get_ticks()
                        ground_scroll = 0
                    elif event.key == pygame.K_q:  # Quit the game
                        run = False

    if game_over == False and flying == True:
        if score > highscore:
            highscore = score
            # Update the high score in the database
            update_high_score("player", score)  # Use the username of the player here

        # generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()
    else:
        if score > highscore:
            highscore = score
            with open('assets/score.txt', 'w') as file:
                file.write(str(highscore))

    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and flying == False and game_over == False:
            flying = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if pause:
                    pause = False
                else:
                    pause = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if music_muted:
                    pygame.mixer.music.set_volume(0.5)
                    music_muted = False
                else:
                    pygame.mixer.music.set_volume(0)
                    music_muted = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                run = False
    if pause:
        Paused()
        if not music_paused:
            pygame.mixer.music.pause()
            music_paused = True

    pygame.display.update()

pygame.quit()
cursor.close()
db_conn.close()