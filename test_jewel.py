import unittest
from jewel import Jewel


class TestJewel(unittest.TestCase):

    def setUp(self):
        self.jewel = Jewel((255,0,0), 50)

    def test_get_color(self):
        test_jewel1 = Jewel((255,0,0), 50)
        test_jewel2 = Jewel((0,255,0), 50)
        self.assertEqual(test_jewel1.get_color(), (255,0,0))
        self.assertEqual(test_jewel2.get_color(), (0,255,0))





if __name__ == '__main__':
    unittest.main()