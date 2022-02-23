import unittest
from bomb import Bomb

class TestBomb(unittest.TestCase):

    def setUp(self):
        self.test_bomb = Bomb(50)

    def test_get_color(self):
        test_bomb = Bomb(50)
        self.assertEqual(test_bomb.get_color(), (0,0,0))
        self.assertEqual(test_bomb.get_color(), (0, 0, 0))


if __name__ == '__main__':
    unittest.main()


