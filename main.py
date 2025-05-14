from object_3d import *
from camera import *
from projection import *
import pygame as pg


class SoftwareRender:
    def __init__(self):
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 1280, 720
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.create_objects()

    def create_objects(self):
        self.camera = Camera(self, [0, 5, -50])
        self.projection = Projection(self)
        self.object = self.get_object_from_file('resources/sphere.obj')
        self.floor = Floor(self, y=0, size=80, tile_count=20)
        s = 80  
        h = 30 
        t = 1
        y = 0

        self.walls = [
            Wall(self, axis='x', position= -s/2, height=h, depth=s, thickness=t, y_base=y),
            Wall(self, axis='x', position= s/2,  height=h, depth=s, thickness=t, y_base=y),
            Wall(self, axis='z', position= -s/2, height=h, depth=s, thickness=t, y_base=y),
            Wall(self, axis='z', position= s/2,  height=h, depth=s, thickness=t, y_base=y),
        ]
        self.center_object_on_platform(self.object, platform_y=0)  
        self.object.controllable = True
        self.object.gravity_enabled = True
        min_y = self.object.vertices[:, 1].min()
        max_y = self.object.vertices[:, 1].max()
        color_top = pg.Color('orange')
        color_bottom = pg.Color('darkred')

        self.object.color_faces = []
        for face in self.object.faces:
            avg_y = np.mean([self.object.vertices[i][1] for i in face])
            color = get_gradient_color(avg_y, min_y, max_y, color_top, color_bottom)
            self.object.color_faces.append((color, face))
        
    def get_object_from_file(self, filename):
        vertex, faces = [], []
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertex.append([float(i) for i in line.split()[1:]] + [1])
                elif line.startswith('f'):
                    faces_ = line.split()[1:]
                    faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
        return Object3D(self, vertex, faces)

    def center_object_on_platform(self, obj, platform_y=0):
        min_y = obj.vertices[:, 1].min()
        offset_y = platform_y - min_y
        obj.translate([0, offset_y, 0])

    def draw(self):
        self.screen.fill(pg.Color('darkslategray'))
        self.floor.draw()
        for wall in self.walls:
            wall.draw()
        self.object.draw()
        self.object.draw()
        self.draw_controls()

    def draw_controls(self):
        font = pg.font.SysFont('Consolas', 18)
        controls = [
            "Kontrol Kamera:",
            "W/A/S/D: Gerak Maju/Kiri/Mundur/Kanan",
            "Q/E    : Naik/Turun",
            "↑/↓/←/→: Rotasi Kamera",
            "",
            "Kontrol Bola:",
            "I/J/K/L : Geser Bola ",
            "          (Atas/Kiri/Bawah/Kanan)",
            "",
            "Kontrol Properti:",
                f"Kecepatan   : {self.object.move_speed:.2f}",
                f"Lompat      : {self.object.jump_strength:.2f}",
                f"Restitusi   : {self.object.restitution:.2f}",
                f"Ukuran Bola : {self.object.radius:.2f}",
                "",
                "[/] : Perkecil / Perbesar",
                "Z/X : + / - Kecepatan",
                "C/V : + / - Lompat",
                "B/N : + / - Restitusi",
            "",
            "R     : Reset Posisi Bola"    
        ]
        
        padding = 24
        width = 400
        height = len(controls) * 22 + padding
        box_surface = pg.Surface((width, height), pg.SRCALPHA)
        box_surface.fill((30, 30, 30, 180)) 

        for i, line in enumerate(controls):
            text = font.render(line, True, pg.Color("white"))
            box_surface.blit(text, (10, i * 22 + 5))
        
        self.screen.blit(box_surface, (10, 10))


    def run(self):
        while True:
            self.draw()
            self.camera.control()
            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()
            self.clock.tick(self.FPS)

if __name__ == '__main__':
    app = SoftwareRender()
    app.run()