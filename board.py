import pygame
from jewel import Jewel
from bomb import Bomb
from random import randint
from random import seed
import time

class Board:

    def __init__(self, screen, rows, cols, block_size, padding_size, width_of_screen, height_of_screen):
        # seed the random number generator
        # this needs a different number every time the game starts
        # the trick to do that is to pass in the time right now in seconds
        seed(time.time())
        self.screen = screen
        self.width = width_of_screen
        self.height = height_of_screen
        self.rows = rows
        self.cols = cols
        self.block_size = block_size
        self.padding = padding_size
        self.is_game_over = False
        self.blocks_needed_each_col = []
        # do the math to figure out where to start drawing the board based on the side of the screen
        # number of padding spaces is always the number of blocks minus 1
        self.width_of_board = (cols * block_size) + ((cols - 1) * padding_size)
        space_of_left_of_board = int((width_of_screen - self.width_of_board) / 2)

        # load the high scores from the text file
        self.scores = []
        lines = []
        with open('scores.txt') as f:
            lines = f.readlines()
        for line in lines:
            # The line from the file has the new line character at the end and we don't want that
            line = line[0:-1]
            (name, score) = line.split(',')
            self.scores.append((name, score))

        # specify the board start parameters
        self.jewels = []
        self.board_start_x = space_of_left_of_board
        self.board_start_y = 70
        self.score = 0
        self.points_per_block = 5
        self.bomb_counter = 0
        self.num_bombs = 0
        self.points_per_bomb = 200
        self.num_blocks_to_add_second = 3
        self.time_of_game = 15
        self.seconds_left = self.time_of_game
        self.last_second = 0
        self.wrong_sound = pygame.mixer.Sound("wrong.wav")
        self.points_sound = pygame.mixer.Sound("points.wav")
        self.explosion_sound = pygame.mixer.Sound("explosion.wav")
        self.retry = []
        # initialize font for high score
        self.score_font = pygame.font.SysFont("Comic Sans MS", 20)

        # the board needs to know if a box is highlighted because it has to wait for another click to
        # complete the process of highlighting two blocks and switching them
        self.is_waiting_for_second_selection = False
        self.pos_selected_box = []
        self.pos_switch_box = []
        self.init_game_board()

    def init_game_board(self):
        for i in range(self.rows):
            row = []
            # in order to check the randomness as the jewels are created we have to add the row first
            # and then just overwrite it with each new jewel that's added
            self.jewels.append([])
            for j in range(self.cols):
                found_good_color = False
                row.append(Jewel(self.get_random_color(), self.block_size))
                while not found_good_color:
                    self.jewels[i] = row
                    if not self.check_3_in_a_row_horizontal(i, j) and not self.check_3_in_a_row_vertical(i, j):
                        found_good_color = True
                    else:
                        row[-1] = Jewel(self.get_random_color(), self.block_size)

    def check_collision(self, mouse_position):
        if self.is_game_over:
            if self.retry.collidepoint(mouse_position):
                self.score = 0
                self.init_game_board()
                self.seconds_left = self.time_of_game
                self.is_game_over = False
            return

        for cur_row in range(self.rows):
            for cur_col in range(self.cols):
                # checking the collision itself will draw the border on the box
                # but we need to know when one of these boxes is_selected is true
                if self.jewels[cur_row][cur_col].check_collision(mouse_position):
                    # if something comes back true and we're not waiting for a
                    # second box to be clicked we should change that
                    if not self.is_waiting_for_second_selection:
                        # check to see if a bomb was clicked
                        if type(self.jewels[cur_row][cur_col]) is Bomb:
                            self.bomb_explosion(cur_row, cur_col)
                            self.fill_cleared_blocks()
                        else:
                            self.is_waiting_for_second_selection = True
                            self.pos_selected_box = (cur_row, cur_col)
                            # turn on the selection for that box
                            self.jewels[cur_row][cur_col].set_selection(True)
                        return
                    else:
                        # what if we click the currently selected box again
                        # we should flip that we are not waiting for a second
                        # selection, and also we need to deselect the box
                        if cur_row == self.pos_selected_box[0] and cur_col == self.pos_selected_box[1]:
                            self.is_waiting_for_second_selection = False
                            self.jewels[cur_row][cur_col].set_selection(False)
                            return

                        # we get here when we are waiting for a selection so
                        # check to see if the clicked position is
                        # up/down/left/right of the selected Box
                        if self.is_valid_switch_box(cur_row, cur_col):
                            self.pos_switch_box = (cur_row, cur_col)
                            # deselect the original box we clicked and switch
                            # these two colors boxes (2,1)
                            self.jewels[self.pos_selected_box[0]][
                                self.pos_selected_box[1]].set_selection(False)
                            self.switch_blocks()
                            self.is_waiting_for_second_selection = False
                            self.draw()
                            pygame.time.wait(250)
                            if not self.clear_adjacent_blocks():
                                # switch the blocks back
                                pygame.mixer.Sound.play(self.wrong_sound)
                                pygame.mixer.music.stop()
                                pygame.time.wait(250)
                                self.switch_blocks()
                        else:
                            print("You cannot swap with a diagonal box")
                        return

    def draw(self):
        if not self.is_game_over:
            self.screen.fill((0, 0, 0))
            self.draw_time_bar()
            for cur_row in range(self.rows):
                for cur_col in range(self.cols):
                    x_value = self.board_start_x + ((self.block_size + self.padding) * cur_col)
                    y_value = self.board_start_y + ((self.block_size + self.padding) * cur_row)
                    self.jewels[cur_row][cur_col].draw(self.screen, x_value, y_value)

        lbl_score = self.score_font.render("Score: " + str(self.score), 1, (255, 255, 255))
        self.screen.blit(lbl_score, (30, 30))
        lbl_high_score = self.score_font.render("--High Scores-- ", 1, (255, 255, 255))
        self.screen.blit(lbl_high_score, (15, self.height/4))
        cur_y = self.height/4 + 30
        for s in self.scores:
            label = self.score_font.render(s[0] + " : " + str(s[1]), 1, (255, 255, 255))
            self.screen.blit(label, (30, cur_y))
            cur_y += 30

        if self.is_game_over:
            lbl_game_over = self.score_font.render("Game Over", 1, (255, 255, 255))
            self.screen.blit(lbl_game_over, (30, 60))
            self.show_retry()

        pygame.display.flip()

    def get_random_color(self):
        # use a random number generator to pick a number from 1 to 5
        color = randint(1,5)
        if color == 1:
            return (255,0,0) #red
        elif color == 2:
            return (0,255,0) #green
        elif color == 3:
            return (0,0,255) #blue
        elif color == 4:
            return (255,225,0) #yellow
        elif color == 5:
            return (137,0,255) # purple

    def check_3_in_a_row_horizontal(self, row, col):
        #check the previous two if it is possible
        cur_jem_color = self.jewels[row][col].get_color()
        try:
            if col - 2 >= 0:
                if cur_jem_color == self.jewels[row][col - 2].get_color() and cur_jem_color == self.jewels[row][col - 1].get_color():
                        return True
            #check the previous and next if it is possible
            elif col - 1 >= 0:
                if cur_jem_color == self.jewels[row][col - 1].get_color() and cur_jem_color == self.jewels[row][col + 1].get_color():
                        return True
            else:
                if cur_jem_color == self.jewels[row][col + 1].get_color() and cur_jem_color == self.jewels[row][col + 2].get_color():
                    return True
        except IndexError:
            #do nothing here right now, this happens when you try to check jewels that have not been created yet
            temp = 0

    def check_3_in_a_row_vertical(self, row, col):
            #check the previous two if it is possible
            cur_jem_color = self.jewels[row][col].get_color()
            try:
                if row - 2 >= 0:
                    if cur_jem_color == self.jewels[row - 2][col].get_color() and cur_jem_color == self.jewels[row - 1][col].get_color():
                            return True
                #check the previous and next if it is possible
                elif row - 1 >= 0:
                    if cur_jem_color == self.jewels[row - 1][col].get_color() and cur_jem_color == self.jewels[row + 1][col].get_color():
                            return True
                else:
                    if cur_jem_color == self.jewels[row + 1][col].get_color() and cur_jem_color == self.jewels[row + 2][col].get_color():
                        return True
            except IndexError:
                # do nothing here right now, this happens when you try to check jewels that have not been created yet
                temp = 0

    def draw_time_bar(self):
        pixels_per_second = self.width_of_board / 60
        # we need to erase the original white bar before we can redraw it
        black_bar = pygame.Rect(self.board_start_x, self.board_start_y - 30, self.width_of_board, 15)
        time_bar = pygame.Rect(self.board_start_x, self.board_start_y - 30, pixels_per_second * self.seconds_left, 15)
        pygame.draw.rect(self.screen, (0, 0, 0), black_bar)
        pygame.draw.rect(self.screen, (255, 255, 255), time_bar)

    def is_valid_switch_box(self, row, col):
        # check right
        if col == self.pos_selected_box[1] + 1 and row == self.pos_selected_box[0]:
            return True
        # check left
        if col == self.pos_selected_box[1] - 1 and row == self.pos_selected_box[0]:
            return True
        # check up
        if col == self.pos_selected_box[1] and row == self.pos_selected_box[0] - 1:
            return True
        # check down
        if col == self.pos_selected_box[1] and row == self.pos_selected_box[0] + 1:
            return True

        return False

    def switch_blocks(self):
        (x, y) = self.pos_selected_box
        (x2, y2) = self.pos_switch_box
        #In case these need to be switched back, we should also swap the coordinate for each variable.
        temp_pos = self.pos_selected_box
        self.pos_selected_box = self.pos_switch_box
        self.pos_switch_box = temp_pos

        # save the selected box as a temp object
        temp = self.jewels[x][y]
        self.jewels[x][y] = self.jewels[x2][y2]
        self.jewels[x2][y2] = temp

    def clear_adjacent_blocks(self):
        cleared_blocks = False
        # check horizontal
        # write down the start pos when we have 2 blocks that are the same next to each other
        # write down the end pos when we have a group of blocks that are the same
        for cur_row in range(self.rows):
            for cur_col in range(self.cols):
                #check all horizontals
                same_block_co = self.count_same_color_blocks_h(cur_row, cur_col)
                if same_block_co >= 3:
                    self.clear_blocks_in_range_h(cur_row, cur_col, cur_col + same_block_co)
                    cleared_blocks = True
                    self.score += (same_block_co * self.points_per_block)
                    pygame.mixer.Sound.play(self.points_sound)
                    pygame.mixer.music.stop()
                #forever 2 blocks cleared add 1 second to the time
                self.seconds_left += int(same_block_co / self.num_blocks_to_add_second)
                #check all verticals
                same_block_co = self.count_same_color_blocks_v(cur_row, cur_col)
                if same_block_co >= 3:
                    self.clear_blocks_in_range_v(cur_col, cur_row, cur_row + same_block_co)
                    cleared_blocks = True
                    self.score += (same_block_co * self.points_per_block)
                    pygame.mixer.Sound.play(self.points_sound)
                    pygame.mixer.music.stop()
                self.seconds_left += int(same_block_co / self.num_blocks_to_add_second)
                #we should limit the timer to 60 seconds
                if self.seconds_left > 60:
                    self.seconds_left = 60
                self.bomb_counter = int(self.score / self.points_per_bomb)
        if cleared_blocks:
            self.draw()
            pygame.time.wait(400)
            self.fill_cleared_blocks()
        return cleared_blocks

    def count_same_color_blocks_h(self, row, col):
        # because one block is always the same color as itself
        same_block_co = 1
        target_color = self.jewels[row][col].get_color()
        # if we pass in a block that has already been cleared, skip it
        if target_color == (0,0,0):
            return 0
        # move over to the next box
        col += 1
        while col < self.cols and target_color == self.jewels[row][col].get_color():
            same_block_co += 1
            col += 1
        return same_block_co

    def clear_blocks_in_range_h(self, row, start_col, end_col):
        # horizontally clear all blocks UP TO BUT NOT INCLUDING the end col
        for i in range(start_col, end_col):
            self.jewels[row][i].clear()

    def count_same_color_blocks_v(self, row, col):
        # because one block is always the same color as itself
        same_block_co = 1
        target_color = self.jewels[row][col].get_color()
        # if we pass in a block that has already been cleared, skip it
        if target_color == (0, 0, 0):
            return 0
        # move over to the next box
        row += 1
        while row < self.rows and target_color == self.jewels[row][col].get_color():
            same_block_co += 1
            row += 1
        return same_block_co

    def clear_blocks_in_range_v(self, col, start_row, end_row):
        # horizontally clear all blocks UP TO BUT NOT INCLUDING the end col
        for i in range(start_row, end_row):
            self.jewels[i][col].clear()

    def fill_cleared_blocks(self):
        # find how many blocks each row needs
        self.blocks_needed_each_col = []
        # go through each row and count how many blocks need to be filled
        for c in range(self.cols):
            cleared_blocks = 0
            for r in range(self.rows):
                if self.jewels[r][c].is_cleared:
                    cleared_blocks += 1
            self.blocks_needed_each_col.append(cleared_blocks)
        # while there are still blocks that need to be filled
        pygame.time.set_timer(pygame.USEREVENT, 250)
        while sum(self.blocks_needed_each_col) != 0:
            for c in range(self.cols):
                #if this column needs a block
                if self.blocks_needed_each_col[c] > 0:
                    #block down one block in that row
                    self.move_down_blocks_in_row(c)
                    self.blocks_needed_each_col[c] -= 1
            self.draw()

            pygame.time.wait(250)

        self.clear_adjacent_blocks()

    def move_down_blocks_in_row(self, col):
        #start at the bottom and move the blocks down one when you find a clear
        for r in range(self.rows-1,-1,-1):
            if self.jewels[r][col].is_cleared:
                self.move_down_blocks_above(r, col)
                return


    def move_down_blocks_above(self, row, col):
        for i in range(row, -1, -1): #
            # in range goes up to but not including the stop value so we actually want to stop at -1
            #if we are on the top row when moving items down the item we're on should get cleared
            if i == 0:
                if self.num_bombs < self.bomb_counter:
                    self.jewels[i][col] = Bomb(self.block_size)
                    self.num_bombs += 1
                else:
                    self.jewels[i][col] = Jewel(self.get_random_color(), self.block_size)
            else:
                self.jewels[i][col] = self.jewels[i-1][col].copy()

    def bomb_explosion(self, row, col):
        self.score += 50
        pygame.mixer.Sound.play(self.explosion_sound)
        #pygame.mixer.music.stop()
        #blow up 2 blocks in all directions
        #clear the two blocks above the bomb
        for r in range(row, row - 3, -1):
            #minus 3 because it goes up to but not including the stop value
            if r >= 0:
                self.jewels[r][col].clear()
        #clear blocks below
        for r in range(row, row + 3, 1):
            # minus 3 because it goes up to but not including the stop value
            if r < self.rows:
                self.jewels[r][col].clear()
        # clear the bomb
        self.jewels[row][col].clear()

        # clear blocks to the left
        for c in range(col, col - 3, -1):  # minus 3 because it goes up to but
            # not including the stop value
            if c >= 0:
                self.jewels[row][c].clear()
        # clear blocks to the right
        for c in range(col, col + 3, 1):  # minus 3 because it goes up to but
            # not including the stop value
            if c < self.cols:
                self.jewels[row][c].clear()
        self.draw()
        pygame.time.wait(750)

    def update_time(self):
        # time.time() gives us the time right now in seconds
        if time.time() - self.last_second > 1:
            self.last_second = time.time()
            self.seconds_left -= 1
            self.draw_time_bar()
            # check for a game over
            if self.seconds_left == 0:
                print("Game Over")
                self.is_game_over = True
                self.screen.fill((0, 0, 0))
                lbl_score = self.score_font.render("Score: " + str(self.score), 1, (255, 255, 255))
                lbl_game_over = self.score_font.render("Game Over", 1, (255, 255, 255))
                self.screen.blit(lbl_score, (30, 30))
                self.screen.blit(lbl_game_over, (30, 60))
                self.check_high_score()
                self.show_retry()
                self.draw()

    def show_retry(self):
        self.retry = pygame.font.SysFont("Comic Sans MS", 40)
        lbl_retry = self.score_font.render("RETRY", 1, (255, 255, 255))
        button_width = 125
        button_height = 50
        x = (self.width/2) - (button_width /2)
        y = (self.height/2) - (button_height/2)
        self.retry = pygame.Rect(x, y,  button_width,button_height)
        pygame.draw.rect(self.screen, (255,255,255), self.retry,5)
        self.screen.blit(lbl_retry, (x + (button_width/4), y + 10))
        pygame.display.flip()

    def check_high_score(self):
        #this happens when the game is over
        has_inserted_score = False
        for i in range(len(self.scores)):
            if self.score > int(self.scores[i][1]):
                print("Congrats you have a new high score!!")
                new_name = input("Enter your name: ")
                # if we have 3 insert in front of the index we're on
                self.scores.insert(i, (new_name, self.score))
                has_inserted_score = True
                # if we added an extra score we should get rid of it
                if len(self.scores) == 4:
                    # if we added an extra one get rid of the last element in the list
                    self.scores.pop()
                break

        if len(self.scores) < 3 and not has_inserted_score:
            # only do this if you have not inserted the score yet
            print("Congrats you have a new high score!!")
            new_name = input("Enter your name: ")
            self.scores.append((new_name, self.score))

        # write the new score to file
        score_file = open("scores.txt", "w")
        for s in self.scores:
            score_file.write(s[0] + "," + str(s[1]) + "\n")
        score_file.close()