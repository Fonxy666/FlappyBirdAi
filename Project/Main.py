"""
Flappy bird game with AI support
"""

#import some pre-written libraries
import pygame #for game development
import neat # for AI support
import time #time and date management
import os # for file handling and other OS relaTED TASK
import random # pseudo random number handling



#set default size for the game window
WIN_WIDTH = 550
WIN_HEIGHT = 800
FPS = 30

#score, generation, population counter and set font
score = 0
generation = 0
population = 0
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans",40)


#set all path for images
sBirdPath1 = os.path.join("img","bird1.png")
sBirdPath2 = os.path.join("img","bird2.png")
sBirdPath3 = os.path.join("img","bird3.png")
sBasePath = os.path.join("img","base.png")
sBgPath = os.path.join("img","bg.png")
sPipePath = os.path.join("img","pipe.png")


#set the desired screen size
#this is a tuple type collection
screen_size = (WIN_WIDTH,WIN_HEIGHT) 


#load necessary images for later usage into this array
#also, enlarge the images (scale2x)
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(sBirdPath1)),
             pygame.transform.scale2x(pygame.image.load(sBirdPath2)),
             pygame.transform.scale2x(pygame.image.load(sBirdPath3))]

BASE_IMG = pygame.transform.scale2x(pygame.image.load(sBasePath))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(sPipePath))
BG_IMG = pygame.transform.scale2x(pygame.image.load(sBgPath))


#lets create a class for the bird
class Bird:
    #setup basic parameters
    IMGS = BIRD_IMGS
    ANIMATION_TIME = 3 #wait time between bird animation

    
    #every class must have a constructor
    def __init__(self, x, y):
        self.x = x #x coord of the bird
        self.y = y #y coord of the bird
        #self.tilt = 0 #rotation of the bird
        self.tick_count = 0 #movement counter
        self.vel = 0 #speed (velocity)
        self.height = self.y
        self.img_count = 0 #image counter for wing animation
        self.img = self.IMGS[0] #start with the first bird image
    #end of function __init__
    
        
    #this does the jumping of the bird
    #it means the AI make decision, if jump is necessary
    def jump(self):
        self.vel = -9
        self.tick_count = 0
        self.height = self.y
    #end of function jump
    
        
    #lets move the bird
    #it means the birdy keeps falling
    def move(self):
        self.tick_count += 1
        
        #delta stands for Displacement
        delta = self.vel * self.tick_count + 1.5 * self.tick_count**2
        
        #don't move too much
        if delta >= 16:
            delta = 16
        if delta < 0:
            delta -= 2
            
        #let's change the y position of the bird
        self.y = self.y + delta
    #end of function move
    

    #draw the bird on the screen
    def draw(self, win):
        self.img_count += 1 #which image to show
        
        #slow down the flapping of the wings
        if self.img_count == self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        if self.img_count == (self.ANIMATION_TIME * 2):
            self.img = self.IMGS[1]
        if self.img_count == (self.ANIMATION_TIME * 3):
            self.img = self.IMGS[2]
            self.img_count = 0

        #copy the image to the window screen
        win.blit(self.img,(self.x, self.y))
    #end of function draw
     
        
    #get a mask for collision detection
    #mask is the 1bit version of the image
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    #end of function get_mask
    
#end of class Bird


#let's create a class for the pipe
class Pipe:
    GAP = 200 #space between the pipes
    VEL = 7 #speed of pipes
    
    #setup parameters
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0

        #a pipe object contains 2 pipes actually
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False #bird passed the pipe?
        self.set_height()
    #end of function __init__
    

    #set random pipe heights
    def set_height(self):
        self.height = random.randrange(30, 550)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    #end of function set_height
        
        
    #now move the pipes along x axis
    def move(self):
        self.x -= self.VEL
    #end of function move


    #let's draw the 2 pipes
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    #end of function draw
    
    
    #collision checking
    def collide(self, bird):
        #get the masks of the objects to check
        #a mask is a 1bit version of the given object
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        #check the distance between  objects       
        top_offset = (self.x - bird.x, self.top - bird.y)
        bottom_offset = (self.x - bird.x, self.bottom - bird.y)
       
        #is there any overlaping between masks?
        t_point = bird_mask.overlap( top_mask, top_offset )
        b_point = bird_mask.overlap( bottom_mask, bottom_offset )
        
        #if so, then birdy hits 1 of the pipes
        if t_point or b_point:
            return True

        #otherwise no collision detected
        return False
    #end of function collide
        
#end of class Pipe


#this is the Base class
class Base:
    VEL = 7
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    #setup the parameters
    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    #end of function init
        
    #move 2 ground image together    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        #off the screen? Shows up on the right
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        #off the screen? Shows up on the right
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    #end of function move
            
    #draw the calcualted images        
    def draw(self, win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))
    
#end of class Base  


#object mover function
def object_mover(win, birds, pipes, base, gen, nets):
    trash = [] #this is the pipe trash
    global score
    global FPS
    
    #we have to know wich pipe is in front of us
    #so we can make decision to jump, or not
    pipe_ind = 0
    if len(birds) > 0:
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1
    else:
        return False

    #check the birds
    for count, bird in enumerate(birds):
        bird.move() #change pos of a bird (down)
        gen[count].fitness += 0.1 #increase a little bit the fitness
    
        #AI will make decision knowing these data    
        data_to_evaluate = ( bird.y,
                            abs(bird.y - pipes[pipe_ind].height),
                            abs(bird.y - pipes[pipe_ind].bottom) )
        #let's make a decision without human intervention
        result = nets[count].activate( data_to_evaluate )
        
        #result is between 0 and 1 (sigmoid activation function)
        if result[0] > 0.5: #if pretty sure...
            bird.jump()
    #bird checker loop is over


    #manage the pipes
    for pipe in pipes:

        pipe.move() #change pos of the pipes
        
        #check pipe - bird collision
        for count,bird in enumerate(birds):
            if pipe.collide(bird):
                gen[count].fitness -= 1 #decrease fitness
                birds.remove( bird ) #delete
                nets.pop( count ) #delete
                gen.pop( count ) #delete

            #birdy left the pipe successfully, so...
            if pipe.passed == False and pipe.x < bird.x:
                pipe.passed = True
                score += 1 #increase score
                
                for g in gen:
                    g.fitness += 5 #increase fitness
                pipes.append(Pipe(WIN_WIDTH+100)) #add another pipe
        #end of birdy loop    
        
        #check if pipe left the window
        if pipe.x + pipe.PIPE_TOP.get_width() < 0:
            trash.append(pipe)
    #pipe management loop is over
                
    #delete the unseen pipes
    for r in trash:
        pipes.remove(r)

    #check if any of the birds hit the ground, or fly away
    for count, bird in enumerate(birds):        
        if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
            gen[count].fitness -= 1 #decrease fitness
            birds.remove( bird ) #delete bird
            nets.pop( count ) #delete "brain" (NN)
            gen.pop( count ) #delete from generation
    #for loop is over    
        
    base.move() #change pos of the ground
    
    #just for fun: above 10 pipes, let's make it faster
    if score > 10 and FPS< 1000:
        FPS += 1
#end of function object mover


#draw the everything on the window screen
def draw_window(win, birds, pipes, base):
    win.blit(BG_IMG, (0,0)) #background drawing
    
    #draw all of the pipes
    for pipe in pipes:
        pipe.draw(win)

    #show score 
    pipe_passed = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(pipe_passed,(5,1) )

    #show generation
    generation_counter = STAT_FONT.render("Generation: " + str(generation),1,(255,255,255))
    win.blit(generation_counter,(5,45) )

    #show population
    genom_counter = STAT_FONT.render("Population: " 
                                     + str(population) + "/" 
                                     + str(len(birds)),1,(255,255,255))
    win.blit(genom_counter,(5,90) )

    
    base.draw(win) #ground drawing
    for bird in birds:
        bird.draw(win) #bird drawing
        
    pygame.display.update() #update the screen
#end of function draw_window
    

#this is the main loop, game starts here (fitness function)    
def run_game( genomes, config ):
    #this runs for every new generation
    gen = []
    nets = []
    birds = []
    global generation
    global population
    
    generation += 1
    population = len(genomes)
    
    #setup every genomes (g) here
    #genome is a bird in the population
    for ID, g in genomes:
        #we create a brain, a neural network (NN)
        net = neat.nn.FeedForwardNetwork.create( g, config )
        nets.append( net ) #we collect all the NN herein the list
        birds.append( Bird(random.randrange(100,230),350) ) #we collect birds in the list
        g.fitness = 0 #zero experience
        gen.append( g ) #we collect genomes in the list
    #genome setup is complete    
        
    
    pygame.init() #setup the game engine
    pygame.display.set_caption("Programozz Pedróval - 2025")
    
    base = Base(730) #create the ground object
    pipes = [Pipe(700)] #create an array for the pipes

    win = pygame.display.set_mode( screen_size ) #create a window to draw onto
    clock = pygame.time.Clock() #clock handles frame rate

    run = True #game runs until it's true
    while run:
        clock.tick(FPS) #FPS is 30
        
        #check the events, like clickx
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #exit click?
                run = False #stop running
                pygame.quit() #close game engine
                quit() #quit program
                break                

        #let's move all of the objects
        if object_mover( win, birds, pipes, base, gen, nets ) == False:
            run = False
            break
               
        #now draw everything on the screen
        draw_window( win, birds, pipes, base )
    #end of while loop
    
#end of function run_game


#this is the function run
def run( config_path ):
    
    try:
        #load the default parameters for neural networks
        config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, 
                                    neat.DefaultStagnation,
                                    config_path)   
    except:
        print("oops, file error, check the file again...")
        return
    
    #create a noob population at the beginning
    #the population consists of x genomes (birdies)
    population = neat.Population( config )
    
    #it excutes the main function for 50 times
    #in other words it's 50 generations
    population.run( run_game,50 )
    
    #okay, that's all folks
    pygame.quit() #exit the game engine
    quit() #exit the whole program
#end of function run
    
 
#the big boom    
if __name__ == "__main__":
    #we need an AI config file
    local_dir = os.path.dirname((__file__))
    config_path = os.path.join(local_dir, "config-feedforward.txt")

    #run the program here
    run( config_path )
#end of entry point









