# src/vis/gui_view.py
import os
import pygame
from typing import Tuple
from src.vis.view_base import View
from src.core.units import TILE

# ================== PATHS ==================
SPRITES_ROOT = os.path.join(os.getcwd(), "Sprites")
BG_IMAGE_PATH = os.path.join(SPRITES_ROOT, "sol.png")


# ================== ISO PROJECTION ==================
def iso_project(tx: float, ty: float) -> Tuple[float, float]:
    sx = (tx - ty) * (TILE / 2)
    sy = (tx + ty) * (TILE / 4)
    return sx, sy


# ================== SYMBOL → TYPE ==================
def symbol_to_type(symbol: str) -> str:
    s = (symbol or "").lower()
    if "k" in s:
        return "knight"
    if "p" in s:
        return "pikeman"
    if "c" in s or "x" in s:
        return "crossbowman"
    return "knight"


# ================== VIEW ==================
class IsometricView(View):

    def __init__(self):
        super().__init__()
        pygame.init()

        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.FULLSCREEN
        )
        pygame.display.set_caption("Medievali – Isometric View")
        self.clock = pygame.time.Clock()

        # camera
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 1.0

        self.dragging = False
        self.last_mouse = None

        # sprites
        self.sprites = {}
        self.loaded = False

        # background
        self.bg = None
        if os.path.isfile(BG_IMAGE_PATH):
            self.bg = pygame.image.load(BG_IMAGE_PATH).convert()
            self.bg = pygame.transform.scale(self.bg, (self.width, self.height))


    # ================== INPUT ==================
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.stop()
                    return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                print("MOUSE DOWN")
                self.dragging = True
                self.last_mouse = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            if event.type == pygame.MOUSEMOTION and self.dragging:
                print("DRAG", mx - lx, my - ly)
                mx, my = pygame.mouse.get_pos()
                lx, ly = self.last_mouse
                self.camera_x -= (mx - lx) * 0.02
                self.camera_y -= (my - ly) * 0.02
                self.last_mouse = (mx, my)

        return None


    def on_exit(self):
        pass


    # ================== SPRITES ==================
    def load_sprites(self):
        self.sprites.clear()

        if not os.path.isdir(SPRITES_ROOT):
            return

        for unit_type in os.listdir(SPRITES_ROOT):
            ut_path = os.path.join(SPRITES_ROOT, unit_type)
            if not os.path.isdir(ut_path):
                continue

            self.sprites[unit_type] = {}

            for color in os.listdir(ut_path):
                cpath = os.path.join(ut_path, color)
                if not os.path.isdir(cpath):
                    continue

                self.sprites[unit_type][color] = {}

                for fname in os.listdir(cpath):
                    if not fname.lower().endswith(".png"):
                        continue

                    direction = os.path.splitext(fname)[0].lower()
                    surf = pygame.image.load(
                        os.path.join(cpath, fname)
                    ).convert_alpha()

                    # ===== AUTO SCALE AoE → ISO =====
                    ow, oh = surf.get_size()
                    scale = (TILE * 1.6) / max(ow, oh)
                    surf = pygame.transform.smoothscale(
                        surf,
                        (int(ow * scale), int(oh * scale))
                    )

                    self.sprites[unit_type][color][direction] = surf

        self.loaded = True


    # ================== LIFECYCLE ==================
    def on_enter(self, battle, game_state):
        self.battle = battle
        self.load_sprites()
        self.camera_x = 0.0
        self.camera_y = 0.0


    # ================== PROJECTION ==================
    def world_to_screen(self, wx: float, wy: float):
        tx = wx - self.camera_x
        ty = wy - self.camera_y

        sx, sy = iso_project(tx, ty)
        sx *= self.zoom
        sy *= self.zoom

        return sx + self.width / 2, sy + self.height / 2


    # ================== RENDER ==================
    def render(self, game_state):
        evt = self.handle_input()
        if evt == "QUIT":
            return

        # ----- background -----
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((40, 40, 50))

        if not game_state or not self.loaded:
            pygame.display.flip()
            self.clock.tick(60)
            return

        render_list = []

        for p in game_state.get("players", []):
            color = p.get("name", "").lower()

            for u in p.get("units", []):
                wx, wy = u["x"], u["y"]
                unit_type = symbol_to_type(u.get("symbol"))

                surf = self.pick_sprite(unit_type, color)
                if not surf:
                    continue

                sx, sy = self.world_to_screen(wx, wy)
                depth = wx + wy

                render_list.append((depth, surf, sx, sy, u.get("hp", 0)))

        # depth sort
        render_list.sort(key=lambda e: e[0])

        for _, surf, sx, sy, hp in render_list:
            x = sx - surf.get_width() // 2
            y = sy - surf.get_height()
            self.screen.blit(surf, (x, y))

            # HP bar
            bar_w = surf.get_width() // 2
            bx = x + surf.get_width() // 4
            by = y - 6
            pygame.draw.rect(self.screen, (60, 60, 60), (bx, by, bar_w, 4))
            pygame.draw.rect(
                self.screen,
                (0, 200, 0),
                (bx, by, int(bar_w * (hp / 100)), 4)
            )
        sx, sy = self.world_to_screen(0, 0)
        pygame.draw.circle(self.screen, (255, 0, 0), (int(sx), int(sy)), 6)

        pygame.display.flip()
        self.clock.tick(60)


    # ================== SPRITE PICK ==================
    def pick_sprite(self, unit_type: str, color: str):
        ut = self.sprites.get(unit_type)
        if not ut:
            return None

        col = ut.get(color) or next(iter(ut.values()))
        return (
            col.get("down")
            or col.get("right")
            or next(iter(col.values()))
        )
