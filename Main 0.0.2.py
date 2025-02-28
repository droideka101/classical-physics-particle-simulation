import pygame
import math
import sys
from circle import Circle

pygame.init()
SIZE = (1366, 768)
screen = pygame.display.set_mode(SIZE)
display = pygame.Surface(SIZE, pygame.SRCALPHA)

FPS = 60
clock = pygame.time.Clock()

# PARTICLE MASSES
m_electron = 1
m_proton = 1836.15
m_neutron = 1838.68

# PARTICLE CHARGES
q_proton = 10
q_electron = -10
q_neutron = 0

# PARTICLE RADII (arbitrary)
r_proton = 10
r_neutron = 10
r_electron = 6

# FORCE CONSTANTS
GravitationalConstant = 0.01
CoulombsConstant = 500

# PARTICLE COLOURS
c_proton = (220, 71, 73)
c_neutron = (254, 202, 116)
c_electron = (106, 198, 220)

fm_to_pixels = 10 # Scale factor for strong force range

epsilon = 1e-15  # Small value to avoid division by zero, reflecting nuclear scales

max_particles = 200
particles = []

# Variables to track mouse drag
dragging = False
start_pos = None
current_pos = None
line_color = (255, 255, 255)  # Default line color

class Particle:
    def __init__(self, startX, startY, radius, colour, mass, charge):
        self.objectCircle = Circle(startX, startY, radius, colour)
        self.mass = mass
        self.charge = charge
        self.velocity_x = 0
        self.velocity_y = 0

    def collideWithEdge(self):
        if self.objectCircle.x >= SIZE[0] + 10:
            self.objectCircle.x = 0
        if self.objectCircle.x <= - 10:
            self.objectCircle.x = SIZE[0]
        if self.objectCircle.y >= SIZE[1] + 10:
            self.objectCircle.y = 0
        if self.objectCircle.y <= -10:
            self.objectCircle.y = SIZE[1]

    def move(self):
        self.collideWithEdge()

        self.objectCircle.x += self.velocity_x
        self.objectCircle.y += self.velocity_y

    def get_position(self):
        return (self.objectCircle.x, self.objectCircle.y)

    def draw(self, surface):
        self.objectCircle.draw(surface)

class Proton(Particle):
    def __init__(self, startX, startY, radius, colour, mass, charge):
        super().__init__(startX, startY, radius, colour, mass, charge)

class Electron(Particle):
    def __init__(self, startX, startY, radius, colour, mass, charge):
        super().__init__(startX, startY, radius, colour, mass, charge)

class Neutron(Particle):
    def __init__(self, startX, startY, radius, colour, mass, charge):
        super().__init__(startX, startY, radius, colour, mass, charge)

def get_distance(p1, p2):
    # Get positions
    x1, y1 = p1.get_position()
    x2, y2 = p2.get_position()
    # Calculate distance and direction
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx ** 2 + dy ** 2) + epsilon  # Avoid division by zero
    return distance, dx, dy

def apply_force(p1, p2, force, distance, dx, dy):
    # Calculate force components
    force_x = force * (dx / distance)
    force_y = force * (dy / distance)
    # Apply force to particles
    p1.velocity_x += (force_x / p1.mass) * dt
    p1.velocity_y += (force_y / p1.mass) * dt
    p2.velocity_x -= (force_x / p2.mass) * dt
    p2.velocity_y -= (force_y / p2.mass) * dt

def calculate_electromagnetic_force(p1, p2):
    # Get distance between particles
    distance, dx, dy = get_distance(p1, p2)
    # Calculate force
    force = -(CoulombsConstant * (p1.charge * p2.charge) / (distance ** 2))
    # Apply force to particles
    apply_force(p1, p2, force, distance, dx, dy)

def calculate_gravitational_force(p1, p2):
    # Get distance between particles
    distance, dx, dy = get_distance(p1, p2)
    # Calculate force
    force = (GravitationalConstant * (p1.mass * p2.mass) / (distance ** 2))
    # Apply force to particles
    apply_force(p1, p2, force, distance, dx, dy)

def calculate_strong_force(p1, p2):
    if isinstance(p1, (Proton, Neutron)) and isinstance(p2, (Proton, Neutron)):
        distance, dx, dy = get_distance(p1, p2)
        r_fm = distance / fm_to_pixels  # Convert pixels to fm
        if r_fm < 2.5:  # Strong force range
            attract = (6 * 10**4) * math.exp(-7 * (0.4*r_fm - 0.3))
            repuls = - (8.5 * 10**4) * math.exp(-3.6 * (0.4*r_fm - 0.3))
            force = -(attract + repuls)
            apply_force(p1, p2, force, distance, dx, dy)

def spawn_particle_with_velocity(start_pos, end_pos, button):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    velocity_x = dx * -0.1  # Adjust the scaling factor as needed
    velocity_y = dy * -0.1  # Adjust the scaling factor as needed

    if button == 1:
        particle = Proton(start_pos[0], start_pos[1], r_proton, c_proton, m_proton, q_proton)
    elif button == 2:
        particle = Electron(start_pos[0], start_pos[1], r_electron, c_electron, m_electron, q_electron)
    elif button == 3:
        particle = Neutron(start_pos[0], start_pos[1], r_neutron, c_neutron, m_neutron, q_neutron)

    particle.velocity_x = velocity_x
    particle.velocity_y = velocity_y
    particles.append(particle)
    print(f"Added particle at ({start_pos[0]}, {start_pos[1]}) with velocity ({velocity_x}, {velocity_y})")

paused = False

while True:
    dt = clock.tick(FPS) / 1000

    keyHeld = pygame.key.get_pressed()

    display.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or keyHeld[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            start_pos = (mouse_x, mouse_y)
            dragging = True

            if len(particles) >= max_particles:
                particles.pop(0)

            # Set the line color based on the particle type
            if event.button == 1:
                line_color = c_proton
            elif event.button == 2:
                line_color = c_electron
            elif event.button == 3:
                line_color = c_neutron

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if dragging and start_pos:
                end_pos = (mouse_x, mouse_y)
                spawn_particle_with_velocity(start_pos, end_pos, event.button)
            dragging = False
            start_pos = None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                particles = []
                print("Cleared all particles")
            if event.key == pygame.K_BACKSPACE and len(particles) != 0:
                print(f"removed particle {particles[-1].__class__.__name__}")
                particles.pop()
            if event.key == pygame.K_p:
                paused = not paused
                print("Paused" if paused else "Unpaused")

    if dragging and start_pos:
        current_pos = pygame.mouse.get_pos()
        pygame.draw.line(display, line_color, start_pos, current_pos, 2)  # Draw the trajectory line

    if not paused:            

        for i in range(len(particles)):
            for j in range(i + 1, len(particles)):
                p1 = particles[i]
                p2 = particles[j]

                calculate_electromagnetic_force(p1, p2)
                calculate_gravitational_force(p1, p2)
                calculate_strong_force(p1, p2)

        for particle in particles:
            particle.move()

    for particle in particles:    
        particle.draw(display)

    # Render to the screen
    screen.blit(display, (0, 0))
    pygame.display.update()