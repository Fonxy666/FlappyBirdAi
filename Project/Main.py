import pygame
import neat
import time
import os
import random

WIN_WIDTH = 550
WIN_HEIGHT = 800
FPS = 30

score = 0
generation = 0
population = 0
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans",40)

sBirdPath1 = os.path.join("img","bird1.png")
sBirdPath2 = os.path.join("img","bird2.png")
sBirdPath3 = os.path.join("img","bird3.png")
sBasePath = os.path.join("img","base.png")
sBgPath = os.path.join("img","bg.png")
sPipePath = os.path.join("img","pipe.png")

screen_size = (WIN_WIDTH,WIN_HEIGHT) 

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(sBirdPath1)),
             pygame.transform.scale2x(pygame.image.load(sBirdPath2)),
             pygame.transform.scale2x(pygame.image.load(sBirdPath3))]

BASE_IMG = pygame.transform.scale2x(pygame.image.load(sBasePath))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(sPipePath))
BG_IMG = pygame.transform.scale2x(pygame.image.load(sBgPath))

class Bird:
    IMGS = BIRD_IMGS
    ANIMATION_TIME = 3

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        
    def jump(self):
        self.vel = -9
        self.tick_count = 0
        self.height = self.y
        
    def move(self):
        self.tick_count += 1
        
        delta = self.vel * self.tick_count + 1.5 * self.tick_count**2
        
        if delta >= 16:
            delta = 16
        if delta < 0:
            delta -= 2
            
        self.y = self.y + delta

    def draw(self, win):
        self.img_count += 1
        
        if self.img_count == self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        if self.img_count == (self.ANIMATION_TIME * 2):
            self.img = self.IMGS[1]
        if self.img_count == (self.ANIMATION_TIME * 3):
            self.img = self.IMGS[2]
            self.img_count = 0

        win.blit(self.img,(self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 7
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False
        self.set_height()
        
    def set_height(self):
        self.height = random.randrange(30, 550)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
        
    def move(self):
        self.x -= self.VEL
        
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - bird.y)
        bottom_offset = (self.x - bird.x, self.bottom - bird.y)
       
        t_point = bird_mask.overlap( top_mask, top_offset )
        b_point = bird_mask.overlap( bottom_mask, bottom_offset )
        
        if t_point or b_point:
            return True
        
        return False
    
class Base:
    VEL = 7
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
   
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))

def draw_window(win, birds, pipes, base):
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)

    pipe_passed = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(pipe_passed,(5,5) )
   
    generation_counter = STAT_FONT.render("Generation: " + str(generation),1,(255,255,255))
    win.blit(generation_counter,(5,45) )

    genom_counter = STAT_FONT.render("Population: " 
                                     + str(population) + "/" 
                                     + str(len(birds)),1,(255,255,255))
    win.blit(genom_counter,(5,90) )

    
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()
    
def object_mover(win, bird, pipes, base):
    trash = []
    global score
            
    bird.move()
    
    for pipe in pipes:
        if pipe.collide(bird):
            score -= 1
            pass
            
        if pipe.x + pipe.PIPE_TOP.get_width() < 0:
            trash.append(pipe)
            
        if pipe.passed == False and pipe.x < bird.x:
            pipe.passed = True
            score += 1
            pipes.append(Pipe(WIN_WIDTH+100))
                
        pipe.move()
                
        for r in trash:
            trash.remove(r)
        
    if bird.y + bird.img.get_height() >= 730:
        score -= 1
        pass
        
    base.move()

def draw_window(win, bird, pipes, base):
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)

    pipe_passed = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(pipe_passed,(5,5) )
    
    base.draw(win)
    bird.draw(win)
    pygame.display.update()
   
def run_game():
    pygame.init()
    pygame.display.set_caption("Manual Flappy Bird - 2025")
    
    base = Base(730)
    bird = Bird(230,350)
    pipes = [Pipe(700)]

    win = pygame.display.set_mode( screen_size )
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        object_mover( win, bird, pipes, base )

        draw_window( win, bird, pipes, base )

    pygame.quit()

if __name__ == "__main__":
    run_game()