import pygame 
import neat
import time
import os
import random
pygame.font.init()
GEN = 0

def blitRotateCenter(surf, image, topleft, angle):
    #to rotate a image with respect to center and blit(show in window)  
    #Input: window in surf, (x,y) position of center in topleft
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

WIN_WIDTH = 600
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):        
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt initially
        self.tick_count = 0
        self.vel = 0 
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0] #keep changing to show it flapping
    def jump(self):       
        self.vel = -10.5   #cuz orgin is in  the top left corner and down is posi y dir
        self.tick_count = 0    #when we last jumped
        self.height = self.y
    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2 #change in position from the moment we jump(think of disp vector pointing down if posi, up if neg), disp = ut + 0.5*gt**2 
        if d >=16:
            d=16  #dont let it go too down
        if d<0:
            d-=2 #make it uniformly go up
        self.y = self.y + d
        if d<0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION   #if going up or above a certain height from start, then tilt bird up
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    def draw(self, win):       
        self.img_count += 1             
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:    #when bird is nose diving it isn't flapping
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2 #to continue from one
        
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt) # tilt the bird

    def get_mask(self):    #if collision
        return pygame.mask.from_surface(self.img)
    
class Pipe:    
    GAP = 200   #gap betw pipes
    VEL = 5   #how fast the background moves
    def __init__(self, x):
        self.x = x   #x position of pipe(x of topleft coord of pipe)
        self.height = 0  #y of bottomline of top_pipe

        # y of topleft of top and bottom pipe
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) 
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False    #to see if bird has passed by this pipe
        self.set_height()

    def set_height(self):        
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()  #is above the screen (neg)
        self.bottom = self.height + self.GAP
    def move(self):        
        self.x -= self.VEL
    def draw(self, win):         
        win.blit(self.PIPE_TOP, (self.x, self.top))        
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    def collide(self, bird, win):        
        bird_mask = bird.get_mask()    #array of pixel where bird(not including transparant part of image) is present
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))  #round cuz dont want float
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)  #value is None if not intersect
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True
        return False
class Base:
    VEL =5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):        
        self.y = y

        #x of topleft of two same images, have them come one after another and cycle, to make it look infinite
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
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))




    
def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0,0))
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: "+str(score), 1,(255, 255, 255))
    win.blit(text, (WIN_WIDTH - text.get_width() - 10, 10))

    text = STAT_FONT.render("Gen: "+str(gen), 1,(255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1
    #the corresponding values in same address refer to same bird
    nets = []  
    ge = []
    birds = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0        #initial fitness to 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock() 
    score = 0  
    run = True
    while run:
        clock.tick(30)    #so the while loop dosent run more than 30 times per sec(this line dosent run consecutivly before its 1/30 sec), we can remove this if we just want to train cuz there is no reason to see the game happen
        for event in pygame.event.get():     #if click anywhere, if just want to play game execute bird.jump() for keyup and jump the first time too after the line run = true so that keyup actually affects in the game
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        #to know according to which pipe we create input(cuz two pipes at the same time)
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
                pipe_ind = 1  
        else:
            run = False
            break
        for x, bird in enumerate(birds): 
            ge[x].fitness += 0.1
            bird.move()            
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))  #inputs is according to distance between bird and top pipe and bottom pipe
            if output[0] > 0.5:  
                bird.jump()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):      #to get the position of where the bird is in the list too
                if pipe.collide(bird, win):
                    ge[x].fitness -= 1
                    birds.pop(x)   
                    nets.pop(x) 
                    ge.pop(x)        
                if not pipe.passed and pipe.x <bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width()<0:  #if pipeoff screen
                rem.append(pipe)

            pipe.move()
        if add_pipe:
            score +=1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y<0:
                birds.pop(x)   
                nets.pop(x) 
                ge.pop(x)
        if score > 50:  #this is cuz by score 50 it would have already broken the fitness thresshold and it might never die so we kill it, and 'winner' variable will have the model that stores the fittest bird and we can use pickle to save the fittest bird and change the main() so that it only works for 1 bird and run
            break 
        base.move()
        draw_window(win, birds, pipes, base, score, GEN)
    


def run(config_file):    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)    
    p = neat.Population(config)

    # to show progress and graphs
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)     #call main func 50 times and pass it all birds

if __name__ == '__main__':
    # Determine path to configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

# [NEAT]
# fitness_criterion     = max       want bird with max fitness
# fitness_threshold     = 100       after 100 fitness we believe bird good, no need more gen
# pop_size              = 50                 
# reset_on_extinction   = False

# [DefaultGenome]
# # node activation options
# activation_default      = tanh
# activation_mutate_rate  = 0.0     0 means it wont randomly change activation function(always tanh)
# activation_options      = tanh

# # node aggregation options
# aggregation_default     = sum
# aggregation_mutate_rate = 0.0
# aggregation_options     = sum

# # node bias options                  bias means b in equeation ( out = w*in +b ) the values below are for initial random values of bias
# bias_init_mean          = 0.0
# bias_init_stdev         = 1.0
# bias_max_value          = 30.0
# bias_min_value          = -30.0
# bias_mutate_power       = 0.5         Standard deviation from which mutation bias is drawn (centered at 0)
# bias_mutate_rate        = 0.7
# bias_replace_rate       = 0.1

# # genome compatibility options
# compatibility_disjoint_coefficient = 1.0
# compatibility_weight_coefficient   = 0.5

# # connection add/remove rates
# conn_add_prob           = 0.5       prob of adding and removing connection
# conn_delete_prob        = 0.5

# # connection enable options
# enabled_default         = True     all connection will be active initially   
# enabled_mutate_rate     = 0.01     1% chance of a connection deactivating

# feed_forward            = True
# initial_connection      = full

# # node add/remove rates
# node_add_prob           = 0.2     prob of adding removing node
# node_delete_prob        = 0.2

# # network parameters                   at the start what kind of network do we want 
# num_hidden              = 0
# num_inputs              = 3
# num_outputs             = 1

# # node response options
# response_init_mean      = 1.0
# response_init_stdev     = 0.0
# response_max_value      = 30.0
# response_min_value      = -30.0
# response_mutate_power   = 0.0             Standard deviation from which mutation for response multiplier is drawn (centered at 0)
# response_mutate_rate    = 0.0
# response_replace_rate   = 0.0

# # connection weight options              simmilar to bias
# weight_init_mean        = 0.0
# weight_init_stdev       = 1.0
# weight_max_value        = 30
# weight_min_value        = -30
# weight_mutate_power     = 0.5               Standard deviation from which weight mutation is drawn (centered at 0)
# weight_mutate_rate      = 0.8
# weight_replace_rate     = 0.1

# [DefaultSpeciesSet]
# compatibility_threshold = 3.0

# [DefaultStagnation]
# species_fitness_func = max
# max_stagnation       = 20      if 20 generation go by with no increase in fitness of a specie(bird having simmilar neural net), then eliminate the spicie 
# species_elitism      = 2

# [DefaultReproduction]
# elitism            = 2
# survival_threshold = 0.2