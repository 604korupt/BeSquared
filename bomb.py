import pygame

class Bomb:

    def __init__(self, bomb_size):
        self.bomb_size = bomb_size
        self.bomb_img = pygame.image.load("bomb.png")
        self.bomb_img = pygame.transform.scale(self.bomb_img, (bomb_size, bomb_size))
        self.block = self.bomb_img.get_rect()
        self.is_cleared = False
        self.x = 0
        self.y = 0


    def draw(self, screen, x, y):
        if not self.is_cleared:
            self.block.x = x
            self.block.y = y
            screen.blit(self.bomb_img, self.block)

    def check_collision(self, mouse_position):
        return self.block.collidepoint(mouse_position)


    def get_color(self):
        return (0,0,0) # return black which should never match with any blocks

    def clear(self):
        self.is_cleared = True

    def copy(self):
        new_bomb = Bomb(self.bomb_size)
        if self.is_cleared:
            new_bomb.clear()
        return new_bomb
