import random

import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

# Game modes
MODE_SELECT = True
RANDOM_MODE = False

vertices = [
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
]

faces = [
    [0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
    [2, 3, 7, 6], [1, 2, 6, 5], [0, 3, 7, 4]
]

def load_texture(filename):
    surf = pygame.image.load(filename)
    image = pygame.image.tostring(surf, "RGBA", True)
    width, height = surf.get_rect().size
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0) # Unbind texture
    return tex_id

class Cube:
    def __init__(self, pos, textures):
        self.pos = np.array(pos, dtype=np.float32)
        self.current_rotation = 0.0
        self.target_rotation = 0.0
        self.rotation_speed = 180.0
        self.textures = textures
        self.owner = None
        self.rotating = False

    def update(self, dt):
        if self.current_rotation != self.target_rotation:
            self.rotating = True
            diff = self.target_rotation - self.current_rotation
            step = self.rotation_speed * dt
            if abs(diff) <= step:
                self.current_rotation = self.target_rotation
            else:
                self.current_rotation += step if diff > 0 else -step
        else:
            self.rotating = False

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.current_rotation, 0, 1, 0)
        self.draw_faces()
        glPopMatrix()

    def draw_faces(self):
        glEnable(GL_TEXTURE_2D)
        for i, face in enumerate(faces):
            tex_id = self.textures.get(i, self.textures['default'])
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glBegin(GL_QUADS)
            uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
            for uv, v in zip(uvs, face):
                glTexCoord2f(*uv)
                glVertex3fv(vertices[v])
            glEnd()
        glBindTexture(GL_TEXTURE_2D, 0) # Unbind texture

    def is_point_inside(self, ray_origin, ray_direction):
        min_bound = self.pos - 1
        max_bound = self.pos + 1
        tmin = (min_bound - ray_origin) / ray_direction
        tmax = (max_bound - ray_origin) / ray_direction
        t1 = np.minimum(tmin, tmax)
        t2 = np.maximum(tmin, tmax)
        t_near = np.max(t1)
        t_far = np.min(t2)
        return t_far >= 0 and t_near <= t_far

    def click(self, turn):
        if self.owner is not None:
            return False
        self.owner = random.choice(['X', 'O']) if RANDOM_MODE else turn
        self.target_rotation = (self.target_rotation - (90 if self.owner == 'X' else 180)) % 360
        return True

def init_gl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_TEXTURE_2D)


def get_ray(mx, my, w, h, modelview, proj):
    near = gluUnProject(mx, h - my, 0.0, modelview, proj, [0, 0, w, h])
    far = gluUnProject(mx, h - my, 1.0, modelview, proj, [0, 0, w, h])
    ray_origin = np.array(near)
    ray_dir = np.array(far) - ray_origin
    return ray_origin, ray_dir / np.linalg.norm(ray_dir)


def check_winner(cubes):
    grid = [cube.owner for cube in cubes]
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for a, b, c in lines:
        if grid[a] and grid[a] == grid[b] == grid[c]:
            return grid[a]
    return None

def is_draw(cubes):
    return all(cube.owner is not None for cube in cubes)


def draw_text_gl(x, y, text_string, font, color=(255, 0, 0, 255)):
    """Renders text to an OpenGL texture and draws it on a quad."""
    text_surface = font.render(text_string, True, color) # Pygame surface
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    width, height = text_surface.get_size()

    # Create OpenGL texture
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Draw the quad
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y + height)
    glTexCoord2f(1, 0); glVertex2f(x + width, y + height)
    glTexCoord2f(1, 1); glVertex2f(x + width, y)
    glTexCoord2f(0, 1); glVertex2f(x, y)
    glEnd()

    glDisable(GL_BLEND)
    glDeleteTextures(1, [tex_id])
    glBindTexture(GL_TEXTURE_2D, 0)


def draw_ui(font, mode_select, winner, turn, game_over, screen_width, screen_height):
    # Switch to 2D orthographic projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, screen_width, screen_height, 0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)

    if mode_select:
        options = ["Press R for Random Mode", "Press T for Turn-based"]
    elif winner:
        options = [f"{winner} wins! Press Space to restart."]
    elif game_over and not winner: # Check for draw
        options = ["It's a Draw! Press Space to restart."]
    elif RANDOM_MODE:
        options = ["X/O's turn. (random mode)"]
    else:
        options = [f"{turn}'s Turn"]

    y_pos = 20
    for i, line in enumerate(options):
        draw_text_gl(20, y_pos + i * 40, line, font)

    # Restore previous projection and modelview matrices
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


def main():
    global RANDOM_MODE, MODE_SELECT
    pygame.init()
    width, height = 800, 600
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Tic Tac Toe")
    font = pygame.font.SysFont("Arial", 30)
    init_gl()

    # Initial camera setup
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -20) # Move camera back

    tex_default = load_texture("crate.png")
    tex_x = load_texture("crate_x.png")
    tex_o = load_texture("crate_o.png")

    spacing = 2.5
    def make_cubes():
        cubes = []
        # Center the grid of cubes slightly
        offset_x = - (3 - 1) * spacing / 2
        offset_y = (3 - 1) * spacing / 2
        for r in range(3):
            for c in range(3):
                pos = [offset_x + c * spacing, offset_y - r * spacing, 0]
                tex = {'default': tex_default, 0: tex_o, 4: tex_x}
                cubes.append(Cube(pos, tex))
        return cubes

    cubes = make_cubes()
    clock = pygame.time.Clock()
    turn = 'X'
    winner = None
    game_over = False

    while True:
        dt = clock.tick(60) / 1000.0
                
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            elif event.type == KEYDOWN:
                if MODE_SELECT:
                    if event.key == K_r:
                        RANDOM_MODE, MODE_SELECT = True, False
                    elif event.key == K_t:
                        RANDOM_MODE, MODE_SELECT = False, False
                elif event.key == K_SPACE and (winner or is_draw(cubes) or game_over):
                    cubes = make_cubes()
                    winner, turn, game_over, MODE_SELECT = None, 'X', False, True

            elif event.type == MOUSEBUTTONDOWN and not (game_over or MODE_SELECT or any(c.rotating for c in cubes)):
                modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
                projection = glGetDoublev(GL_PROJECTION_MATRIX)
                mx, my = pygame.mouse.get_pos()
                ray_origin, ray_dir = get_ray(mx, my, width, height, modelview, projection)
                for cube in cubes:
                    if cube.is_point_inside(ray_origin, ray_dir):
                        changed = cube.click(turn)
                        if changed and not RANDOM_MODE:
                            turn = 'O' if turn == 'X' else 'X'
                        break

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # --- 3D Scene Rendering ---
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        # Set up camera view for 3D scene
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -15)

        rotating_cubes_exist = False
        for cube in cubes:
            cube.update(dt)
            cube.draw()
            if cube.rotating:
                rotating_cubes_exist = True

        if not game_over and not rotating_cubes_exist and not MODE_SELECT:
            winner = check_winner(cubes)
            if winner:
                game_over = True
            elif is_draw(cubes):
                game_over = True

        # --- UI Rendering ---
        draw_ui(font, MODE_SELECT, winner, turn, game_over, width, height)

        pygame.display.flip()

if __name__ == "__main__":
    main()
    pygame.quit()
