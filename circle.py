import pygame

class Circle:
    def __init__(self, x, y, radius, colour=(255, 255, 255)):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour

    def draw(self, surface):
        pygame.draw.circle(surface, self.colour, (self.x, self.y), self.radius)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def collidepoint(self, point):
        # Check if a point (x, y) is inside the circle
        px, py = point
        distance = ((px - self.x) ** 2 + (py - self.y) ** 2) ** 0.5
        return distance <= self.radius