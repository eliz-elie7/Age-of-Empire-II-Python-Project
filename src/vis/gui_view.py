import os
import pygame
from typing import Tuple
from src.vis.view_base import View

TILE = 32.0  # 1 tile = 32 pixels

# ================== PATHS ==================
SPRITES_ROOT = os.path.join(os.getcwd(), "Sprites")
BG_IMAGE_PATH = os.path.join(SPRITES_ROOT, "sol.png")


# ================== ISO PROJECTION ==================
def iso_project(tx: float, ty: float) -> Tuple[float, float]:
    # projection isométrique homogène (plus stable visuellement)
    sx = (tx - ty) * (TILE / 2)
    sy = (tx + ty) * (TILE / 2)
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

        self.width = 1800
        self.height = 1000
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Medievali – Isometric View")
        self.clock = pygame.time.Clock()

        # camera
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 0.2
        self.freeze_camera_frames = 0

        # behavior controls
        self.auto_follow = True
        self.follow_smooth = 0.15
        self.zoom_speed = 1.03
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        self.drag_sensitivity = 0.015

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
    # ================== SPRITES ==================
    def load_sprites(self):
        self.sprites.clear()

        if not os.path.isdir(SPRITES_ROOT):
            return

        for unit_type in os.listdir(SPRITES_ROOT):
            ut_path = os.path.join(SPRITES_ROOT, unit_type)
            if not os.path.isdir(ut_path):
                continue

            unit_type = unit_type.lower()
            self.sprites[unit_type] = {}

            for color in os.listdir(ut_path):
                cpath = os.path.join(ut_path, color)
                if not os.path.isdir(cpath):
                    continue

                color_key = color.lower()
                self.sprites[unit_type][color_key] = {}

                for fname in os.listdir(cpath):
                    if not fname.lower().endswith(".png"):
                        continue

                    direction = os.path.splitext(fname)[0].lower()
                    surf = pygame.image.load(
                        os.path.join(cpath, fname)
                    ).convert_alpha()

                    ow, oh = surf.get_size()
                    scale = (TILE * 1.6) / max(ow, oh)
                    surf = pygame.transform.smoothscale(
                        surf,
                        (int(ow * scale), int(oh * scale))
                    )

                    self.sprites[unit_type][color_key][direction] = surf

        self.loaded = True



    # ================== INPUT ==================
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try: self.stop()
                except Exception: pass
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    try: self.stop()
                    except Exception: pass
                    return "quit"

                if event.key == pygame.K_F9:
                    return "switch_view"

                if event.key == pygame.K_c:
                    self.center_on_units()

                if event.key == pygame.K_f:
                    self.auto_follow = not self.auto_follow

                if event.key == pygame.K_z:
                    self.zoom = 1.0

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.camera_x -= 12 / max(self.zoom, 0.1)
                    self.auto_follow = False
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.camera_x += 12 / max(self.zoom, 0.1)
                    self.auto_follow = False
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.camera_y -= 12 / max(self.zoom, 0.1)
                    self.auto_follow = False
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.camera_y += 12 / max(self.zoom, 0.1)
                    self.auto_follow = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse = pygame.mouse.get_pos()
                    self.auto_follow = False
                elif event.button == 4:
                    self.zoom = min(self.zoom * self.zoom_speed, self.max_zoom)
                elif event.button == 5:
                    self.zoom = max(self.zoom / self.zoom_speed, self.min_zoom)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            if event.type == pygame.MOUSEMOTION and self.dragging:
                mx, my = pygame.mouse.get_pos()
                lx, ly = self.last_mouse
                dx = mx - lx
                dy = my - ly
                self.camera_x -= dx * self.drag_sensitivity / max(self.zoom, 0.1)
                self.camera_y -= dy * self.drag_sensitivity / max(self.zoom, 0.1)
                self.last_mouse = (mx, my)

        return None


    # ================== CAMERA HELPERS ==================
    def center_on_units(self, initial_game_state=None):
        gs = initial_game_state if initial_game_state else getattr(self.battle, "get_state", lambda: None)()
        avgx = avgy = 0.0

        if gs:
            units = []
            for p in gs.get("players", []):
                units.extend(p.get("units", []))

            if units:
                avgx = sum(u.get("x", 0) for u in units) / len(units)
                avgy = sum(u.get("y", 0) for u in units) / len(units)

        self.camera_x = avgx
        self.camera_y = avgy


    # ================== PROJECTION ==================
    def world_to_screen(self, wx: float, wy: float):
        tx = wx - self.camera_x
        ty = wy - self.camera_y

        sx, sy = iso_project(tx, ty)
        sx *= self.zoom
        sy *= self.zoom

        # 🔒 anti-glissement
        sx = round(sx)
        sy = round(sy)

        return sx + self.width / 2, sy + self.height / 2


    # ================== RENDER ==================
    def render(self, game_state):

        # auto-follow caméra
        if self.freeze_camera_frames > 0:
            self.freeze_camera_frames -= 1
        else:

            if self.auto_follow and getattr(self, "battle", None):
                gs = self.battle.get_state()
                units = []
                for p in gs.get("players", []):
                    units.extend(p.get("units", []))

                    if units:
                        tx = sum(u.get("x", 0) for u in units) / len(units)
                        ty = sum(u.get("y", 0) for u in units) / len(units)
                        self.camera_x += (tx - self.camera_x) * self.follow_smooth
                        self.camera_y += (ty - self.camera_y) * self.follow_smooth

        # ----- background synchronisé caméra iso -----
        if self.bg:
            cx, cy = iso_project(self.camera_x, self.camera_y)
            ox = int(cx) % self.bg.get_width()
            oy = int(cy) % self.bg.get_height()

            for x in range(-1, 2):
                for y in range(-1, 2):
                    self.screen.blit(
                        self.bg,
                        (-ox + x * self.bg.get_width(),
                         -oy + y * self.bg.get_height())
                    )
        else:
            self.screen.fill((40, 40, 50))

        if not game_state:
            pygame.display.flip()
            self.clock.tick(60)
            return

        render_list = []

        for p in game_state.get("players", []):
            color = p.get("color", "blue").lower()

            for u in p.get("units", []):
                wx, wy = u["x"], u["y"]
                unit_type = symbol_to_type(u.get("symbol"))

                surf = self.pick_sprite(unit_type, color)
                sx, sy = self.world_to_screen(wx, wy)

                # ✅ profondeur écran (clé du 2.5D propre)
                depth = sy

                render_list.append((depth, surf, sx, sy, u.get("hp", 0), color))

        render_list.sort(key=lambda e: e[0])

        for _, surf, sx, sy, hp, color in render_list:
            if surf:
                anchor_x = surf.get_width() // 2
                anchor_y = surf.get_height() - int(TILE * 0.35) # Teste 0.35 ou 0.4

                x = sx - anchor_x
                y = sy - anchor_y
                shadow_w = surf.get_width() * 0.6
                shadow_h = surf.get_height() * 0.2

                shadow = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
                # 2. Dessine l'ombre légèrement PLUS BAS que les pieds pour donner du relief
                self.screen.blit(shadow, (sx - shadow_w // 2, sy - shadow_h // 4))
                self.screen.blit(surf, (x, y))

        pygame.display.flip()
        self.clock.tick(60)


    # ================== SPRITE PICK ==================
    def pick_sprite(self, unit_type: str, color: str):
        ut = self.sprites.get(unit_type.lower())
        if not ut:
            return None
        return ut.get(color.lower(), {}).values().__iter__().__next__()
        # ================== VIEW LIFECYCLE ==================
    def on_enter(self, battle, game_state):
        self.battle = battle
        self.load_sprites()
        self.center_on_units(initial_game_state=game_state)
        self.auto_follow = True
        self.freeze_camera_frames = 60  # ~1 seconde à 60 FPS


    def on_exit(self):
        pass

