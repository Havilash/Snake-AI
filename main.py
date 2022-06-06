import os
import sys
import pygame
import neat
import random
import pickle
import re

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
        self.apple_frame_count = 0

        self.color = color
        self.body = []
        self.head = Body(pos)  # set head to front
        self.body.append(self.head)  # add cube to body

        self.is_dying = False
        self.turns = {}

        self.dirnx = 0  # Direction x
        self.dirny = 1  # Direction y


        self.apple = Apple(randomSnack(ROWS, self))


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

    def spawn_apple(self):
        if self.body[0].pos == self.apple.pos:  # when apple is eaten
            self.addCube()
            self.apple = Apple(randomSnack(ROWS, self))
            self.apple_frame_count = 0
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
        # Distance to the Walls
        # dist_wall_right = self.rows - self.head.pos[0]
        # dist_wall_bottom = self.rows - self.head.pos[1]
        # dist_wall_left = self.head.pos[0]
        # dist_wall_top = self.head.pos[1]

        # x_dist_tail = self.body[-1].pos[0] - self.head.pos[0]
        # y_dist_tail = self.body[-1].pos[1] - self.head.pos[1]

        x_dist_food = self.apple.pos[0] - self.head.pos[0]
        y_dist_food = self.apple.pos[1] - self.head.pos[1]

        is_obstacle = [[],[],[],[]]
        for i, pos_val in enumerate([(0, 1), (0, -1), (1, 0), (-1, 0)]):
            pos = (self.head.pos[0] + pos_val[0], self.head.pos[1] + pos_val[1])
            if pos in list(map(lambda z: z.pos, self.body[1:])) or (pos[0] < 0 and pos[0] >= ROWS and pos[1] >= ROWS and pos[1] < 0):  # check if body overlap
                is_obstacle[i] = 1
                continue
            is_obstacle[i] = 0

        return (x_dist_food, y_dist_food, *is_obstacle)
        # return (x_dist_food, y_dist_food)


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
    APPLE_TIME = 100  # livetime without eating apples

    nets = []
    ge = []
    snakes = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        snakes.append(Snake((255, 0, 0), (10, 10)))
        ge.append(genome)

    gen += 1

    is_running = True

    clock = pygame.time.Clock()
    
    while is_running and len(snakes) > 0:
        clock.tick(FPS)  # Set frames per second to 10
        for event in pygame.event.get():  # Quits Pygame
            if event.type == pygame.QUIT:
                is_running = False
                pygame.quit()
                sys.exit()

        # Evalulate Data
        for x, snake in enumerate(snakes):
            snake.apple_frame_count += 1
            ge[x].fitness += 0.1

            data = snake.get_data()

            output = nets[x].activate(data)  # Neural Network Output

            if output[0] > 0.5:
                snake.dirnx = -1
                snake.dirny = 0
                
            elif output[1] > 0.5:
                snake.dirnx = 1
                snake.dirny = 0

            elif output[2] > 0.5:
                snake.dirnx = 0
                snake.dirny = -1

            elif output[3] > 0.5:
                snake.dirnx = 0
                snake.dirny = 1
                
        for i, snake in enumerate(snakes):  
            snake.move()
            if snake.spawn_apple():
                ge[i].fitness += 5
            

        for i, snake in enumerate(snakes):
            if snake.head.pos in list(map(lambda z: z.pos, snake.body[1:])):  # check if body overlap
                # print("overlap death")
                snake.die()
                break

            if snake.dirnx == -1 and snake.head.pos[0] < 0 or snake.dirnx == 1 and snake.head.pos[0] >= ROWS or snake.dirny == 1 and snake.head.pos[1] >= ROWS or snake.dirny == -1 and snake.head.pos[1] < 0:
                # print("edge death")
                snake.die()

            if snake.apple_frame_count > APPLE_TIME:
                # print("apple death")
                ge[i].fitness -= 7
                snake.die()
            
        for i, snake in enumerate(snakes):
            if snake.is_dying:
                ge[i].fitness -= 2
                snakes.pop(i)
                ge.pop(i)
                nets.pop(i)

        # print(list(map(lambda x: x.fitness, ge)), list(map(lambda x: x.apple_frame_count, snakes)))

        redrawWindow(WIN, snakes)  # Refresh screen

def run(config_path):
    global FPS

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)


    for root, dirs, files in os.walk('checkpoints'):
        checkpoint_nums = list(map(lambda x: int(re.search('[0-9]*$', x).group(0)), files))
        best_checkpoint = max(checkpoint_nums)
            
    p = neat.Checkpointer.restore_checkpoint('checkpoints/neat-checkpoint-' + str(best_checkpoint))

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(50, filename_prefix='checkpoints/neat-checkpoint-'))

    # pe = neat.ThreadedEvaluator(1 + multiprocessing.cpu_count(), eval_genomes)
    # winner = p.run(pe.evaluate, 10)

    winner = p.run(eval_genomes, 300)

    print("[SAVING] saving best genome ...")
    pickle.dump(winner, open('save_winner.pickle', 'wb'))

    print('\nBest genome:\n{!s}'.format(winner))

    FPS = 20
    replay_genome(config_path, "save_winner.pickle")



def replay_genome(config_path, genome_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    genome = pickle.load(open(genome_path, "rb"))

    eval_genomes([(1, genome)], config)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    run(config_path)
    # replay_genome(config_path, "save_genome.pickle")