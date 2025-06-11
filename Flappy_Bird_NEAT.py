import random
import pygame
from pygame.locals import *
import neat
import os
from typing import List, Tuple

# COLOR CONSTANTS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKBLUE = (0, 0, 63)

# GAME CONSTANTS
START_COORDS = (100, 400)
BIRD_SIZE = (46, 34)
GRAVITY_ACCEL = 2
JUMP_VELOCITY = 8

PIPE_SPEED = 5
PIPE_WIDTH = 150
PIPE_GAP = 165
PIPE_LOWER_LIM, PIPE_UPPER_LIM = (200, 600)

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 30
BACKGROUND_WIDTH = 880
BACKGROUND_SPEED = 3

class Bird:
    """Represents the bird agent in the Flappy Bird game."""
    def __init__(self):
        self.x, self.y = START_COORDS
        self.w, self.h = BIRD_SIZE
        self.accel = GRAVITY_ACCEL
        self.vel = JUMP_VELOCITY
        self.time_ini = 0
        self.time_elapsed = 0
        self.score = 0
        self.alive = True

    def time_init(self) -> None:
        """Initialize time marker for gravity calculations."""
        self.time_ini = pygame.time.get_ticks()

    def time_diff(self) -> None:
        """Update time elapsed since last jump."""
        self.time_elapsed = (pygame.time.get_ticks() - self.time_ini) / 1000

    def gravity(self) -> None:
        """Apply gravity to the bird's position."""
        self.vel -= self.accel * self.time_elapsed
        self.y -= self.vel

    def jump(self) -> None:
        """Simulate a jump by resetting velocity and time."""
        self.time_init()
        self.vel = JUMP_VELOCITY

    def draw_bird(self, surface: pygame.Surface, image: pygame.Surface) -> None:
        """Draw the bird image on the surface."""
        surface.blit(image, [self.x - 10, self.y - 3])

    def get_rect(self) -> pygame.Rect:
        """Return the bird's rectangular hitbox."""
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Pipe:
    """Represents a pipe obstacle in the game."""
    def __init__(self, x: int):
        self.x, self.y = (x, 0)
        self.w, self.h = (PIPE_WIDTH, random.randint(PIPE_LOWER_LIM, PIPE_UPPER_LIM))
        self.gap = PIPE_GAP
        self.cleared = False

    def move(self) -> None:
        """Move the pipe leftward."""
        self.x -= PIPE_SPEED

    def draw_pipe_upper(self, surface: pygame.Surface, image: pygame.Surface) -> None:
        """Draw the top pipe on a given surface."""
        surface.blit(image, [self.x - 8, self.h - 552])

    def draw_pipe_lower(self, surface: pygame.Surface, image: pygame.Surface) -> None:
        """Draw the bottom pipe on a given surface."""
        surface.blit(image, [self.x - 8, self.h + self.gap - 28])

    def get_rect(self) -> Tuple[pygame.Rect, pygame.Rect]:
        """Return both top and bottom pipe rectangles for collision detection."""
        return (
            pygame.Rect(self.x, self.y, self.w, self.h),
            pygame.Rect(self.x, self.h + self.gap - 3, self.w, SCREEN_HEIGHT - (self.h + self.gap))
        )


class Background:
    """Handles background scrolling."""
    def __init__(self):
        self.x, self.y = (0, 0)
        self.w = BACKGROUND_WIDTH

    def move(self) -> None:
        """Scroll the background left."""
        self.x -= BACKGROUND_SPEED

    def draw_background(self, surface: pygame.Surface, image: pygame.Surface, x: int, y: int) -> None:
        """Draw the background at a given location."""
        surface.blit(image, [x, y])


def draw_text_outline(surface: pygame.Surface, text: str, size: int, position: Tuple[int, int], text_color: Tuple[int, int, int],
                      outline_color: Tuple[int, int, int] = BLACK, font_name: str = 'freesansbold.ttf', outline_thickness: int = 1) -> None:
    """
    Draw text with an outline.
    """
    font = pygame.font.Font(font_name, size)
    for dx in [-outline_thickness, 0, outline_thickness]:
        for dy in [-outline_thickness, 0, outline_thickness]:
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                outline_rect = outline_surf.get_rect(center=(position[0] + dx, position[1] + dy))
                surface.blit(outline_surf, outline_rect)

    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=position)
    surface.blit(text_surf, text_rect)


def event_handler(game_state: str, players: List[Bird], pipes: List[Pipe]) -> str:
    """
    Handle user input and update the game state.
    """
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "MENU":
                    for player in players:
                        player.time_init()
                    return "PLAY"
                elif game_state == "PLAY":
                    for player in players:
                        player.jump()
            elif event.key == pygame.K_r and game_state == "DEAD":
                return "MENU"
            elif event.key == pygame.K_q:
                return "QUIT"
    return game_state


def main(genomes: List[Tuple[int, neat.DefaultGenome]], config_file: neat.Config) -> None:
    """
    Main NEAT training loop.
    """
    neural_networks = []
    genome_objects = []
    players = []
    pipes = [Pipe(610)]
    game_state = "MENU"

    # Create networks, genomes and bird instances
    for _, genome in genomes:
        network = neat.nn.FeedForwardNetwork.create(genome, config_file)
        neural_networks.append(network)
        players.append(Bird())
        genome.fitness = 0 # Initializing each genome's fitness
        genome_objects.append(genome)

    pygame.init()
    displaySurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('FLAPPY BIRD')
    clock = pygame.time.Clock()
    
    bg_image = pygame.image.load("./Images/bg_resize.png").convert()
    bird_image = pygame.image.load("./Images/bird_resize.png").convert_alpha()
    pipe_lower = pygame.image.load("./Images/pipe_lower.png").convert_alpha()
    pipe_upper = pygame.image.load("./Images/pipe_upper.png").convert_alpha()
    background = Background()

    while game_state != "QUIT":
        game_state = event_handler(game_state, players, pipes)

        if game_state == "MENU":
            background.draw_background(displaySurface, bg_image, background.x, background.y)
            background.draw_background(displaySurface, bg_image, background.x + 880, background.y)
            background.move()
            draw_text_outline(displaySurface, "FLAPPY BIRD NEUROEVOLUTION", 36, (SCREEN_WIDTH//2, 300), WHITE)
            draw_text_outline(displaySurface, "Press SPACE to start", 24, (SCREEN_WIDTH//2, 450), WHITE)
            draw_text_outline(displaySurface, "Press Q to stop the game", 24, (SCREEN_WIDTH//2, 500), WHITE)

        elif game_state == "PLAY":
            if pipes[-1].x <= 250:
                pipes.append(Pipe(610)) # Add pipes if current pipe reacher half of the screem

            pipes = [pipe for pipe in pipes if pipe.x + pipe.w > 0] # Clear pipes that left the screen
            if background.x <= -880:
                background.x = 0

            background.draw_background(displaySurface, bg_image, background.x, background.y)
            background.draw_background(displaySurface, bg_image, background.x + 880, background.y)
            background.move()

            # Calculate the variables the birds will "see" to play the game
            distance_next_pipe = min([pipe.x for pipe in pipes if not pipe.cleared]) - players[0].x #Calculate the distance of the bird til next pipe
            next_pipe = [pipe for pipe in pipes if not pipe.cleared][0]
            next_top_pipe_y = next_pipe.h # Get the coming upper pipe's height
            next_bottom_pipe_y = next_pipe.h + next_pipe.gap # Get the coming lower pipe's height

            for idx, player in enumerate(players):
                if player.y >= SCREEN_HEIGHT or player.y + player.h <= 0:
                    genome_objects[idx].fitness -= 10 # Punish players for going out the screen
                    player.alive = False

            for pipe in pipes:
                pipe.move()
                pipe.draw_pipe_upper(displaySurface, pipe_upper)
                pipe.draw_pipe_lower(displaySurface, pipe_lower)

                pipe_collision_upper, pipe_collision_lower = pipe.get_rect()
                for idx, player in enumerate(players):
                    player_collision = player.get_rect()
                    if player_collision.colliderect(pipe_collision_upper) or player_collision.colliderect(pipe_collision_lower):
                        genome_objects[idx].fitness -= 10 # Punish players for dying to a pipe
                        player.alive = False
                    if player.x > pipe.x + pipe.w and not pipe.cleared:
                        player.score += 1
                        genome_objects[idx].fitness += 20 #Rewards players for clearing a ser of pipes.
                        pipe.cleared = True

            indexes_dead = [i for i, p in enumerate(players) if not p.alive] # Clear players that have been labeled as dead
            for idx in sorted(indexes_dead, reverse=True):
                players.pop(idx)
                neural_networks.pop(idx)
                genome_objects.pop(idx)

            for idx, player in enumerate(players):
                player.time_diff()
                player.gravity()
                player.draw_bird(displaySurface, bird_image)
                genome_objects[idx].fitness += 0.1 # Reward the players minimally for surviving one tick
                output = neural_networks[idx].activate((player.y, distance_next_pipe, next_top_pipe_y, next_bottom_pipe_y)) # Get the model's response to jumping depending on x values
                if output[0] > 0.5: # Check if the model wants to jump
                    player.jump()

            if len(players) == 0:
                game_state = "QUIT"

            if genome_objects:
                max_fit = [round(g.fitness, 1) for g in genome_objects] # Get the max fitness and draw it
                draw_text_outline(displaySurface, f"Max Fitness: {max(max_fit):.1f} for {len(genome_objects)} alive birds", 32, (200, 30), WHITE)

        pygame.display.update()
        clock.tick(FPS)


path_file: str = os.getcwd() + '/config-feedforward.txt'

def run(file_path: str) -> None:
    """
    Set up NEAT configuration and start the evolutionary training process.
    """
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        file_path
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    statistics = neat.StatisticsReporter()
    population.add_reporter(statistics)
    winner = population.run(main, 10) # Run main game over generations


if __name__ == "__main__":
    run(path_file)
