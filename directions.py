# turns the direction vectors into constants
from pygame.math import Vector2


class Directions:
    RIGHT = Vector2(1, 0)
    LEFT = Vector2(-1, 0)
    UP = Vector2(0, -1)
    DOWN = Vector2(0, 1)
