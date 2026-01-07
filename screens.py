import pygame

MENU, RULES, GAME, GAME_OVER, CONGRATS = "menu", "rules", "game", "game_over", "congrats"

class Button:
    def __init__(self, text, rect):
        self.text = text
        self.rect = pygame.Rect(rect)

    def draw(self, screen, font):
        pygame.draw.rect(screen, (180, 180, 180), self.rect)
        label = font.render(self.text, True, (0, 0, 0))
        screen.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


def draw_menu(screen, font, event, buttons):
    screen.fill((230, 230, 230))

    for b in buttons:
        b.draw(screen, font)

    if event:
        for b in buttons:
            if b.is_clicked(event):
                if b.text == "Play":
                    return GAME
                if b.text == "Rules":
                    return RULES
                if b.text == "Exit":
                    pygame.quit()
                    exit()

    return MENU


def draw_rules(screen, font, event):
    screen.fill((245, 245, 245))
    lines = [
        "RULES:",
        "- Collect all coins",
        "- Avoid monsters",
        "- Player moves continuously",
        "- Window grows with each level",
        "",
        "Press ESC to return"
    ]

    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, (0, 0, 0)), (40, 40 + i * 30))

    if event and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return MENU

    return RULES


def draw_game_over(screen, font, event):
    screen.fill((0, 0, 0))
    text = font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=screen.get_rect().center))

    sub = font.render("Press ESC to return to menu", True, (200, 200, 200))
    screen.blit(sub, (screen.get_width() // 2 - 120, screen.get_height() // 2 + 40))

    if event and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return MENU

    return GAME_OVER

def draw_congrats(screen, font, event):
    screen.fill((0, 0, 0))

    title = font.render("CONGRATULATIONS!", True, (255, 215, 0))
    screen.blit(title, title.get_rect(center=(screen.get_width()//2, 120)))

    sub = font.render("You completed all mazes!", True, (200, 200, 200))
    screen.blit(sub, sub.get_rect(center=(screen.get_width()//2, 180)))

    hint = font.render("Press ESC to return to menu", True, (150, 150, 150))
    screen.blit(hint, hint.get_rect(center=(screen.get_width()//2, 240)))

    if event and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return MENU

    return CONGRATS
