import math
import os
import sys
import pygame
import neat
import random
import pickle
import re
import concurrent.futures

WIDTH = 500
HEIGHT = 500
ROWS = 20
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 1000
gen = 0


class Cube():
    rows = ROWS
    width = WIDTH
    color = (255, 255, 255)

    def __init__(self, start, dirnx=1, dirny=0):
        self.pos = start
        self.dirnx = 1
        self.dirny = 0

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)  # change position

    def draw(self, surface, eyes=False):
        dis = self.width // self.rows  # Width/Height of each cube
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        # By multiplying the row and column value of our cube by the width and height of each cube we can determine where to draw it

        if eyes:
            center = dis // 2
            radius = 3
            circleMiddle = (i * dis + center - radius, j * dis + 8)
            circleMiddle2 = (i * dis + dis - radius * 2, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)


class Snake():
    rows = ROWS
    # body = []

    def __init__(self, color, pos):
        self.color = color
        self.body = []
        self.head = Body(pos)  # set head to front
        self.body.append(self.head)  # add cube to body

        self.is_dying = False
        self.turns = {}

        self.dirnx = 0  # Direction x
        self.dirny = 1  # Direction y


        self.apple = Apple(randomSnack(ROWS, self))
        self.dist_food = 0
        self.old_dist_food = math.sqrt((self.apple.pos[1] - self.head.pos[1])**2 + (self.apple.pos[1] - self.head.pos[1])**2)



    def move(self):


        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]


        for i, b in enumerate(self.body):  # loop through all cubes in body
            p = b.pos[:]  # stores position of cubes on grid

            if p in self.turns:  # if cubes current position is one where we turned
                turn = self.turns[p]  # get desired direction
                b.move(turn[0], turn[1])  # move cube in the direction

                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:  # if not turning
                # check if reached the edge
                if b.dirnx == -1 and b.pos[0] <= 0 or b.dirnx == 1 and b.pos[0] >= b.rows - 1 or b.dirny == 1 and b.pos[
                    1] >= b.rows - 1 or b.dirny == -1 and b.pos[1] <= 0:
                    pass
                else:
                    b.move(b.dirnx, b.dirny)

    def reset(self, pos):
        self.head = Body(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        # We need to know which side of the snake to add the cube to.
        # So we check what direction we are currently moving in to determine if we
        # need to add the cube to the left, right, above or below.
        if dx == 1 and dy == 0:
            self.body.append(Body((tail.pos[0] - 1, tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(Body((tail.pos[0] + 1, tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(Body((tail.pos[0], tail.pos[1] - 1)))
        elif dx == 0 and dy == -1:
            self.body.append(Body((tail.pos[0], tail.pos[1] + 1)))

        # We then set the cubes direction to the direction of the snake.
        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def spawn_apple(self):  # as class-instance function to create apples for every snake
        if self.body[0].pos == self.apple.pos:  # when apple is eaten
            self.addCube()
            self.apple = Apple(randomSnack(ROWS, self))
            return True

    def draw(self, surface, eyes=False):
        for i, c in enumerate(self.body):
            if i == 0:  # for the first cube in the list we want to draw eyes
                c.draw(surface, True)  # adding the true as an argument will tell us to draw eyes
            else:
                c.draw(surface)  # otherwise we will just draw a cube

    def die(self):
        # print('Score: ', len(self.body))
        # self.reset((10, 10))
        self.is_dying = True

    def get_data(self):
        # distance to edges
        # dist_edge_right = self.rows - self.head.pos[0]
        # dist_edge_bottom = self.rows - self.head.pos[1]
        # dist_edge_left = self.head.pos[0]
        # dist_edge_top = self.head.pos[1]

        # distance to tail
        # x_dist_tail = self.body[-1].pos[0] - self.head.pos[0]
        # y_dist_tail = self.body[-1].pos[1] - self.head.pos[1]

        # distance to food
        # x_dist_food = self.apple.pos[0] - self.head.pos[0]
        # y_dist_food = self.apple.pos[1] - self.head.pos[1]

        # direction to food
        food_direction = [0, 0, 0, 0]  # straight, back, left, right
        if self.head.pos[1] > self.apple.pos[1]:  # straight
            food_direction[0] = 1
        if self.head.pos[1] < self.apple.pos[1]:  # back
            food_direction[1] = 1
        if self.head.pos[0] > self.apple.pos[0]:  # left
            food_direction[2] = 1
        if self.head.pos[0] < self.apple.pos[0]:  # right
            food_direction[3] = 1

        # check if is obstacle at given position
        is_obstacle = [0,0,0,0]  # 0 = no obstacle, 1 = obstacle
        for i, pos_val in enumerate([(0, 1), (0, -1), (1, 0), (-1, 0)]):  # down, up, right, left 
            pos = (self.head.pos[0] + pos_val[0], self.head.pos[1] + pos_val[1])
            if pos in list(map(lambda z: z.pos, self.body[1:])) or (pos[0] < 0 or pos[0] >= ROWS or pos[1] >= ROWS or pos[1] < 0):
                is_obstacle[i] = 1

        # return (x_dist_food, y_dist_food, *is_obstacle)
        return (*food_direction, *is_obstacle)


class Body(Cube):
    color = (0, 255, 0)

    def __init__(self, start):
        super().__init__(start)


class Apple(Cube):
    color = (255, 0, 0)

    def __init__(self, start):
        super().__init__(start, 1, 0)


def drawGrid(w, rows, win):
    sizeBtwn = w // rows

    x = 0
    y = 0

    for i in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

        pygame.draw.line(win, (255, 255, 255), (x, 0), (x, w))
        pygame.draw.line(win, (255, 255, 255), (0, y), (w, y))


def redrawWindow(win, snakes):
    win.fill((0, 0, 0))
    
    for snake in snakes:
        snake.draw(win)
        snake.apple.draw(win)
    drawGrid(WIDTH, ROWS, win)
    pygame.display.update()


def randomSnack(rows, item):
    positions = item.body  # snakes positions

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
            continue
        else:
            break

    return (x, y)


def eval_genomes(genomes, config):
    global gen, FPS

    nets = []
    ge = []
    snakes = []

    # Create genomes, nets, snakes
    for genome_id, genome in genomes:
        genome.fitness = 0 
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        snakes.append(Snake((255, 0, 0), (10, 10)))
        ge.append(genome)

    gen += 1

    is_running = True

    clock = pygame.time.Clock()
    while is_running and len(snakes) > 0:
        clock.tick(FPS)  # Set frames per second to 10

        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  # Quits Pygame
                is_running = False
                pygame.quit()
                sys.exit()

        # Evalulate Data
        for x, snake in enumerate(snakes):
            snake.dist_food = math.sqrt((snake.apple.pos[1] - snake.head.pos[1])**2 + (snake.apple.pos[1] - snake.head.pos[1])**2)
            if snake.dist_food < snake.old_dist_food:
                ge[x].fitness += 0.1
            elif snake.dist_food >= snake.old_dist_food:
                ge[x].fitness -= 0.14
            snake.old_dist_food = snake.dist_food

            data = snake.get_data()

            output = nets[x].activate(data)  # Neural Network Output

            if output[0] > 0.5:  # left
                snake.dirnx = -1
                snake.dirny = 0
                
            if output[1] > 0.5:  # right
                snake.dirnx = 1
                snake.dirny = 0

            if output[2] > 0.5:  # up
                snake.dirnx = 0
                snake.dirny = -1

            if output[3] > 0.5:  # down
                snake.dirnx = 0
                snake.dirny = 1
                
        for i, snake in enumerate(snakes):  
            snake.move()
            if snake.spawn_apple():
                ge[i].fitness += 5
            
        # check snake death
        for i, snake in enumerate(snakes):
            if snake.head.pos in list(map(lambda z: z.pos, snake.body[1:])):  # check if body overlap
                # print("overlap death")
                ge[i].fitness -= 1
                snake.die()
                break

            if snake.dirnx == -1 and snake.head.pos[0] < 0 or snake.dirnx == 1 and snake.head.pos[0] >= ROWS or snake.dirny == 1 and snake.head.pos[1] >= ROWS or snake.dirny == -1 and snake.head.pos[1] < 0:  # check if body crashes with edge
                # print("edge death")
                snake.die()

            if ge[i].fitness < -10:  # check if snake doesn't eat apples
                # print("apple death")
                ge[i].fitness -= 2
                snake.die()
            
        # delete dead snakes
        for i, snake in enumerate(snakes):
            if snake.is_dying:
                ge[i].fitness -= 4.5
                snakes.pop(i)
                ge.pop(i)
                nets.pop(i)

        # print(list(map(lambda x: x.fitness, ge)))

        redrawWindow(WIN, snakes)  # Refresh screen

def run(config_path):
    global FPS
    # FPS = 20
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    
    # get most recent checkpoint
    checkpoints_path = 'checkpoints'
    for root, dirs, files in os.walk(checkpoints_path):
        if root == 'checkpoints':
            checkpoint_nums = list(map(lambda x: int(re.search('[0-9]*$', x).group(0)), files))
    # restore checkpoint
    if checkpoint_nums:
        best_checkpoint = 'neat-checkpoint-' + str(max(checkpoint_nums))
        p = neat.Checkpointer.restore_checkpoint(os.path.join(checkpoints_path, best_checkpoint))
    else:
        p = neat.Population(config)

    # p = neat.Checkpointer.restore_checkpoint(os.path.join(checkpoints_path,'neat-checkpoint-' + str(599)))

    # stats
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(100, filename_prefix=os.path.join(checkpoints_path,'neat-checkpoint-')))

    # evaluate genomes
    winner = p.run(eval_genomes, 1000)

    # save winner genome
    print("[SAVING] saving best genome ...")
    pickle.dump(winner, open('save_winner.pickle', 'wb'))

    print('\nBest genome:\n{!s}'.format(winner))


    FPS = 20
    replay_genome(config_path, "save_winner.pickle")



def replay_genome(config_path, genome_path):
    global FPS
    FPS = 20

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    genome = pickle.load(open(genome_path, "rb"))

    eval_genomes([(1, genome)], config)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    run(config_path)
    # replay_genome(config_path, "save_winner.pickle")