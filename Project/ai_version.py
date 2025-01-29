import pygame
import neat
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

def object_mover(win, birds, pipes, base, gen, nets):
    trash = []
    global score
    global FPS
    
    pipe_ind = 0
    if len(birds) > 0:
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1
    else:
        return False

    for count, bird in enumerate(birds):
        bird.move()
        gen[count].fitness += 0.1
        
        data_to_evaluate = ( bird.y,
                            abs(bird.y - pipes[pipe_ind].height),
                            abs(bird.y - pipes[pipe_ind].bottom) )

        result = nets[count].activate( data_to_evaluate )
        
        if result[0] > 0.5:
            bird.jump()

    for pipe in pipes:

        pipe.move() 
        
        for count,bird in enumerate(birds):
            if pipe.collide(bird):
                gen[count].fitness -= 1
                birds.remove( bird )
                nets.pop( count )
                gen.pop( count )
                
            if pipe.passed == False and pipe.x < bird.x:
                pipe.passed = True
                score += 1
                
                for g in gen:
                    g.fitness += 5
                pipes.append(Pipe(WIN_WIDTH+100))

        if pipe.x + pipe.PIPE_TOP.get_width() < 0:
            trash.append(pipe)

    for r in trash:
        pipes.remove(r)

    for count, bird in enumerate(birds):        
        if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
            gen[count].fitness -= 1
            birds.remove( bird )
            nets.pop( count )
            gen.pop( count )
            
    base.move()
    
    if score > 10 and FPS< 1000:
        FPS += 1

def draw_window(win, birds, pipes, base):
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)
        
    pipe_passed = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(pipe_passed,(5,1) )

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

def run_game( genomes, config ):
    
    gen = []
    nets = []
    birds = []
    global generation
    global population
    
    generation += 1
    population = len(genomes)
    
    for ID, g in genomes:
        net = neat.nn.FeedForwardNetwork.create( g, config )
        nets.append( net )
        birds.append( Bird(random.randrange(100,230),350) )
        g.fitness = 0
        gen.append( g )    
    
    pygame.init()
    pygame.display.set_caption("Ai FLappy Bird - 2025")
    
    base = Base(730)
    pipes = [Pipe(700)]

    win = pygame.display.set_mode( screen_size )
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break                

        if object_mover( win, birds, pipes, base, gen, nets ) == False:
            run = False
            break
               
        draw_window( win, birds, pipes, base )

def run( config_path ):
    
    try:
        config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, 
                                    neat.DefaultStagnation,
                                    config_path)   
    except:
        print("oops, file error, check the file again...")
        return
    
    population = neat.Population( config )

    population.run( run_game,50 )

    pygame.quit()
    quit()
   
if __name__ == "__main__":
    local_dir = os.path.dirname((__file__))
    config_path = os.path.join(local_dir, "ai-config.txt")

    run( config_path )
