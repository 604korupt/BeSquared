import sys, pygame
from board import Board

pygame.init()

"""
We want to keep track of the board in a 2d array

board =
[ red, blue, green]
[ red, green, yellow]
[ empty, green, blue]

0,0  0,1

"""

size = width, height = 800, 600
black = 0, 0, 0

# set the size of our screen
screen = pygame.display.set_mode(size)

size_of_block = 50
column_padding = 10
num_rows = 8
num_cols = 8

board = Board(screen, num_rows, num_cols, size_of_block, column_padding, width, height)


screen.fill(black)
board.draw()
while 1:
    #user events such as keystrokes will fire off here
    for event in pygame.event.get():
        #guess - when you press the X button on the GUI it comes in here as
        # pygame.QUIT
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            board.check_collision(event.pos)
            board.draw()

    board.update_time()
    pygame.display.flip()

