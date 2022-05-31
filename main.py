import pygame
import random
import os
import neat


WIDTH = 500
HEIGHT = 500
ROWS = 20
WIN = pygame.display.set_mode((WIDTH, HEIGHT))


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
    body = []
    turns = {}
    is_dying = False

    def __init__(self, color, pos):
        self.color = color
        self.head = Body(pos)  # set head to front
        self.body.append(self.head)  # add cube to body

        self.dirnx = 0  # Direction x, y
        self.dirny = 1

    def move(self):
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:  # check if user wants to close window
        #         pygame.quit()

        #     keys = pygame.key.get_pressed()  # get pressed keys

        #     for key in keys:  # loop through all keys
        #         if keys[pygame.K_LEFT]:
        #             self.dirnx = -1
        #             self.dirny = 0
                    
        #         elif keys[pygame.K_RIGHT]:
        #             self.dirnx = 1
        #             self.dirny = 0

        #         elif keys[pygame.K_UP]:
        #             self.dirnx = 0
        #             self.dirny = -1

        #         elif keys[pygame.K_DOWN]:
        #             self.dirnx = 0
        #             self.dirny = 1

        #     self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]


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
                    self.die()
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

    def draw(self, surface, eyes=False):
        for i, c in enumerate(self.body):
            if i == 0:  # for the first cube in the list we want to draw eyes
                c.draw(surface, True)  # adding the true as an argument will tell us to draw eyes
            else:
                c.draw(surface)  # otherwise we will just draw a cube

    def die(self):
        print('Score: ', len(self.body))
        self.reset((10, 10))
        self.is_dying = True

    def get_data(self):
        x_dist_wall = self.rows - self.head.pos[0]
        y_dist_wall = self.rows - self.head.pos[1]
        x_dist_tail = self.body[-1].pos[0] - self.head.pos[0]
        y_dist_tail = self.body[-1].pos[1] - self.head.pos[1]
        # x_dist_food = 0
        # y_dist_food = 0

        return (x_dist_wall, y_dist_wall, x_dist_tail, y_dist_tail)


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


def redrawWindow(win, snakes, apple):
    win.fill((0, 0, 0))
    
    for snake in snakes:
        snake.draw(win)
    apple.draw(win)
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


def main(genomes, config):
    nets = []
    ge = []
    snakes = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        snakes.append(Snake((255, 0, 0), (10, 10)))
        ge.append(genome)

    # snakes.pop(0)
    # ge.pop(0)
    # nets.pop(0)

    apple = Apple(randomSnack(ROWS, snakes[0]))


    is_running = True

    clock = pygame.time.Clock()
    while is_running and len(snakes) > 0:
        clock.tick(5)  # Set frames per second to 10
        for event in pygame.event.get():  # Quits Pygame
            if event.type == pygame.QUIT:
                is_running = False
                pygame.quit()
                break


        # Evalulate Data
        for x, snake in enumerate(snakes):
            ge[x].fitness += 0.1

            x_dist_food = apple.pos[0] - snake.head.pos[0]
            y_dist_food = apple.pos[1] - snake.head.pos[1]
            data = snake.get_data()
            data = (*data, x_dist_food, y_dist_food)

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
                
            snake.turns[snake.head.pos[:]] = [snake.dirnx, snake.dirny]

        for snake in snakes:  
            snake.move()
            if snake.body[0].pos == apple.pos:  # when apple is eaten
                snake.addCube()
                apple = Apple(randomSnack(ROWS, snake))

        for i, snake in enumerate(snakes):
            for x in range(len(snake.body)-1):
                if snake.body[x].pos in list(map(lambda z: z.pos, snake.body[x + 1:])):
                    # This will check if any of the positions in our body list overlap
                    # print("die")
                    snake.die()
                    # break
            
            if snake.is_dying:
                ge[i].fitness -= 1.5
                snakes.pop(i)
                ge.pop(i)
                nets.pop(i)


        redrawWindow(WIN, snakes, apple)  # Refresh screen
    pygame.time.delay(3000)

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 100)

    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)