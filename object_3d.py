import pygame as pg
from matrix_functions import *
from numba import njit


@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

def get_gradient_color(y, min_y, max_y, color_top, color_bottom):
    ratio = (y - min_y) / (max_y - min_y + 1e-5)
    r = color_bottom.r + (color_top.r - color_bottom.r) * ratio
    g = color_bottom.g + (color_top.g - color_bottom.g) * ratio
    b = color_bottom.b + (color_top.b - color_bottom.b) * ratio
    return pg.Color(int(r), int(g), int(b))

class Object3D:
    def __init__(self, render, vertices='', faces=''):
        self.render = render
        self.vertices = np.array(vertices)
        self.faces = faces

        self.ground_level = 0

        self.translate([0.0001, 0.0001, 0.0001])

        self.font = pg.font.SysFont('Arial', 30, bold=True)
        self.color_faces = [(pg.Color('orange'), face) for face in self.faces]
        self.movement_flag, self.draw_vertices = True, False
        self.label = ''

        self.velocity = 0.0
        self.on_ground = False
        self.jump_strength = 7.5
        self.acceleration = -9.8
        self.t = 0.0
        self.restitution = 0.7 
        self.controllable = False
        self.move_speed = 0.5

        self.velocity_vector = np.array([0.0, 0.0, 0.0])
        self.acceleration_value = 1.0
        self.drag = 0.95
        self.radius = 1.0
        self.rotation_speed = 1
        self.launch_direction = np.array([0.0, 0.0, 0.0])
        self.launch_power = 5.0

    def update_gravity(self, dt):
        self.t += dt
        dy = self.velocity * dt + 0.5 * self.acceleration * dt ** 2
        self.velocity += self.acceleration * dt
        self.translate([0, dy, 0])

        bottom_y = self.vertices[:, 1].min()
        if bottom_y <= self.ground_level:
            offset = self.ground_level - bottom_y
            self.translate([0, offset, 0])
            self.velocity = -self.velocity * self.restitution

            if abs(self.velocity) < 0.1:
                self.velocity = 0
                self.acceleration = 0
                self.t = 0
                self.on_ground = True  
            else:
                self.on_ground = False
        else:
            self.on_ground = False

    def draw(self):
        self.screen_projection()
        self.movement()

    def movement(self):
        if self.controllable:
            self.control()
            self.handle_wall_collision(bounds=(-40, 40), restitution=self.restitution)
        if self.movement_flag and self.gravity_enabled:
            dt = 1 / self.render.FPS
            self.update_gravity(dt)
        
    def screen_projection(self):
        vertices = self.vertices @ self.render.camera.camera_matrix()
        vertices = vertices @ self.render.projection.projection_matrix
        vertices /= vertices[:, -1].reshape(-1, 1)
        vertices[(vertices > 2) | (vertices < -2)] = 0
        vertices = vertices @ self.render.projection.to_screen_matrix
        vertices = vertices[:, :2]

        for index, color_face in enumerate(self.color_faces):
            color, face = color_face
            try:
                polygon = np.array([vertices[i] for i in face])
            except IndexError:
                continue 

            if not any_func(polygon, self.render.H_WIDTH, self.render.H_HEIGHT):
                pg.draw.polygon(self.render.screen, color, polygon, 0)
                if self.label:
                    text = self.font.render(self.label[index], True, pg.Color('white'))
                    self.render.screen.blit(text, polygon[-1])

        if self.draw_vertices:
            for vertex in vertices:
                if not any_func(vertex, self.render.H_WIDTH, self.render.H_HEIGHT):
                    pg.draw.circle(self.render.screen, pg.Color('white'), vertex, 2)

    def translate(self, pos):
        self.vertices = self.vertices @ translate(pos)

    def scale(self, scale_to):
        self.vertices = self.vertices @ scale(scale_to)

    def rotate_x(self, angle):
        self.vertices = self.vertices @ rotate_x(angle)

    def rotate_y(self, angle):
        self.vertices = self.vertices @ rotate_y(angle)

    def rotate_z(self, angle):
        self.vertices = self.vertices @ rotate_z(angle)

    def control(self):
        if not self.controllable:
            return

        key = pg.key.get_pressed()
        forward = self.render.camera.forward[:3]
        right = self.render.camera.right[:3]

        # Proyeksi ke XZ (abaikan Y)
        forward[1] = 0
        right[1] = 0

        if np.linalg.norm(forward) != 0:
            forward = forward / np.linalg.norm(forward)
        if np.linalg.norm(right) != 0:
            right = right / np.linalg.norm(right)

        acceleration = np.array([0.0, 0.0, 0.0])

        if key[pg.K_i]:
            acceleration += forward * self.acceleration_value
        if key[pg.K_k]:
            acceleration -= forward * self.acceleration_value
        if key[pg.K_j]:
            acceleration -= right * self.acceleration_value
        if key[pg.K_l]:
            acceleration += right * self.acceleration_value

        if key[pg.K_i]:
            self.launch_direction += self.get_forward_vector() * 0.01
        if key[pg.K_k]:
            self.launch_direction -= self.get_forward_vector() * 0.01
        if key[pg.K_j]:
            self.launch_direction -= self.get_right_vector() * 0.01
        if key[pg.K_l]:
            self.launch_direction += self.get_right_vector() * 0.01

        if key[pg.K_SPACE]:
            self.velocity = self.jump_strength
            self.acceleration = -9.8
            self.t = 0
            self.on_ground = False

        if key[pg.K_c]:
            self.jump_strength += 0.01
        if key[pg.K_v]:
            self.jump_strength -= 0.01

        if key[pg.K_z]:
            self.move_speed += 0.01
        if key[pg.K_x]:
            self.move_speed -= 0.01

        if key[pg.K_b]:
            self.restitution += 0.01
        if key[pg.K_n]:
            self.restitution -= 0.01

        if key[pg.K_r]:
            self.reset_position()

        if key[pg.K_m]:
            self.launch()

        if key[pg.K_LEFTBRACKET]:
            self.scale(0.99)
            self.radius *= 0.99

        if key[pg.K_RIGHTBRACKET]:
            self.scale(1.01)
            self.radius *= 1.01

        if key[pg.K_LSHIFT]:
            if np.linalg.norm(self.launch_direction) > 0:
                direction = self.launch_direction / np.linalg.norm(self.launch_direction)
                self.velocity_vector += direction * self.launch_power
                self.velocity = self.jump_strength
                self.acceleration = -9.8
                self.t = 0
                self.on_ground = False
                self.launch_direction[:] = 0

        dt = 1 / self.render.FPS

        self.velocity_vector += acceleration * dt * self.move_speed

        self.velocity_vector *= self.drag

        if np.linalg.norm(self.velocity_vector) < 0.001:
            self.velocity_vector = np.array([0.0, 0.0, 0.0])

        self.translate(self.velocity_vector)

        distance = np.linalg.norm(self.velocity_vector)
        if distance > 0:
            direction = self.velocity_vector / distance
            up = np.array([0, 1, 0])
            axis = np.cross(direction, up)
            angle = distance / self.radius
            rot_matrix = self.rotation_matrix(axis, angle)
            self.rotate_around_center(rot_matrix)
        
    def reset_position(self):
        center_x, center_z = 0.0, 0.0
        min_y = self.vertices[:, 1].min()
        offset_x = center_x - self.vertices[:, 0].mean()
        offset_y = 0 - min_y
        offset_z = center_z - self.vertices[:, 2].mean()
        self.translate([offset_x, offset_y, offset_z])

        self.velocity = 0.0
        self.velocity_vector = np.array([0.0, 0.0, 0.0])
        self.acceleration = -9.8
        self.t = 0.0
        self.on_ground = False

    def rotate_around_center(self, rot_matrix):
        center = self.vertices.mean(axis=0)
        self.vertices = self.vertices @ translate(-center[:3])
        self.vertices = self.vertices @ rot_matrix
        self.vertices = self.vertices @ translate(center[:3])

    def rotation_matrix(self, axis, angle):
        x, y, z = axis / np.linalg.norm(axis)
        c, s = np.cos(angle), np.sin(angle)
        t = 1 - c
        return np.array([
            [t*x*x + c,   t*x*y - s*z, t*x*z + s*y, 0],
            [t*x*y + s*z, t*y*y + c,   t*y*z - s*x, 0],
            [t*x*z - s*y, t*y*z + s*x, t*z*z + c,   0],
            [0,           0,           0,           1]
        ])

    def handle_wall_collision(self, bounds=(-40, 40), restitution=0.8):
        min_x = self.vertices[:, 0].min()
        max_x = self.vertices[:, 0].max()
        min_z = self.vertices[:, 2].min()
        max_z = self.vertices[:, 2].max()

        left, right = bounds
        front, back = bounds

        if min_x < left and self.velocity_vector[0] < 0:
            offset = left - min_x
            self.translate([offset, 0, 0])
            self.velocity_vector[0] *= -restitution
        elif max_x > right and self.velocity_vector[0] > 0:
            offset = right - max_x
            self.translate([offset, 0, 0])
            self.velocity_vector[0] *= -restitution

        if min_z < front and self.velocity_vector[2] < 0:
            offset = front - min_z
            self.translate([0, 0, offset])
            self.velocity_vector[2] *= -restitution
        elif max_z > back and self.velocity_vector[2] > 0:
            offset = back - max_z
            self.translate([0, 0, offset])
            self.velocity_vector[2] *= -restitution

    def get_forward_vector(self):
        vec = self.render.camera.forward[:3]
        vec[1] = 0
        if np.linalg.norm(vec) != 0:
            vec /= np.linalg.norm(vec)
        return vec

    def get_right_vector(self):
        vec = self.render.camera.right[:3]
        vec[1] = 0
        if np.linalg.norm(vec) != 0:
            vec /= np.linalg.norm(vec)
        return vec

class Axes(Object3D):
    def __init__(self, render):
        super().__init__(render)
        self.vertices = np.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
        self.faces = np.array([(0, 1), (0, 2), (0, 3)])
        self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]
        self.color_faces = [(color, face) for color, face in zip(self.colors, self.faces)]
        self.draw_vertices = False
        self.label = 'XYZ'

class Floor(Object3D):
    def __init__(self, render, y=-10, size=80, tile_count=10):
        self.render = render
        self.y = y
        self.size = size
        self.tile_count = tile_count

        vertices = []
        faces = []
        color_faces = []

        tile_size = size / tile_count
        half = size / 2

        for i in range(tile_count):
            for j in range(tile_count):
                x0 = -half + i * tile_size
                z0 = -half + j * tile_size
                x1 = x0 + tile_size
                z1 = z0 + tile_size

                idx = len(vertices)
                vertices.extend([
                    [x0, y, z0, 1],
                    [x1, y, z0, 1],
                    [x1, y, z1, 1],
                    [x0, y, z1, 1],
                ])
                faces.append((idx, idx+1, idx+2, idx+3))

                # Checkerboard pattern
                is_dark = (i + j) % 2 == 0
                color = pg.Color('dimgray') if is_dark else pg.Color('gray')
                color_faces.append((color, faces[-1]))

        super().__init__(render, vertices, faces)
        self.color_faces = color_faces
        self.movement_flag = False
        self.draw_vertices = False
        self.controllable = False
        self.gravity_enabled = False

class Wall(Object3D):
    def __init__(self, render, axis='x', position=0, height=20, depth=80, thickness=1, y_base=-10):
        self.render = render
        h = height
        d = depth
        t = thickness
        y0 = y_base
        y1 = y0 + h

        if axis == 'x':
            x0 = position
            vertices = [
                [x0, y0, -d/2, 1],
                [x0 + t, y0, -d/2, 1],
                [x0 + t, y1, -d/2, 1],
                [x0, y1, -d/2, 1],
                [x0, y0, d/2, 1],
                [x0 + t, y0, d/2, 1],
                [x0 + t, y1, d/2, 1],
                [x0, y1, d/2, 1],
            ]
        else:
            z0 = position
            vertices = [
                [-d/2, y0, z0, 1],
                [ d/2, y0, z0, 1],
                [ d/2, y1, z0, 1],
                [-d/2, y1, z0, 1],
                [-d/2, y0, z0 + t, 1],
                [ d/2, y0, z0 + t, 1],
                [ d/2, y1, z0 + t, 1],
                [-d/2, y1, z0 + t, 1],
            ]

        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (1, 2, 6, 5),
            (0, 3, 7, 4),
        ]

        super().__init__(render, vertices, faces)
        self.color_faces = [(pg.Color('slategray'), face) for face in faces]
        self.movement_flag = False
        self.controllable = False
        self.gravity_enabled = False
