import pygame

class Jewel:

    def __init__(self, color, jewel_size):
        self.color = color
        self.jewel_size = jewel_size
        self.is_selected = False
        self.is_cleared = False
        # we need to initialize the block, but it will get its position set later
        self.block = pygame.Rect(0,0,0,0)
        # self.block = pygame.Rect(x, y, jewelSize,jewelSize)

    # x and y here represent the pixel to draw them on the scree
    def draw(self, screen, x, y):
        if self.is_cleared:
            color = (0,0,0)
        else:
            color = self.color
        self.block = pygame.Rect(x, y, self.jewel_size, self.jewel_size)
        pygame.draw.rect(screen, color, self.block)
        if self.is_selected:
            outline_width = 3
            padding_to_outline = 2
            # use the width of the outline and padding to calculate the outline
            # rectangle width. because we are padding and stroking the outline on
            # both sides we have to add it twice
            outline_dimension = self.jewel_size + ((outline_width + padding_to_outline) * 2)
            # draw white rectangle around the jewel
            pygame.draw.rect(screen, (255,255,255), (x - (outline_width + padding_to_outline), y - (outline_width + padding_to_outline),
                                                     outline_dimension, outline_dimension), outline_width)

    def check_collision(self, mouse_position):
        return self.block.collidepoint(mouse_position)

    def set_selection(self, is_selected):
        self.is_selected = is_selected

    def get_color(self):
        return self.color

    def clear(self):
        self.is_cleared = True

    def copy(self):
        new_jewel = Jewel(self.color, self.jewel_size)
        if self.is_cleared:
            new_jewel.clear()
        return new_jewel