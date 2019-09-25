import pygame
from settings import Settings  # imports just a specific class from settings file
from ship import Ship  # imports just a specific class from ship file
import game_functions as gf  # imports entire game_functions file and assigns it alias "gf"
from pygame.sprite import Group
from game_stats import GameStats
import button as butt
from scoreboard import Scoreboard
# questions: research statements in ship.py and bullet.py and possibly redundant statement in check_play_button() in gf


def run_game():
    # initialize game, create screen object, group of bullets, and group of aliens
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")
    play_button = butt.Button(ai_settings, screen, "Normal")
    mode_button = butt.ModeButton(ai_settings, screen, "Scientology Mode")  # I added this at 3 in the morning...
    set_mode = ai_settings.mode
    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings, screen, stats)
    ship = Ship(ai_settings, screen)
    bullets = Group()
    aliens = Group()
    gf.create_fleet(ai_settings, screen, set_mode, ship, aliens)  # fleet
    # Main loop for game
    while True:
        # Listen for user activity, and input all data. gf is a # file alias
        set_mode = ai_settings.mode
        gf.check_events(ai_settings, screen, stats, play_button, mode_button, sb, ship, bullets, aliens)
        if stats.game_active:
            # put things in motion
            ship.update()
            gf.update_bullets(ai_settings, screen, stats, sb, set_mode, ship, bullets, aliens)
            gf.update_aliens(ai_settings, stats, screen, sb, set_mode, ship, bullets, aliens)
        gf.update_screen(ai_settings, screen, stats, play_button, mode_button, sb, ship, bullets, aliens)


run_game()
