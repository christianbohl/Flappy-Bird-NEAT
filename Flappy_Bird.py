import pygame
import random
from pygame.locals import *
import sys
import os
from typing import List, Tuple

# Constants: Sizes in pixels / speeds in pixels per tick
# BIRD CONSTANTS
START_COORDS = (100, 400)
BIRD_SIZE = (46, 34)
GRAVITY_ACCEL = 2
JUMP_VELOCITY = 8

# PIPE CONSTANTS
PIPE_SPEED = 5
PIPE_WIDTH = 150
PIPE_GAP = 165

# BACKGROUND / GAME CONSTANTS
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 30
BACKGROUND_WIDTH = 880
BACKGROUND_SPEED = 3

# COLOR CODES
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Bird:
    """Represents the player's bird character."""

    def __init__(self):
        self.x, self.y = START_COORDS
        self.w, self.h = BIRD_SIZE
        self.accel = GRAVITY_ACCEL
        self.vel = JUMP_VELOCITY
        self.time_ini = 0
        self.time_elapsed = 0.0
        self.score = 0

    def time_init(self) -> None:
        """Initializes the timer when the bird jumps."""
        self.time_ini = pygame.time.get_ticks()

    def time_diff(self) -> None:
        """Calculates the time since the last jump."""
        self.time_elapsed = (pygame.time.get_ticks() - self.time_ini) / 1000

    def gravity(self) -> None:
        """Applies gravity to update vertical velocity and position."""
        self.vel = self.vel - (self.accel * self.time_elapsed)
        self.y = self.y - self.vel

    def jump(self) -> None:
        """Resets jump velocity and timer."""
        self.time_init()
        self.vel = JUMP_VELOCITY

    def draw_bird(self, surface: pygame.Surface, image: pygame.Surface) -> None:
        """Draws the bird on the given surface."""
        surface.blit(image, [self.x - 10, self.y - 3])

    def get_rect(self) -> pygame.Rect:
        """Returns the bounding rectangle for collision detection."""
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Pipe:
    """Represents an obstacle pipe pair in the game."""

    def __init__(self, x: int):
        self.x, self.y = (x, 0)
        self.w, self.h = (PIPE_WIDTH, random.randint(100, 550))
        self.gap = PIPE_GAP
        self.cleared = False  # True if bird passed through and scored

    def move(self) -> None:
        """Moves the pipes to the left."""
        self.x -= PIPE_SPEED

    def draw_pipe_upper(self, surface: pygame.Surface, image: pygame.Surface) -> None:
        """Draw upper pipe on a given surface."""
        surface.blit(image, [self.x - 8, self.h - 552]) # Draw upper pipe adjusting the image to the hitbox

    def draw_pipe_lower(self, surface: pygame.Surface, image: pygame.Surface) -> None:
        """Draw lower pipe on a given surface."""
        surface.blit(image, [self.x - 8, self.h + self.gap - 28]) # Draw lower pipe adjusting the image to the hitbox

    def get_rect(self) -> Tuple[pygame.Rect, pygame.Rect]:
        """Returns the bounding rectangles for upper and lower pipes for collision detection."""
        return (
            pygame.Rect(self.x, self.y, self.w, self.h),
            pygame.Rect(self.x, self.h + self.gap - 3, self.w, SCREEN_HEIGHT - (self.h + self.gap))
        )


class Background:
    """Represents the scrolling background."""

    def __init__(self) -> None:
        self.x, self.y = (0, 0)
        self.w = BACKGROUND_WIDTH

    def move(self) -> None:
        """Moves the background to create a scrolling effect."""
        self.x -= BACKGROUND_SPEED

    def draw_background(self, surface: pygame.Surface, image: pygame.Surface, x: int, y: int) -> None:
        """Draws the background on a given surface."""
        surface.blit(image, [x, y])


def draw_text_outline(
    surface: pygame.Surface, text: str, size: int, position: Tuple[int, int],
    text_color: Tuple[int, int, int], outline_color: Tuple[int, int, int] = BLACK,
    font_name: str = 'freesansbold.ttf', outline_thickness: int = 1
) -> None:
    """Draws text with an outline."""
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
    """Handles user inputs and game state transitions."""
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "MENU":
                    players.clear() # Reset the players and pipes when game is over
                    pipes.clear()
                    players.append(Bird())
                    pipes.append(Pipe(610))
                    for player in players:
                        player.time_init()
                    return "PLAY"

                elif game_state == "PLAY":
                    for player in players:
                        player.jump()

            elif event.key == pygame.K_r and game_state == "DEAD":
                return "MENU"

            elif event.key == pygame.K_q or event.type == QUIT:
                return "QUIT"

    return game_state


def resource_path(relative_path: str) -> str:
    """Returns absolute path to resource, compatible with PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main() -> None:
    """Main game loop and state management."""
    players = []
    pipes = []
    game_state = "MENU"

    pygame.init()
    pygame.display.set_caption('FLAPPY BIRD')
    clock = pygame.time.Clock()
    display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Load resources
    bg_image = pygame.image.load(resource_path("Images/bg_resize.png")).convert()
    bird_image = pygame.image.load(resource_path("Images/bird_resize.png")).convert_alpha()
    pipe_lower = pygame.image.load(resource_path("Images/pipe_lower.png")).convert_alpha()
    pipe_upper = pygame.image.load(resource_path("Images/pipe_upper.png")).convert_alpha()
    background = Background()

    while game_state != "QUIT":
        game_state = event_handler(game_state, players, pipes)

        if game_state == "MENU":
            # Draw scrolling background
            background.draw_background(display_surface, bg_image, background.x, background.y)
            background.draw_background(display_surface, bg_image, background.x + BACKGROUND_WIDTH, background.y)
            background.move()
            draw_text_outline(display_surface, "WELCOME TO FLAPPY BIRD", 36, (SCREEN_WIDTH//2, 300), WHITE)
            draw_text_outline(display_surface, "Press SPACE to start", 24, (SCREEN_WIDTH//2, 450), WHITE)
            draw_text_outline(display_surface, "Press Q to stop the game", 24, (SCREEN_WIDTH//2, 500), WHITE)

        elif game_state == "PLAY":
            # Generate new pipes when they reach the half point of the screen
            if pipes[-1].x <= 250:
                pipes.append(Pipe(610))
            pipes = [pipe for pipe in pipes if pipe.x + pipe.w > 0] # Delete pipes that left the screen

            if background.x <= -BACKGROUND_WIDTH:
                background.x = 0

            background.draw_background(display_surface, bg_image, background.x, background.y)
            background.draw_background(display_surface, bg_image, background.x + BACKGROUND_WIDTH, background.y)
            background.move() # Move and draw the background to create a continuous loop

            for player in players:
                if player.y >= SCREEN_HEIGHT or player.y + player.h <= 0:
                    game_state = "DEAD" # Check if players left the screen

            for pipe in pipes:
                pipe.move()
                pipe.draw_pipe_upper(display_surface, pipe_upper)
                pipe.draw_pipe_lower(display_surface, pipe_lower)
                upper_rect, lower_rect = pipe.get_rect()

                for player in players:
                    if player.get_rect().colliderect(upper_rect) or player.get_rect().colliderect(lower_rect):
                        game_state = "DEAD" #Check if players collided with any pipe
                    if player.x > pipe.x + pipe.w and not pipe.cleared:
                        player.score += 1
                        pipe.cleared = True # Update score and cleared status of pipes.

            draw_text_outline(display_surface, f"SCORE: {players[0].score:.0f}", 32, (SCREEN_WIDTH//2, 30), WHITE) # Draw score

            for player in players:
                player.time_diff()
                player.gravity()
                player.draw_bird(display_surface, bird_image)

        elif game_state == "DEAD":
            draw_text_outline(display_surface, "OH DEAR! YOU LOST", 36, (SCREEN_WIDTH//2, 300), WHITE)
            draw_text_outline(display_surface, f"FINAL SCORE: {players[0].score:.0f}", 24, (SCREEN_WIDTH//2, 450), WHITE)
            draw_text_outline(display_surface, "Press R to Restart", 24, (SCREEN_WIDTH//2, 570), WHITE)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("./error.log", "w") as f:
            f.write(str(e))
        input("An error occurred. Press Enter to exit.")
