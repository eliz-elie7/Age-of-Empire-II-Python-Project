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

        # behavior controls
        self.auto_follow = True            # auto-center on units
        self.follow_smooth = 0.15          # smoothing factor for auto-follow (0..1)
        self.zoom_speed = 1.03             # smaller zoom step (previously 1.1)
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        self.drag_sensitivity = 0.015      # smaller drag sensitivity

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
                try: self.stop()
                except Exception: pass
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    try: self.stop()
                    except Exception: pass
                    return "quit"
                # recenter camera on units
                if event.key == pygame.K_c:
                    self.center_on_units()
                # toggle auto-follow
                if event.key == pygame.K_f:
                    self.auto_follow = not self.auto_follow
                # reset zoom
                if event.key == pygame.K_z:
                    self.zoom = 1.0
                # keyboard pan (slower)
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

            # Mouse buttons + wheel
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse = pygame.mouse.get_pos()
                    self.auto_follow = False  # manual drag disables auto-follow
                elif event.button == 4:
                    # wheel up -> zoom in (slower)
                    self.zoom = min(self.zoom * self.zoom_speed, self.max_zoom)
                elif event.button == 5:
                    # wheel down -> zoom out (slower)
                    self.zoom = max(self.zoom / self.zoom_speed, self.min_zoom)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            if event.type == pygame.MOUSEMOTION and self.dragging:
                mx, my = pygame.mouse.get_pos()
                lx, ly = self.last_mouse
                dx = mx - lx
                dy = my - ly
                # use reduced sensitivity and account for zoom
                self.camera_x -= dx * self.drag_sensitivity / max(self.zoom, 0.1)
                self.camera_y -= dy * self.drag_sensitivity / max(self.zoom, 0.1)
                self.last_mouse = (mx, my)

            # Touch (mobile) support: positions normalized [0..1]
            if event.type == pygame.FINGERDOWN:
                fx = int(event.x * self.width)
                fy = int(event.y * self.height)
                self.dragging = True
                self.last_mouse = (fx, fy)
                self.auto_follow = False

            if event.type == pygame.FINGERMOTION and getattr(self, "dragging", False):
                dx = event.dx * self.width
                dy = event.dy * self.height
                self.camera_x -= dx * self.drag_sensitivity / max(self.zoom, 0.1)
                self.camera_y -= dy * self.drag_sensitivity / max(self.zoom, 0.1)
                self.last_mouse = (int(event.x * self.width), int(event.y * self.height))

            if event.type == pygame.FINGERUP:
                self.dragging = False

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
        # center camera on current units (or map center if none)
        self.center_on_units(initial_game_state=game_state)
        # keep auto_follow enabled at start so user sees formation
        self.auto_follow = True

    # new helper to center camera on units
    def center_on_units(self, initial_game_state=None):
        gs = initial_game_state if initial_game_state is not None else getattr(self, "battle", None) and self.battle.get_state()
        avgx = avg_y = 0.0
        if gs:
            units = []
            for p in gs.get("players", []):
                units.extend(p.get("units", []))
            if units:
                avgx = sum(u.get("x", 0) for u in units) / len(units)
                avg_y = sum(u.get("y", 0) for u in units) / len(units)
            else:
                wm = getattr(self.battle, "world_map", None)
                if wm:
                    try:
                        avgx = wm.get_width() / 2.0
                        avg_y = wm.get_height() / 2.0
                    except Exception:
                        avgx = getattr(wm, "width", 0) / 2.0
                        avg_y = getattr(wm, "height", 0) / 2.0
        else:
            wm = getattr(self.battle, "world_map", None)
            if wm:
                try:
                    avgx = wm.get_width() / 2.0
                    avg_y = wm.get_height() / 2.0
                except Exception:
                    avgx = getattr(wm, "width", 0) / 2.0
                    avg_y = getattr(wm, "height", 0) / 2.0

        self.camera_x = avgx
        self.camera_y = avg_y


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
        evt = None  # input handled by main loop; keep local variable to avoid accidental use
        # If auto-follow is active and we have a battle state, smoothly follow average unit pos
        if self.auto_follow and getattr(self, "battle", None):
            gs = self.battle.get_state()
            units = []
            if gs:
                for p in gs.get("players", []):
                    units.extend(p.get("units", []))
            if units:
                target_x = sum(u.get("x", 0) for u in units) / len(units)
                target_y = sum(u.get("y", 0) for u in units) / len(units)
            else:
                wm = getattr(self.battle, "world_map", None)
                if wm:
                    try:
                        target_x = wm.get_width() / 2.0
                        target_y = wm.get_height() / 2.0
                    except Exception:
                        target_x = getattr(wm, "width", 0) / 2.0
                        target_y = getattr(wm, "height", 0) / 2.0
                else:
                    target_x = self.camera_x
                    target_y = self.camera_y
            # smooth interpolation toward target
            self.camera_x += (target_x - self.camera_x) * self.follow_smooth
            self.camera_y += (target_y - self.camera_y) * self.follow_smooth

        # ----- background (tiled with camera offset) -----
        if self.bg:
            bw, bh = self.bg.get_size()
            ox = int(self.camera_x) % bw
            oy = int(self.camera_y) % bh
            cols = (self.width // bw) + 2
            rows = (self.height // bh) + 2
            for i in range(-1, cols - 1):
                for j in range(-1, rows - 1):
                    bx = -ox + i * bw
                    by = -oy + j * bh
                    self.screen.blit(self.bg, (bx, by))
        else:
            self.screen.fill((40, 40, 50))

        if not game_state:
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
                sx, sy = self.world_to_screen(wx, wy)
                depth = wx + wy

                render_list.append((depth, surf, sx, sy, u.get("hp", 0), color))

        # depth sort
        render_list.sort(key=lambda e: e[0])

        for _, surf, sx, sy, hp, color in render_list:
            if surf:
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
            else:
                # fallback: draw a simple circle and HP bar
                cx, cy = int(sx), int(sy)
                mapping = {
                    "player a": (50, 120, 200),
                    "player b": (200, 30, 30),
                    "red": (200, 30, 30),
                    "blue": (50, 120, 200),
                    "green": (50, 180, 50),
                    "yellow": (230, 200, 50)
                }
                rgb = mapping.get(color, None)
                if rgb is None:
                    h = abs(hash(color)) % 255
                    rgb = (h, 120, 255 - h)
                pygame.draw.circle(self.screen, rgb, (cx, cy - 8), 12)
                # HP bar
                bar_w = 20
                bx = cx - bar_w // 2
                by = cy - 26
                pygame.draw.rect(self.screen, (60, 60, 60), (bx, by, bar_w, 4))
                pygame.draw.rect(self.screen, (0, 200, 0), (bx, by, int(bar_w * (hp / 100)), 4))

        sx, sy = self.world_to_screen(0, 0)
        pygame.draw.circle(self.screen, (255, 0, 0), (int(sx), int(sy)), 6)

        pygame.display.flip()
        self.clock.tick(60)


    # ================== SPRITE PICK ==================
    def pick_sprite(self, unit_type: str, color: str):
        ut = self.sprites.get(unit_type)
        if not ut:
            return None

        col = ut.get(color)
        if not col:
            try:
                col = next(iter(ut.values()))
            except StopIteration:
                return None

        # prefer down -> right -> any
        try:
            return col.get("down") or col.get("right") or next(iter(col.values()))
        except Exception:
            return None
