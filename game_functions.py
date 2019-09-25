import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:  # can use elif as each event is only connected to only one key
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def check_keyup_events(event, ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:  # can use elif as each event is only connected to only one key
        ship.moving_left = False


def check_events(ai_settings, screen, stats, play_button, mode_button, sb, ship, bullets, aliens):
    # check_events listens for user interaction and calls check_keyup_events() or check_keydown_events() accordingly
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, mouse_x, mouse_y, play_button, sb, ship, bullets, aliens)
            check_mode_button(ai_settings, screen, stats, mouse_x, mouse_y, mode_button, sb, ship, bullets, aliens)


def check_mode_button(ai_settings, screen, stats, mouse_x, mouse_y, mode_button, sb, ship, bullets, aliens):
    # new game when mouse clicked over alternative button
    button_clicked = mode_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        ai_settings.initialize_dynamic_settings()  # resets all settings that change with stage back to level 1.
        ai_settings.mode = True
        pygame.mouse.set_visible(False)  # hide mouse

        stats.reset_stats()  # resets things like number of aliens left in field from any previous game
        stats.game_active = True

        sb.prep_score()
        sb.prep_high_score()  # is this particular line really necessary? I thought prep_high_score has the prep called
        # automatically whenever it is changed in check_bullet_alien_collisions() via check_high_score(). Redundancy?
        sb.prep_level()
        sb.prep_ships()

        aliens.empty()
        bullets.empty()

        create_fleet(ai_settings, screen, ai_settings.mode, ship, aliens)
        ship.center_ship()


def check_play_button(ai_settings, screen, stats, mouse_x, mouse_y, play_button, sb, ship, bullets, aliens):
    # new game when mouse clicked over button
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        ai_settings.initialize_dynamic_settings()  # resets all settings that change with stage back to level 1.
        pygame.mouse.set_visible(False)  # hide mouse

        stats.reset_stats()  # resets things like number of aliens left in field from any previous game
        stats.game_active = True

        sb.prep_score()
        sb.prep_high_score()  # is this particular line really necessary? I thought prep_high_score has the prep called
        # automatically whenever it is changed in check_bullet_alien_collisions() via check_high_score(). Redundancy?
        sb.prep_level()
        sb.prep_ships()

        aliens.empty()
        bullets.empty()

        create_fleet(ai_settings, screen, ai_settings.mode, ship, aliens)
        ship.center_ship()


def update_screen(ai_settings, screen, stats, play_button, mode_button, sb, ship, bullets, aliens):
    # redraw screen with color each loop pass
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    sb.show_score()
    # Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()
        mode_button.draw_button()
    pygame.display.flip()  # Make recent screen visible, by flipping it over the old one


def update_bullets(ai_settings, screen, stats, sb, mode, ship, bullets, aliens):
    bullets.update()  # move bullets
    for bullet in bullets.copy():  # remove bullets as they fly off screen
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collisions(ai_settings, screen, stats, sb, mode, ship, bullets, aliens)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, mode, ship, bullets, aliens):
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)  # collisions is a dictionary variable (a map)
    # Remember that each value in collisions is a bullet ID followed by a list of aliens its collided with
    if collisions:
        for bullet in collisions.values():  # executes once for each bullet active in this game tic
            stats.score += ai_settings.alien_points * len(bullet)  # len(bullet) == size of alien list for the bullet
        # we use a dictionary because, if our bullets are thick and capable of hitting multiple aliens, they will
        # acknowledge each alien rather than simply detect a single impact and increment points once.
        # Also, if two bullets were to somehow hit aliens at the same tic, the game needs to account for each bullet
        # individually and not merely scream "a bullet has hit during this tic, increment score once!"
        sb.prep_score()
        check_high_score(ai_settings, stats, sb)
    if len(aliens) == 0:
        bullets.empty()  # destroy all bullets, spawn new fleet, increase speedup_scale in settings
        ai_settings.increase_speed()
        # increase the level and tell scoreboard to prep it
        stats.level += 1
        sb.prep_level()
        ai_settings.levelUp.play()

        create_fleet(ai_settings, screen, mode, ship, aliens)


def check_high_score(ai_settings, stats, sb):
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()  # see annotation above prep_score() in scoreboard.py for explanation
        if not stats.broke_high_score:  # so high score sound will only play once per game.
            ai_settings.brokeHighScore.play()
            stats.broke_high_score = True


def get_number_aliens_x(ai_settings, alien_width):
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, mode, aliens, alien_number, row_number):
    alien = Alien(ai_settings, screen, mode)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, mode, ship, aliens):
    alien = Alien(ai_settings, screen, mode)  # create a "dummy" alien to get its dimensions
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)  # use those dimensions to find suitable number
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
    # now spawn them
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, mode, aliens, alien_number, row_number)


def check_fleet_edges(ai_settings, aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break  # break so we don't bother examining anymore aliens in the Group


def change_fleet_direction(ai_settings, aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, screen, sb, mode, ship, bullets, aliens):
    # Respond to ship being hit by alien.
    ship.explode.play()
    if stats.ships_left > 0:
        # Decrement ships_left.
        stats.ships_left -= 1

        # update scoreboard
        sb.prep_ships()

        # empty groups
        aliens.empty()
        bullets.empty()

        # restart fleet and spawn new ship (really just centering old one)
        create_fleet(ai_settings, screen, mode, ship, aliens)
        ship.center_ship()

        # Pause
        sleep(0.5)
    else:
        ai_settings.gameOver.play()
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats, screen, sb, mode, ship, bullets, aliens):
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treat this the same as if the ship got hit.
            ship_hit(ai_settings, stats, screen, sb, mode, ship, bullets, aliens)
            break  # break so we don't bother examining anymore aliens in the Group


def update_aliens(ai_settings, stats, screen, sb, mode, ship, bullets, aliens):
    check_fleet_edges(ai_settings, aliens)  # make sure to see if fleet is on an edge. If so, change their direction.
    aliens.update()
    # look for alien ship collisions
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, sb, mode, ship, bullets, aliens)
    # Look for aliens hitting the bottom of the screen.
    check_aliens_bottom(ai_settings, stats, screen, sb, mode, ship, bullets, aliens)
