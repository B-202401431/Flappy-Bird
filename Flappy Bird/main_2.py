import random
import sys
import os
import pygame
from pygame.locals import *

# Initialize pygame
pygame.init()

# Global variables
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = int(SCREENHEIGHT * 0.8)
FPSCLOCK = pygame.time.Clock()

# Game Assets
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/redbird-upflap.png'
BACKGROUND = 'gallery/sprites/background-day.png'
PIPE = 'gallery/sprites/pipe-green.png'

# File to store high score
HIGH_SCORE_FILE = "high_score.txt"
FONT = pygame.font.SysFont(None, 30)

# Difficulty levels
DIFFICULTY_SETTINGS = {
    'Easy': {'pipe_gap': 160, 'pipe_speed': 3},
    'Medium': {'pipe_gap': 140, 'pipe_speed': 4},
    'Hard': {'pipe_gap': 120, 'pipe_speed': 5},
}
difficulty = 'Medium'  # Default

new_high_score_achieved = False
new_high_score_counter = 0


def get_high_score():
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0
    with open(HIGH_SCORE_FILE, 'r') as f:
        try:
            return int(f.read())
        except ValueError:
            return 0

def save_high_score(score):
    global new_high_score_achieved
    high_score = get_high_score()
    if score > high_score:
        new_high_score_achieved = True
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(score))


def chooseDifficulty():
    global difficulty
    options = list(DIFFICULTY_SETTINGS.keys())
    selected = 0

    while True:
        SCREEN.fill((0, 0, 0))
        title = FONT.render("Choose Difficulty", True, (255, 255, 255))
        SCREEN.blit(title, ((SCREENWIDTH - title.get_width()) // 2, 50))

        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            text = FONT.render(opt, True, color)
            SCREEN.blit(text, ((SCREENWIDTH - text.get_width()) // 2, 150 + i * 40))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == K_RETURN:
                    difficulty = options[selected]
                    return
        FPSCLOCK.tick(FPS)


def welcomeScreen():
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0
    high_score = get_high_score()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))

        # Show difficulty
        diff_text = FONT.render(f'Difficulty: {difficulty}', True, (255, 255, 255))
        SCREEN.blit(diff_text, (10, SCREENHEIGHT - 30))

        # High Score
        high_digits = [int(x) for x in list(str(high_score))]
        width = sum(GAME_SPRITES['numbers'][d].get_width() for d in high_digits)
        xoffset = (SCREENWIDTH - width) / 2
        for d in high_digits:
            SCREEN.blit(GAME_SPRITES['numbers'][d], (xoffset, SCREENHEIGHT * 0.03))
            xoffset += GAME_SPRITES['numbers'][d].get_width()

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame():
    global new_high_score_achieved, new_high_score_counter
    new_high_score_achieved = False
    new_high_score_counter = 30  # Frames to show message

    settings = DIFFICULTY_SETTINGS[difficulty]
    pipe_gap = settings['pipe_gap']
    pipe_speed = settings['pipe_speed']

    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)

    bird_velocity_y = -9
    max_velocity_y = 10
    gravity = 1
    flap_velocity = -9
    bird_flapped = False

    newPipe1 = getRandomPipe(pipe_gap)
    newPipe2 = getRandomPipe(pipe_gap)

    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    bird_velocity_y = flap_velocity
                    bird_flapped = True
                    GAME_SOUNDS['wing'].play()

        if bird_velocity_y < max_velocity_y and not bird_flapped:
            bird_velocity_y += gravity

        if bird_flapped:
            bird_flapped = False

        playery += min(bird_velocity_y, GROUNDY - playery - GAME_SPRITES['player'].get_height())

        # Collision
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            if (playerx + GAME_SPRITES['player'].get_width() > uPipe['x']) and (playerx < uPipe['x'] + GAME_SPRITES['pipe'][0].get_width()):
                if playery < uPipe['y'] + GAME_SPRITES['pipe'][0].get_height() or playery + GAME_SPRITES['player'].get_height() > lPipe['y']:
                    GAME_SOUNDS['hit'].play()
                    save_high_score(score)
                    return

        if playery > GROUNDY - 25:
            GAME_SOUNDS['die'].play()
            save_high_score(score)
            return

        # Move pipes
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] -= pipe_speed
            lowerPipe['x'] -= pipe_speed

        # Add new pipe
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe(pipe_gap)
            upperPipes.append({'x': SCREENWIDTH + 10, 'y': newpipe[0]['y']})
            lowerPipes.append({'x': SCREENWIDTH + 10, 'y': newpipe[1]['y']})

        # Remove pipes
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + pipe_speed:
                score += 1
                GAME_SOUNDS['point'].play()

        # Draw
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
        SCREEN.blit(GAME_SPRITES['base'], (0, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        # Score draw
        myDigits = [int(x) for x in list(str(score))]
        width = sum(GAME_SPRITES['numbers'][d].get_width() for d in myDigits)
        Xoffset = (SCREENWIDTH - width) / 2
        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()

        # New high score message (only for limited frames)
        if new_high_score_achieved and new_high_score_counter > 0:
            text_surface = FONT.render('New High Score!', True, (255, 0, 0))
            SCREEN.blit(text_surface, ((SCREENWIDTH - text_surface.get_width()) / 2, SCREENHEIGHT * 0.2))
            new_high_score_counter -= 1

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def getRandomPipe(pipe_gap):
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + pipe_gap
    pipe = [
        {'x': pipeX, 'y': -y1},
        {'x': pipeX, 'y': y2}
    ]
    return pipe


if __name__ == "__main__":
    pygame.display.set_caption('Flappy Bird')
    GAME_SPRITES['numbers'] = tuple(pygame.image.load(f'gallery/sprites/{i}.png').convert_alpha() for i in range(10))
    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    chooseDifficulty()
    while True:
        welcomeScreen()
        mainGame()
