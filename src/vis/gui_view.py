import os
import pygame
import sys
import math
from typing import Tuple, Dict
from src.vis.view_base import View

TILE = 32.0

# ================== PATHS ==================
SPRITES_ROOT = os.path.join(os.getcwd(), "Sprites")
BG_IMAGE_PATH = os.path.join(SPRITES_ROOT, "sol.png")

def iso_project(tx: float, ty: float) -> Tuple[float, float]:
    sx = (tx - ty) * (TILE / 2)
    sy = (tx + ty) * (TILE / 2)
    return sx, sy

def symbol_to_type(symbol: str) -> str:
    s = (symbol or "").lower()
    if "k" in s: return "knight"
    if "p" in s: return "pikeman"
    if "c" in s or "x" in s: return "crossbowman"
    if "s" in s or "s" in s: return "longswordman"
    if "e" in s: return "eliteskirmisher"
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
        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        self.ui_mode = 3 
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 0.15
        self.last_zoom = 0.2 
        self.freeze_camera_frames = 0
        
        self.minimap_size = 200
        self.minimap_margin = 20
        self.minimap_rect = pygame.Rect(
            self.width - self.minimap_size - self.minimap_margin,
            self.height - self.minimap_size - self.minimap_margin,
            self.minimap_size,
            self.minimap_size
        )

        self.auto_follow = True
        self.follow_smooth = 0.15
        self.zoom_speed = 1.03
        self.min_zoom = 0.05
        self.max_zoom = 4.0
        self.drag_sensitivity = 0.015
        self.dragging = False
        self.last_mouse = None

        self.sprites = {} 
        self.scaled_cache = {} 
        self.loaded = False

        self.bg = None
        if os.path.isfile(BG_IMAGE_PATH):
            self.bg = pygame.image.load(BG_IMAGE_PATH).convert()
            self.bg = pygame.transform.scale(self.bg, (self.width, self.height))

    def load_sprites(self):
        """Charge les sprites en les classant par Type > Couleur > Direction."""
        self.sprites.clear()
        self.scaled_cache.clear()
        if not os.path.isdir(SPRITES_ROOT): return

        for unit_type_folder in os.listdir(SPRITES_ROOT):
            ut_path = os.path.join(SPRITES_ROOT, unit_type_folder)
            if not os.path.isdir(ut_path): continue
            u_key = unit_type_folder.lower()
            self.sprites[u_key] = {}

            for color_folder in os.listdir(ut_path):
                cpath = os.path.join(ut_path, color_folder)
                if not os.path.isdir(cpath): continue
                c_key = color_folder.lower()
                self.sprites[u_key][c_key] = {}

                for fname in os.listdir(cpath):
                    if not fname.lower().endswith(".png"): continue
                    surf = pygame.image.load(os.path.join(cpath, fname)).convert_alpha()
                    
                    if "eliteskirmisher" in u_key:
                    # On définit le blanc (255, 255, 255) comme transparent
                        bg_color = surf.get_at((0, 0))
                        surf.set_colorkey(bg_color)
                    # --- AGRANDISSEMENT : base_scale à 2.2 au lieu de 1.5 ---
                    ow, oh = surf.get_size()
                    #base_scale = (TILE * 2.2) / max(ow, oh)
                    reference_dim = (ow + oh) / 2  # On prend la moyenne des deux dimensions
                    base_scale = (TILE * 2.8) / reference_dim 

                    # On ajuste spécifiquement pour les chevaliers s'ils restent trop petits
                    if "knight" in u_key:
                        base_scale *= 1.2  # On redonne 20% de taille aux cavaliers
                    surf = pygame.transform.smoothscale(surf, (int(ow * base_scale), int(oh * base_scale)))
                    
                    # On utilise le nom du fichier (sans extension) comme clé de direction
                    direction_name = os.path.splitext(fname)[0].lower()
                    self.sprites[u_key][c_key][direction_name] = surf
        self.loaded = True

    def get_direction_str(self, vx: float, vy: float) -> str:
        """Détermine la direction cardinale à partir d'un vecteur."""
        if abs(vx) < 0.01 and abs(vy) < 0.01:
            return "down"
        # Calcul de l'angle en degrés
        angle = math.degrees(math.atan2(vy, vx))
        # Ajustement pour la perspective isométrique (offset de 45°)
        if -45 <= angle <= 45: return "right"
        if 45 < angle <= 135: return "down"
        if -135 <= angle < -45: return "up"
        return "left"

    def get_scaled_sprite(self, unit_type, color, direction="down"):
        """Récupère le sprite orienté et mis à l'échelle."""
        ut = self.sprites.get(unit_type)
        if not ut: return None
        cl = ut.get(color)
        if not cl: return None
        
        # On cherche la direction spécifiée, sinon "down", sinon la première disponible
        base_surf = cl.get(direction) or cl.get("down") or next(iter(cl.values()))
        
        if abs(self.zoom - self.last_zoom) > 0.01:
            self.scaled_cache.clear()
            self.last_zoom = self.zoom
            
        cache_key = f"{unit_type}_{color}_{direction}"
        if cache_key not in self.scaled_cache:
            s_fact = self.zoom * 5.0
            nw = max(1, int(base_surf.get_width() * s_fact))
            nh = max(1, int(base_surf.get_height() * s_fact))
            self.scaled_cache[cache_key] = pygame.transform.smoothscale(base_surf, (nw, nh))
        return self.scaled_cache[cache_key]

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game()
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.exit_game()
                    return "quit"

                if event.key == pygame.K_F1: self.ui_mode = 0
                if event.key == pygame.K_F2: self.ui_mode = 1
                if event.key == pygame.K_F3: self.ui_mode = 2
                if event.key == pygame.K_F4: self.ui_mode = 3
               
                if event.key == pygame.K_TAB: return "\t"
                if event.key == pygame.K_F11: return "save"
                if event.key == pygame.K_F12: return "load"

                if event.key == pygame.K_n:
                    self.zoom = min(self.zoom * 1.2, self.max_zoom)
                if event.key == pygame.K_z:
                    self.zoom = max(self.zoom / 1.2, self.min_zoom)

                if event.key == pygame.K_p: return "pause"
                if event.key == pygame.K_k: return "accelerer"
                if event.key == pygame.K_r: return "normal"
            
                if event.key == pygame.K_F9: return "switch_view"
                if event.key == pygame.K_c: self.center_on_units()
                if event.key == pygame.K_f: self.auto_follow = not self.auto_follow

                cam_speed = 15 / max(self.zoom, 0.1)
                if event.key in (pygame.K_LEFT, pygame.K_a): self.camera_x -= cam_speed; self.auto_follow = False
                if event.key in (pygame.K_RIGHT, pygame.K_d): self.camera_x += cam_speed; self.auto_follow = False
                if event.key in (pygame.K_UP, pygame.K_w): self.camera_y -= cam_speed; self.auto_follow = False
                if event.key in (pygame.K_DOWN, pygame.K_s): self.camera_y += cam_speed; self.auto_follow = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.ui_mode in (2, 3) and self.minimap_rect.collidepoint(event.pos):
                    self.move_camera_to_minimap(event.pos)
                    return None
                if event.button == 1: 
                    self.dragging, self.last_mouse, self.auto_follow = True, event.pos, False
                elif event.button == 4: self.zoom = min(self.zoom * self.zoom_speed, self.max_zoom)
                elif event.button == 5: self.zoom = max(self.zoom / self.zoom_speed, self.min_zoom)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: self.dragging = False

            if event.type == pygame.MOUSEMOTION and self.dragging:
                dx, dy = event.pos[0] - self.last_mouse[0], event.pos[1] - self.last_mouse[1]
                self.camera_x -= dx * self.drag_sensitivity / max(self.zoom, 0.1)
                self.camera_y -= dy * self.drag_sensitivity / max(self.zoom, 0.1)
                self.last_mouse = event.pos
        return None

    def exit_game(self):
        pygame.quit()

    def draw_unit_counters(self, game_state):
        if self.ui_mode not in (1, 3): return
        y_off = 20
        for p in game_state.get("players", []):
            c_name = p.get("color", "white")
            counts = {"knight": 0, "pikeman": 0, "crossbowman": 0 , "longswordman": 0 , "eliteskirmisher": 0}
            for u in p.get("units", []):
                counts[symbol_to_type(u.get("symbol"))] += 1
            
            header = self.font.render(f"PLAYER {c_name.upper()} : {len(p.get('units', []))}", True, pygame.Color(c_name))
            self.screen.blit(header, (20, y_off))
            y_off += 25
            for ut, count in counts.items():
                txt = self.font.render(f"  {ut.capitalize()}: {count}", True, (200, 200, 200))
                self.screen.blit(txt, (20, y_off))
                y_off += 20
            y_off += 10

    def draw_minimap(self, game_state):
        if self.ui_mode not in (2, 3): return
        pygame.draw.rect(self.screen, (25, 25, 25), self.minimap_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), self.minimap_rect, 1)
        if not game_state or not hasattr(self, 'battle'): return
        
        mw, mh = self.battle.map.width, self.battle.map.height
        for p in game_state.get("players", []):
            for u in p.get("units", []):
                mx = self.minimap_rect.x + (u["x"] / mw) * self.minimap_size
                my = self.minimap_rect.y + (u["y"] / mh) * self.minimap_size
                pygame.draw.rect(self.screen, p.get("color", "white"), (int(mx), int(my), 2, 2))

    def move_camera_to_minimap(self, pos):
        rx = (pos[0] - self.minimap_rect.x) / self.minimap_size
        ry = (pos[1] - self.minimap_rect.y) / self.minimap_size
        if hasattr(self, 'battle'):
            self.camera_x, self.camera_y = rx * self.battle.map.width, ry * self.battle.map.height
            self.auto_follow = False

    def render(self, game_state):
        # Auto-follow
        if self.auto_follow and getattr(self, "battle", None):
            gs = self.battle.get_state()
            all_u = [u for p in gs.get("players", []) for u in p.get("units", [])]
            if all_u:
                tx, ty = sum(u["x"] for u in all_u)/len(all_u), sum(u["y"] for u in all_u)/len(all_u)
                self.camera_x += (tx - self.camera_x) * self.follow_smooth
                self.camera_y += (ty - self.camera_y) * self.follow_smooth

        # Dessin Background
        if self.bg:
            cx, cy = iso_project(self.camera_x, self.camera_y)
            ox, oy = int(cx * self.zoom) % self.bg.get_width(), int(cy * self.zoom) % self.bg.get_height()
            self.screen.blit(self.bg, (-ox, -oy))
            self.screen.blit(self.bg, (-ox + self.bg.get_width(), -oy))
            self.screen.blit(self.bg, (-ox, -oy + self.bg.get_height()))
            self.screen.blit(self.bg, (-ox + self.bg.get_width(), -oy + self.bg.get_height()))
        else: self.screen.fill((40, 40, 50))

        if not game_state: return

        render_list = []
        for p in game_state.get("players", []):
            color = p.get("color", "blue").lower()
            for u in p.get("units", []):
                # DETERMINATION DE LA DIRECTION POUR LE SPRITE
                # Si l'unité a une cible, elle regarde vers elle, sinon vers son mouvement
                order = u.get("order_type")
                look_vx, look_vy = 0, 0
                
                # Récupération de la direction depuis l'objet réel si possible
                # (Assumes l'unité stocke sa 'direction' calculée dans Unit.update)
                direction = u.get("direction", "down")
                
                surf = self.get_scaled_sprite(symbol_to_type(u.get("symbol")), color, direction)
                if surf:
                    sx, sy = self.world_to_screen(u["x"], u["y"])
                    el = self.battle.world_map.get_elevation_at(u["x"], u["y"])
                    render_list.append((sy, surf, sx, sy, el))

        # Tri par profondeur (Z-ordering)
        render_list.sort(key=lambda e: e[0])
        v_s = self.zoom * 5.0 

        for _, surf, sx, sy, el in render_list:
            # Ancrage : centre horizontal, bas du sprite
            ax, ay = surf.get_width() // 2, int(surf.get_height() * 0.85)
            
            # 1. SOL (Indicateur sobre d'élévation)
            if el > 0:
                terrain_color = (60, 80, 60) if el == 1 else (90, 110, 90)
                pygame.draw.circle(self.screen, terrain_color, (sx, sy), int(TILE * 0.6 * self.zoom))

            # 2. OMBRE
            sh_w, sh_h = TILE * 0.8 * v_s, TILE * 0.4 * v_s
            shadow = pygame.Surface((int(sh_w), int(sh_h)), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
            self.screen.blit(shadow, (sx - sh_w // 2, sy - sh_h // 2))
            
            # 3. UNITÉ
            self.screen.blit(surf, (sx - ax, sy - ay))

        self.draw_unit_counters(game_state)
        self.draw_minimap(game_state)
        pygame.display.flip()
        self.clock.tick(60)

    def world_to_screen(self, wx, wy):
        tx, ty = wx - self.camera_x, wy - self.camera_y
        sx, sy = iso_project(tx, ty)
        elevation = self.battle.world_map.get_elevation_at(wx, wy)
        # Décalage vertical sobre par niveau
        height_offset = elevation * 15.0 * self.zoom
        return round(sx * self.zoom + self.width/2), round((sy * self.zoom) - height_offset + self.height/2)

    def center_on_units(self, initial_game_state=None):
        gs = initial_game_state if initial_game_state else getattr(self.battle, "get_state", lambda: None)()
        if gs:
            units = [u for p in gs.get("players", []) for u in p.get("units", [])]
            if units:
                self.camera_x = sum(u["x"] for u in units) / len(units)
                self.camera_y = sum(u["y"] for u in units) / len(units)

    def on_enter(self, battle, game_state):
        self.battle = battle
        self.load_sprites()
        self.center_on_units(game_state)
        self.auto_follow = True

    def on_exit(self): 
        self.sprites.clear()
        self.scaled_cache.clear()
        pygame.quit()