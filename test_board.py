import unittest
import pygame
from board import Board
import random


class TestBoard(unittest.TestCase):

    def setUp(self):
        pygame.init()
        size = width, height = 800, 600

        screen = pygame.display.set_mode(size)

        size_of_block = 50
        column_padding = 10
        num_rows = 7
        num_cols = 7
        self.board_test = Board(screen, num_rows, num_cols, size_of_block, column_padding, width, height)



    def test_get_random_color(self):
        pygame.init()
        size = width, height = 800, 600

        screen = pygame.display.set_mode(size)

        size_of_block = 50
        column_padding = 10
        num_rows = 7
        num_cols = 7
        board_test = Board(screen, num_rows, num_cols, size_of_block, column_padding, width, height)


        random.seed(1)
        self.assertEqual(board_test.get_random_color(), (0,255,0))

        random.seed(2)
        self.assertEqual(board_test.get_random_color(), (255, 0, 0))



if __name__ == '__main__':
    unittest.main()
