import pygame
import Logic
import time

## game UI n back end
SCREEN_SIZE = (1024, 1024)
LETTER_COLOR = (255, 255, 255)

START_X = 194
START_Y = 124
OFFSET_X = 103.5
OFFSET_Y = 104.4
SIZE = 94

# wordle feed back color
WRONG = (65, 65, 67)
WRONG_POS = (182, 161, 66)
CORRECT = (83, 138, 78)

# game
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
background = pygame.image.load("/home/izu/Izu/Projects/wordle-game/assets/background.png")

class gameVars:
    def __init__(self):
        self.reset()

    def reset(self):
        self.answer = Logic.choose_word()
        self.choices = []
        self.temp = []
        self.feedback = []

        self.running = True
        self.prev = 0
        self.current = 0
        
        screen.blit(background, (0, 0))
        print(self.answer)

vars = gameVars()

# game
def play_game():
    pygame.draw.rect(screen, (255, 0, 0), (START_X, START_Y, 10, 10))
    font = pygame.font.SysFont(None, 110)
    screen.blit(background, (0, 0))


    while vars.running:
        changed = False
        changed = False

        if len(vars.temp) != vars.prev:
            vars.prev = len(vars.temp)
            print(vars.temp)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                vars.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if len(vars.temp) != 0:
                        changed = True
                        vars.temp.pop()

                
                elif event.key == pygame.K_RETURN:
                    choice = "".join(vars.temp)
                    changed = True

                    if Logic.validate_choice(choice):
                        vars.current += 1
                        vars.choices.append(choice)
                        vars.temp.clear()
                        vars.feedback.append(Logic.validate_ans(choice, vars.answer))

                    else:
                        print("Invalid")

                else:
                    char = event.unicode
                    changed = True
                    
                    if char.isalpha() and len(char) == 1 and len(vars.temp) < 5:
                        vars.temp.append(char)

        if changed:
            screen.blit(background, (0, 0))
            dy = int(START_Y + OFFSET_Y * vars.current + SIZE / 2)
            
            for ox in range(len(vars.temp)):
                dx = int(START_X + OFFSET_X * ox + SIZE /2)

                text = font.render(vars.temp[ox].upper(), True, LETTER_COLOR)
                text_rect = text.get_rect()
                text_rect.center = (dx, dy)

                screen.blit(text, text_rect)
            # board
            for oy in range(len(vars.choices)):
                for ox in range(5):
                    dx = int(START_X + OFFSET_X * ox)
                    dy = int(START_Y + OFFSET_Y * oy)

                    # feedback
                    if vars.feedback[oy][ox] == -1:
                        color = WRONG

                    elif vars.feedback[oy][ox] == 0:
                        color = WRONG_POS

                    else:
                        color = CORRECT

                    pygame.draw.rect(screen, color, (dx, dy, SIZE, SIZE))

                    # words
                    dy = int(START_Y + OFFSET_Y * oy + SIZE / 2)
                    dx = int(START_X + OFFSET_X * ox + SIZE / 2)

                    text = font.render(vars.choices[oy][ox].upper(), True, LETTER_COLOR)
                    text_rect = text.get_rect()
                    text_rect.center = (dx, dy)

                    screen.blit(text, text_rect)
            
                if not Logic.is_won(vars.feedback[oy]):
                    pygame.display.update()
                    print("Won")
                    time.sleep(1)
                    vars.reset()

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    while True:
        play_game()