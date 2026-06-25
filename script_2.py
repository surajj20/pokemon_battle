from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import random
import sys
import math

try:
    import pygame
except ImportError as exc:
    raise SystemExit(
        "Pygame is required. Install it with: pip install pygame"
    ) from exc


# ─── Type Effectiveness ───────────────────────────────────────────────────────
TYPE_EFFECTIVENESS = {
    "Fire":     {"Grass": 2.0, "Water": 0.5, "Electric": 1.0, "Rock": 0.5,  "Psychic": 1.0, "Normal": 1.0, "Flying": 1.0, "Ice": 2.0},
    "Water":    {"Fire": 2.0,  "Grass": 0.5, "Electric": 0.5, "Rock": 2.0,  "Psychic": 1.0, "Normal": 1.0, "Flying": 1.0, "Ice": 1.0},
    "Grass":    {"Water": 2.0, "Fire": 0.5,  "Electric": 1.0, "Rock": 2.0,  "Psychic": 1.0, "Normal": 1.0, "Flying": 0.5, "Ice": 1.0},
    "Electric": {"Water": 2.0, "Grass": 0.5, "Fire": 1.0,    "Flying": 2.0, "Rock": 1.0,    "Psychic": 1.0, "Normal": 1.0, "Ice": 1.0},
    "Rock":     {"Fire": 2.0,  "Flying": 2.0,"Ice": 2.0,     "Water": 1.0,  "Grass": 1.0,   "Electric": 1.0,"Psychic": 1.0,"Normal": 1.0},
    "Psychic":  {"Psychic": 1.0,"Fire": 1.0, "Water": 1.0,   "Grass": 1.0,  "Electric": 1.0,"Rock": 1.0,    "Normal": 1.0, "Flying": 1.0,"Ice": 1.0},
    "Flying":   {"Grass": 2.0, "Electric": 0.5,"Rock": 0.5,  "Fire": 1.0,   "Water": 1.0,   "Psychic": 1.0, "Normal": 1.0, "Ice": 1.0},
    "Ice":      {"Grass": 2.0, "Flying": 2.0,"Fire": 0.5,    "Water": 0.5,  "Electric": 1.0,"Rock": 1.0,    "Psychic": 1.0,"Normal": 1.0},
    "Normal":   {"Rock": 0.5,  "Flying": 1.0,"Fire": 1.0,    "Water": 1.0,  "Grass": 1.0,   "Electric": 1.0,"Psychic": 1.0,"Ice": 1.0},
}

# ─── Screen & FPS ─────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1100, 760
FPS = 60

# ─── Colour Palette (deep RPG dark theme) ─────────────────────────────────────
BG_DARK      = (12,  14,  26)
BG_MID       = (20,  24,  44)
PANEL_DARK   = (22,  26,  50)
PANEL_MID    = (30,  36,  68)
PANEL_LIGHT  = (40,  48,  88)
BORDER_DIM   = (55,  65, 110)
BORDER_GLOW  = (100, 130, 255)

WHITE        = (240, 245, 255)
OFF_WHITE    = (190, 200, 225)
BLACK        = (5,    5,  10)

RED_VIVID    = (255,  60,  80)
RED_DARK     = (180,  30,  50)
GREEN_VIVID  = ( 60, 220, 110)
GREEN_DARK   = ( 20, 140,  60)
ORANGE_VIVID = (255, 160,  40)
ORANGE_DARK  = (200, 100,  20)
YELLOW_VIVID = (255, 220,  50)
GOLD         = (220, 175,  50)
PURPLE_VIVID = (180,  80, 255)
BLUE_VIVID   = ( 80, 160, 255)
CYAN_VIVID   = ( 60, 220, 220)
TEAL         = ( 40, 180, 160)

GRAY_DIM     = ( 80,  90, 120)
GRAY_MID     = (120, 135, 170)

# ─── Type colours ─────────────────────────────────────────────────────────────
TYPE_COLORS = {
    "Fire":     (255, 100,  40),
    "Water":    ( 50, 150, 255),
    "Grass":    ( 60, 200, 100),
    "Electric": (255, 215,  40),
    "Rock":     (170, 140,  90),
    "Psychic":  (220,  80, 200),
    "Flying":   (110, 185, 255),
    "Ice":      (140, 220, 255),
    "Normal":   (170, 175, 200),
}

# ─── Type emojis for the log ──────────────────────────────────────────────────
TYPE_EMOJI = {
    "Fire": "🔥", "Water": "💧", "Grass": "🌿", "Electric": "⚡",
    "Rock": "🪨", "Psychic": "🔮", "Flying": "🌪️", "Ice": "❄️", "Normal": "⭐",
}


# ─── Data classes ─────────────────────────────────────────────────────────────
@dataclass
class Move:
    name: str
    power: int
    move_type: str


@dataclass
class Pokemon:
    name: str
    p_type: str
    max_hp: int
    attack: int
    defense: int
    speed: int
    moves: List[Move]
    hp: int = field(init=False)

    def __post_init__(self) -> None:
        self.hp = self.max_hp

    @property
    def fainted(self) -> bool:
        return self.hp <= 0

    def reset(self) -> None:
        self.hp = self.max_hp

    def choose_best_move(self, opponent: "Pokemon") -> Move:
        best_move = self.moves[0]
        best_score = -1.0
        for move in self.moves:
            score = move.power * type_multiplier(move.move_type, opponent.p_type)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move


def type_multiplier(attack_type: str, defense_type: str) -> float:
    return TYPE_EFFECTIVENESS.get(attack_type, {}).get(defense_type, 1.0)


def damage(attacker: Pokemon, defender: Pokemon, move: Move) -> int:
    base = move.power + attacker.attack
    raw = (base * 2) / max(1, defender.defense)
    multiplier = type_multiplier(move.move_type, defender.p_type)
    variance = random.uniform(0.88, 1.0)
    return max(1, int(raw * multiplier * variance))


def build_pokedex() -> List[Pokemon]:
    return [
        Pokemon("Charizard", "Fire", 120, 28, 16, 26, [
            Move("Flame Burst", 26, "Fire"), Move("Air Slash", 22, "Flying"),
            Move("Bite", 18, "Normal"), Move("Inferno Wing", 32, "Fire"),
        ]),
        Pokemon("Blastoise", "Water", 135, 25, 22, 18, [
            Move("Water Gun", 20, "Water"), Move("Shell Bash", 24, "Normal"),
            Move("Aqua Tail", 28, "Water"), Move("Bubble Beam", 26, "Water"),
        ]),
        Pokemon("Venusaur", "Grass", 128, 26, 20, 17, [
            Move("Vine Whip", 20, "Grass"), Move("Leaf Blade", 28, "Grass"),
            Move("Solar Beam", 34, "Grass"), Move("Tackle", 16, "Normal"),
        ]),
        Pokemon("Pikachu", "Electric", 95, 30, 12, 34, [
            Move("Thunder Shock", 22, "Electric"), Move("Quick Attack", 18, "Normal"),
            Move("Spark", 26, "Electric"), Move("Volt Burst", 30, "Electric"),
        ]),
        Pokemon("Golem", "Rock", 145, 29, 26, 10, [
            Move("Rock Throw", 24, "Rock"), Move("Boulder Crush", 30, "Rock"),
            Move("Headbutt", 20, "Normal"), Move("Earth Slam", 28, "Rock"),
        ]),
        Pokemon("Alakazam", "Psychic", 100, 34, 10, 30, [
            Move("Psybeam", 26, "Psychic"), Move("Mind Shock", 30, "Psychic"),
            Move("Confusion", 22, "Psychic"), Move("Zen Cut", 18, "Normal"),
        ]),
        Pokemon("Pidgeot", "Flying", 110, 24, 16, 28, [
            Move("Gust", 20, "Flying"), Move("Wing Attack", 26, "Flying"),
            Move("Feather Rush", 18, "Normal"), Move("Sky Strike", 30, "Flying"),
        ]),
        Pokemon("Lapras", "Ice", 140, 24, 22, 16, [
            Move("Ice Beam", 30, "Ice"), Move("Frost Bite", 24, "Ice"),
            Move("Surf", 26, "Water"), Move("Body Slam", 20, "Normal"),
        ]),
    ]


# ─── Helpers ──────────────────────────────────────────────────────────────────
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_rounded_rect(surf, color, rect, radius=12, border_color=None, border_width=2):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, border_width, border_radius=radius)


def draw_gradient_rect(surf, top_color, bot_color, rect, radius=12):
    """Draw a vertical gradient rectangle."""
    clip = surf.get_clip()
    surf.set_clip(rect)
    r = pygame.Rect(rect)
    for y in range(r.height):
        t = y / max(1, r.height - 1)
        c = lerp_color(top_color, bot_color, t)
        pygame.draw.line(surf, c, (r.x, r.y + y), (r.x + r.width - 1, r.y + y))
    surf.set_clip(clip)
    pygame.draw.rect(surf, top_color, rect, 2, border_radius=radius)


def draw_hp_bar(surf, x, y, w, h, ratio, glow=False):
    """Draw a polished HP bar with color gradient based on ratio."""
    # Background track
    pygame.draw.rect(surf, (15, 18, 35), (x, y, w, h), border_radius=h // 2)
    pygame.draw.rect(surf, BORDER_DIM, (x, y, w, h), 1, border_radius=h // 2)

    if ratio <= 0:
        return

    fill_w = max(4, int(w * ratio))

    if ratio > 0.5:
        bar_top = lerp_color(GREEN_VIVID, (100, 255, 130), 0.4)
        bar_bot = GREEN_DARK
    elif ratio > 0.2:
        bar_top = ORANGE_VIVID
        bar_bot = ORANGE_DARK
    else:
        bar_top = RED_VIVID
        bar_bot = RED_DARK

    fill_rect = pygame.Rect(x, y, fill_w, h)
    draw_gradient_rect(surf, bar_top, bar_bot, fill_rect, radius=h // 2)

    # Shine strip
    shine_rect = pygame.Rect(x + 2, y + 1, fill_w - 4, max(1, h // 3))
    shine_surf = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
    shine_surf.fill((255, 255, 255, 50))
    surf.blit(shine_surf, shine_rect)


def draw_type_badge(surf, p_type, x, y, font):
    """Draw a small coloured type badge."""
    tc = TYPE_COLORS.get(p_type, GRAY_MID)
    label = font.render(p_type.upper(), True, BLACK)
    pad_x, pad_y = 10, 4
    bw = label.get_width() + pad_x * 2
    bh = label.get_height() + pad_y * 2
    badge_rect = pygame.Rect(x, y, bw, bh)
    draw_rounded_rect(surf, tc, badge_rect, radius=bh // 2)
    # darken border
    dark_tc = tuple(max(0, c - 60) for c in tc)
    pygame.draw.rect(surf, dark_tc, badge_rect, 1, border_radius=bh // 2)
    surf.blit(label, (x + pad_x, y + pad_y))
    return bw


def draw_stars(surf, x, y, count, filled, size=10, gap=14):
    """Draw star health indicators."""
    for i in range(count):
        cx = x + i * gap
        color = YELLOW_VIVID if i < filled else GRAY_DIM
        points = []
        for j in range(10):
            angle = math.pi / 2 + j * math.pi / 5
            r = size // 2 if j % 2 == 0 else size // 4
            points.append((cx + r * math.cos(angle), y + r * math.sin(angle)))
        if len(points) >= 3:
            pygame.draw.polygon(surf, color, points)


# ─── Button ───────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, text, fill, text_color=WHITE, enabled=True,
                 accent_color=None, icon=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.fill = fill
        self.text_color = text_color
        self.enabled = enabled
        self.accent = accent_color or fill
        self.icon = icon
        self._hovered = False

    def draw(self, surf, font, hovered=False):
        if not self.enabled:
            base = lerp_color(self.fill, PANEL_DARK, 0.6)
            border = BORDER_DIM
            tc = GRAY_DIM
        else:
            base = lerp_color(self.fill, (255, 255, 255), 0.08) if hovered else self.fill
            border = lerp_color(self.fill, WHITE, 0.4)
            tc = self.text_color

        # Shadow
        shadow_rect = self.rect.move(0, 3)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 80))
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80),
                         shadow_surf.get_rect(), border_radius=12)
        surf.blit(shadow_surf, shadow_rect)

        # Body gradient
        top_c = lerp_color(base, WHITE, 0.15)
        bot_c = lerp_color(base, BLACK, 0.2)
        draw_gradient_rect(surf, top_c, bot_c, self.rect, radius=12)
        pygame.draw.rect(surf, border, self.rect, 2, border_radius=12)

        # Shine
        shine = pygame.Rect(self.rect.x + 4, self.rect.y + 3,
                            self.rect.width - 8, self.rect.height // 3)
        sh = pygame.Surface((shine.width, shine.height), pygame.SRCALPHA)
        sh.fill((255, 255, 255, 35))
        surf.blit(sh, shine)

        full_text = f"{self.icon}  {self.text}" if self.icon else self.text
        label = font.render(full_text, True, tc)
        lr = label.get_rect(center=self.rect.center)
        surf.blit(label, lr)

    def contains(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


# ─── Particles ────────────────────────────────────────────────────────────────
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: int
    max_life: int
    color: Tuple[int, int, int]
    size: float

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # gravity
        self.life -= 1

    def draw(self, surf):
        t = self.life / self.max_life
        alpha = int(255 * t)
        s = max(1, int(self.size * t))
        ps = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        c = self.color + (alpha,)
        pygame.draw.circle(ps, c, (s, s), s)
        surf.blit(ps, (self.x - s, self.y - s))


# ─── Flash effect ─────────────────────────────────────────────────────────────
@dataclass
class FlashEffect:
    x: int
    y: int
    text: str
    color: Tuple[int, int, int]
    life: int = 60

    def update(self):
        self.life -= 1
        self.y -= 1

    def draw(self, surf, font):
        t = self.life / 60
        alpha = int(255 * min(1.0, t * 2))
        label = font.render(self.text, True, self.color)
        a_surf = pygame.Surface(label.get_size(), pygame.SRCALPHA)
        a_surf.blit(label, (0, 0))
        a_surf.set_alpha(alpha)
        surf.blit(a_surf, (self.x - label.get_width() // 2, self.y))


# ─── Main Game ────────────────────────────────────────────────────────────────
class DuelGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pokémon Team Duel")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.tick = 0

        # ── Fonts ──────────────────────────────────────────────────────────
        self.title_font  = pygame.font.SysFont("Georgia", 36, bold=True)
        self.header_font = pygame.font.SysFont("Georgia", 22, bold=True)
        self.body_font   = pygame.font.SysFont("Verdana", 17)
        self.small_font  = pygame.font.SysFont("Verdana", 14)
        self.tiny_font   = pygame.font.SysFont("Verdana", 12)
        self.badge_font  = pygame.font.SysFont("Verdana", 11, bold=True)
        self.log_font    = pygame.font.SysFont("Courier New", 14)
        self.big_font    = pygame.font.SysFont("Georgia", 52, bold=True)

        # ── Stars background ──────────────────────────────────────────────
        rng = random.Random(42)
        self.bg_stars = [(rng.randint(0, WIDTH), rng.randint(0, HEIGHT),
                          rng.uniform(0.3, 1.0)) for _ in range(120)]

        # ── Game state ────────────────────────────────────────────────────
        self.pokedex = build_pokedex()
        self.state = "team_select"
        self.team_size = 3
        self.selected_player_team: List[Pokemon] = []
        self.enemy_team: List[Pokemon] = []
        self.player_index = 0
        self.enemy_index = 0
        self.log: List[str] = ["Choose your team and start the duel!"]
        self.winner_text = ""

        self.particles: List[Particle] = []
        self.flash_effects: List[FlashEffect] = []

        # ── Buttons ───────────────────────────────────────────────────────
        self.roster_buttons: List[Button] = []
        self.team_size_buttons: List[Button] = []
        self.start_button = Button(
            pygame.Rect(820, 650, 220, 52), "Start Battle",
            (40, 160, 80), icon="⚔️", enabled=False
        )
        self.restart_button = Button(
            pygame.Rect(420, 490, 260, 52), "Play Again",
            (50, 100, 200), icon="🔄", enabled=False
        )
        self.move_buttons: List[Button] = []
        self.build_team_select_buttons()
        self.build_move_buttons()

    # ── Button builders ───────────────────────────────────────────────────────
    def build_team_select_buttons(self) -> None:
        self.roster_buttons = []
        sx, sy = 42, 162
        cw, ch = 235, 90
        gx, gy = 16, 12
        for i, poke in enumerate(self.pokedex):
            row, col = i // 2, i % 2
            rect = pygame.Rect(sx + col * (cw + gx), sy + row * (ch + gy), cw, ch)
            self.roster_buttons.append(Button(rect, poke.name, TYPE_COLORS[poke.p_type]))

        self.team_size_buttons = []
        for i, size in enumerate((1, 2, 3)):
            rect = pygame.Rect(826, 214 + i * 72, 210, 52)
            self.team_size_buttons.append(
                Button(rect, f"Team Size: {size}",
                       (60, 120, 200) if size != self.team_size else (40, 160, 80))
            )

    def build_move_buttons(self) -> None:
        self.move_buttons = []
        y = 614
        for i in range(4):
            rect = pygame.Rect(86 + i * 155, y, 143, 56)
            self.move_buttons.append(Button(rect, f"Move {i+1}", PANEL_MID))

    # ── State helpers ─────────────────────────────────────────────────────────
    def current_player(self) -> Optional[Pokemon]:
        while self.player_index < len(self.selected_player_team) and \
              self.selected_player_team[self.player_index].fainted:
            self.player_index += 1
        if self.player_index >= len(self.selected_player_team):
            return None
        return self.selected_player_team[self.player_index]

    def current_enemy(self) -> Optional[Pokemon]:
        while self.enemy_index < len(self.enemy_team) and \
              self.enemy_team[self.enemy_index].fainted:
            self.enemy_index += 1
        if self.enemy_index >= len(self.enemy_team):
            return None
        return self.enemy_team[self.enemy_index]

    def add_log(self, msg: str) -> None:
        self.log.append(msg)
        self.log = self.log[-6:]

    def spawn_hit_particles(self, cx, cy, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 5)
            self.particles.append(Particle(
                cx, cy, math.cos(angle) * speed, math.sin(angle) * speed - 1,
                life=random.randint(25, 50), max_life=50,
                color=color, size=random.uniform(3, 7)
            ))

    def update_particles(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        for f in self.flash_effects:
            f.update()
        self.flash_effects = [f for f in self.flash_effects if f.life > 0]

    # ── Battle logic ──────────────────────────────────────────────────────────
    def begin_battle(self) -> None:
        remaining = [p for p in self.pokedex if p not in self.selected_player_team]
        self.enemy_team = random.sample(
            remaining if len(remaining) >= self.team_size else self.pokedex,
            self.team_size
        )
        for p in self.selected_player_team + self.enemy_team:
            p.reset()
        self.player_index = 0
        self.enemy_index = 0
        self.log = ["Battle starts! Choose your move!"]
        self.state = "battle"
        self.restart_button.enabled = False

    def resolve_turn(self, player_move: Move) -> None:
        player = self.current_player()
        enemy  = self.current_enemy()
        if player is None or enemy is None:
            self.finish_battle()
            return

        enemy_move = enemy.choose_best_move(player)
        if player.speed >= enemy.speed:
            first, second = player, enemy
            fmove, smove = player_move, enemy_move
        else:
            first, second = enemy, player
            fmove, smove = enemy_move, player_move

        self.do_attack(first, second, fmove)
        if second.fainted:
            self.add_log(f"💀 {second.name} fainted!")
            self.advance_indices(second)
            self.check_battle_end()
            return

        self.do_attack(second, first, smove)
        if first.fainted:
            self.add_log(f"💀 {first.name} fainted!")
            self.advance_indices(first)
        self.check_battle_end()

    def do_attack(self, attacker: Pokemon, defender: Pokemon, move: Move) -> None:
        dealt = damage(attacker, defender, move)
        defender.hp = max(0, defender.hp - dealt)
        mult = type_multiplier(move.move_type, defender.p_type)
        emoji = TYPE_EMOJI.get(move.move_type, "")
        if mult > 1:
            effect = " SUPER EFFECTIVE!"
            flash_c = YELLOW_VIVID
        elif mult < 1:
            effect = " Not very effective."
            flash_c = GRAY_DIM
        else:
            effect = ""
            flash_c = WHITE

        self.add_log(f"{emoji} {attacker.name} → {move.name} [-{dealt} HP]{effect}")

        # Particle burst at defender position
        if attacker in self.selected_player_team:
            cx, cy = 840, 240  # enemy card center
        else:
            cx, cy = 280, 420  # player card center
        tc = TYPE_COLORS.get(move.move_type, WHITE)
        self.spawn_hit_particles(cx, cy, tc, count=22)
        if effect:
            self.flash_effects.append(FlashEffect(cx, cy - 40, effect.strip(), flash_c))

    def advance_indices(self, fainted: Pokemon) -> None:
        if fainted in self.selected_player_team:
            self.player_index += 1
        if fainted in self.enemy_team:
            self.enemy_index += 1

    def check_battle_end(self) -> None:
        if self.current_player() is None or self.current_enemy() is None:
            self.finish_battle()

    def finish_battle(self) -> None:
        pa = any(not p.fainted for p in self.selected_player_team)
        ea = any(not p.fainted for p in self.enemy_team)
        if pa and not ea:
            self.winner_text = "🏆  VICTORY!"
        elif ea and not pa:
            self.winner_text = "💀  DEFEAT..."
        else:
            self.winner_text = "⚔️  DRAW"
        self.add_log(self.winner_text)
        self.state = "result"
        self.restart_button.enabled = True

    def reset_game(self) -> None:
        for p in self.pokedex:
            p.reset()
        self.selected_player_team = []
        self.enemy_team = []
        self.player_index = 0
        self.enemy_index = 0
        self.log = ["Choose your team and start the duel!"]
        self.winner_text = ""
        self.state = "team_select"
        self.start_button.enabled = False
        self.restart_button.enabled = False
        self.particles.clear()
        self.flash_effects.clear()
        self.build_team_select_buttons()

    def active_move_buttons(self, pokemon: Pokemon) -> List[Button]:
        buttons = []
        for i, move in enumerate(pokemon.moves):
            btn = self.move_buttons[i]
            tc = TYPE_COLORS.get(move.move_type, PANEL_MID)
            b = Button(btn.rect, move.name, tc, text_color=BLACK,
                       icon=TYPE_EMOJI.get(move.move_type, ""))
            buttons.append(b)
        return buttons

    # ── Click handlers ────────────────────────────────────────────────────────
    def handle_click(self, pos):
        if self.state == "team_select":
            self._click_team_select(pos)
        elif self.state == "battle":
            self._click_battle(pos)
        elif self.state == "result":
            if self.restart_button.contains(pos):
                self.reset_game()

    def _click_team_select(self, pos):
        for btn in self.team_size_buttons:
            if btn.contains(pos):
                self.team_size = int(btn.text.split(": ")[1])
                self.selected_player_team = self.selected_player_team[:self.team_size]
                self.build_team_select_buttons()
                self.start_button.enabled = len(self.selected_player_team) == self.team_size
                return
        for i, btn in enumerate(self.roster_buttons):
            if btn.contains(pos):
                poke = self.pokedex[i]
                if poke in self.selected_player_team:
                    self.selected_player_team.remove(poke)
                    self.add_log(f"Removed {poke.name}")
                else:
                    if len(self.selected_player_team) >= self.team_size:
                        self.add_log("Team full! Remove one first.")
                        return
                    self.selected_player_team.append(poke)
                    self.add_log(f"Added {poke.name} ✓")
                self.start_button.enabled = len(self.selected_player_team) == self.team_size
                return
        if self.start_button.contains(pos) and len(self.selected_player_team) == self.team_size:
            self.begin_battle()

    def _click_battle(self, pos):
        player = self.current_player()
        if player is None:
            self.finish_battle()
            return
        for i, btn in enumerate(self.active_move_buttons(player)):
            if btn.contains(pos):
                self.resolve_turn(player.moves[i])
                return

    # ── Drawing primitives ────────────────────────────────────────────────────
    def draw_bg(self):
        """Dark starfield background with subtle gradient."""
        self.screen.fill(BG_DARK)
        # Subtle horizon glow
        glow = pygame.Surface((WIDTH, 300), pygame.SRCALPHA)
        for y in range(300):
            alpha = int(18 * (1 - y / 300))
            pygame.draw.line(glow, (60, 80, 160, alpha), (0, y), (WIDTH, y))
        self.screen.blit(glow, (0, 200))

        # Stars
        for sx, sy, bright in self.bg_stars:
            twinkle = 0.6 + 0.4 * math.sin(self.tick * 0.03 + sx)
            a = int(bright * twinkle * 200)
            s = pygame.Surface((2, 2), pygame.SRCALPHA)
            s.fill((220, 230, 255, a))
            self.screen.blit(s, (sx, sy))

    def draw_panel(self, rect, top_color=PANEL_DARK, bot_color=None,
                   border_color=BORDER_DIM, radius=16):
        bc = bot_color or lerp_color(top_color, BLACK, 0.3)
        draw_gradient_rect(self.screen, top_color, bc, rect, radius=radius)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=radius)

    def draw_header(self):
        # Title bar
        bar = pygame.Rect(0, 0, WIDTH, 90)
        draw_gradient_rect(self.screen, (18, 22, 50), (10, 12, 30), bar, radius=0)
        pygame.draw.line(self.screen, BORDER_GLOW, (0, 89), (WIDTH, 89), 2)

        title = self.title_font.render("POKÉMON TEAM DUEL", True, YELLOW_VIVID)
        sub   = self.small_font.render("Select your team  ·  Choose moves  ·  Defeat the enemy bot", True, GRAY_MID)
        self.screen.blit(title, (40, 16))
        self.screen.blit(sub,   (42, 58))

        # Decorative accent line
        pygame.draw.line(self.screen, lerp_color(YELLOW_VIVID, ORANGE_VIVID, 0.5),
                         (40, 52), (40 + title.get_width(), 52), 2)

    def draw_pokemon_card(self, pokemon: Pokemon, rect: pygame.Rect,
                          show_moves=False, label_text=""):
        tc = TYPE_COLORS.get(pokemon.p_type, GRAY_MID)
        dark_tc = lerp_color(tc, BLACK, 0.55)
        mid_tc  = lerp_color(tc, BLACK, 0.35)

        # Drop shadow
        shadow = rect.move(4, 5)
        sh = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 90))
        pygame.draw.rect(sh, (0,0,0,90), sh.get_rect(), border_radius=18)
        self.screen.blit(sh, shadow)

        # Card body
        draw_gradient_rect(self.screen, mid_tc, dark_tc, rect, radius=18)
        pygame.draw.rect(self.screen, lerp_color(tc, WHITE, 0.35),
                         rect, 2, border_radius=18)

        # Inner content region
        inner = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, rect.height - 16)
        inner_surf = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        inner_surf.fill((0, 0, 0, 40))
        self.screen.blit(inner_surf, inner)

        # Pokémon name
        name_surf = self.header_font.render(pokemon.name, True, WHITE)
        self.screen.blit(name_surf, (rect.x + 16, rect.y + 14))

        # Type badge
        draw_type_badge(self.screen, pokemon.p_type,
                        rect.x + 16, rect.y + 44, self.badge_font)

        # HP text
        hp_ratio = max(0, pokemon.hp) / pokemon.max_hp
        hp_color = GREEN_VIVID if hp_ratio > 0.5 else ORANGE_VIVID if hp_ratio > 0.2 else RED_VIVID
        hp_surf = self.small_font.render(f"HP  {pokemon.hp} / {pokemon.max_hp}", True, hp_color)
        self.screen.blit(hp_surf, (rect.right - hp_surf.get_width() - 16, rect.y + 14))

        # HP bar
        bar_y = rect.y + rect.height - 28
        draw_hp_bar(self.screen, rect.x + 16, bar_y, rect.width - 32, 14, hp_ratio)

        # Stats row
        stats = self.tiny_font.render(
            f"ATK {pokemon.attack}  DEF {pokemon.defense}  SPD {pokemon.speed}",
            True, lerp_color(WHITE, BLACK, 0.25)
        )
        self.screen.blit(stats, (rect.x + 16, rect.y + 68))

        if show_moves:
            moves_y = rect.y + 96
            for i, mv in enumerate(pokemon.moves[:4]):
                me = TYPE_EMOJI.get(mv.move_type, "")
                tc2 = TYPE_COLORS.get(mv.move_type, GRAY_MID)
                mt = self.tiny_font.render(f"{me} {mv.name}", True,
                                           lerp_color(tc2, WHITE, 0.4))
                self.screen.blit(mt, (rect.x + 16, moves_y + i * 18))

        if label_text:
            lt = self.badge_font.render(label_text, True, lerp_color(tc, WHITE, 0.7))
            self.screen.blit(lt, (rect.x, rect.y - 20))

    def draw_log(self):
        log_rect = pygame.Rect(40, 530, 1020, 108)
        self.draw_panel(log_rect, top_color=(16, 20, 44), bot_color=(10, 12, 28),
                        border_color=BORDER_DIM)

        lbl = self.badge_font.render("BATTLE LOG", True, GOLD)
        self.screen.blit(lbl, (log_rect.x + 16, log_rect.y + 10))
        pygame.draw.line(self.screen, BORDER_DIM,
                         (log_rect.x + 16, log_rect.y + 28),
                         (log_rect.right - 16, log_rect.y + 28), 1)

        for i, line in enumerate(self.log[-5:]):
            age = len(self.log[-5:]) - 1 - i
            alpha_t = 1.0 - age * 0.18
            color = lerp_color(OFF_WHITE, GRAY_DIM, 1 - alpha_t)
            t = self.log_font.render(line, True, color)
            self.screen.blit(t, (log_rect.x + 16, log_rect.y + 34 + i * 16))

    # ── Screen draws ──────────────────────────────────────────────────────────
    def draw_team_select(self):
        self.draw_header()

        # Left panel: roster
        left = pygame.Rect(30, 108, 756, 408)
        self.draw_panel(left, PANEL_DARK, border_color=BORDER_DIM)
        lbl = self.header_font.render("CHOOSE YOUR POKÉMON", True, YELLOW_VIVID)
        self.screen.blit(lbl, (50, 118))

        mouse_pos = pygame.mouse.get_pos()
        for i, (btn, poke) in enumerate(zip(self.roster_buttons, self.pokedex)):
            selected = poke in self.selected_player_team
            tc = TYPE_COLORS[poke.p_type]

            # Highlight border for selected
            outer = btn.rect.inflate(6, 6)
            if selected:
                pygame.draw.rect(self.screen, GREEN_VIVID, outer, 3, border_radius=20)
            else:
                pygame.draw.rect(self.screen, BORDER_DIM, outer, 2, border_radius=20)

            top_c = lerp_color(tc, WHITE, 0.1) if not selected else lerp_color(GREEN_VIVID, WHITE, 0.1)
            bot_c = lerp_color(tc, BLACK, 0.4) if not selected else lerp_color(GREEN_DARK, BLACK, 0.3)
            draw_gradient_rect(self.screen, top_c, bot_c, btn.rect, radius=16)

            # Check mark
            if selected:
                ck = self.header_font.render("✓", True, WHITE)
                self.screen.blit(ck, (btn.rect.right - 28, btn.rect.y + 6))

            name_s = self.body_font.render(poke.name, True, WHITE)
            self.screen.blit(name_s, (btn.rect.x + 14, btn.rect.y + 8))
            draw_type_badge(self.screen, poke.p_type, btn.rect.x + 14,
                            btn.rect.y + 38, self.badge_font)
            stats_s = self.tiny_font.render(
                f"HP {poke.max_hp}  ATK {poke.attack}  SPD {poke.speed}",
                True, lerp_color(WHITE, BLACK, 0.2)
            )
            self.screen.blit(stats_s, (btn.rect.x + 14, btn.rect.y + 64))

        # Right panel: team config
        right = pygame.Rect(800, 108, 262, 408)
        self.draw_panel(right, PANEL_DARK, border_color=BORDER_DIM)
        ts_lbl = self.header_font.render("TEAM SIZE", True, YELLOW_VIVID)
        self.screen.blit(ts_lbl, (820, 120))

        for btn in self.team_size_buttons:
            size = int(btn.text.split(": ")[1])
            btn.fill = (40, 160, 80) if size == self.team_size else (40, 70, 140)
            btn.draw(self.screen, self.small_font,
                     hovered=btn.rect.collidepoint(pygame.mouse.get_pos()))

        # Selected team list
        sel_lbl = self.header_font.render(
            f"SELECTED  {len(self.selected_player_team)}/{self.team_size}", True, OFF_WHITE)
        self.screen.blit(sel_lbl, (820, 380))
        for i, p in enumerate(self.selected_player_team):
            tc = TYPE_COLORS[p.p_type]
            dot = self.body_font.render(f"• {p.name}", True, lerp_color(tc, WHITE, 0.5))
            self.screen.blit(dot, (826, 410 + i * 28))

        # Start button
        self.start_button.enabled = len(self.selected_player_team) == self.team_size
        self.start_button.draw(self.screen, self.header_font,
                               hovered=self.start_button.rect.collidepoint(pygame.mouse.get_pos()))

        hint = self.tiny_font.render("Click to select, then press Start Battle", True, GRAY_DIM)
        self.screen.blit(hint, (820, 718))

        self.draw_log()

    def draw_battle(self):
        self.draw_header()

        # Battlefield background
        bf = pygame.Rect(30, 108, 1040, 340)
        draw_gradient_rect(self.screen, (16, 22, 52), (24, 18, 44), bf, radius=18)
        pygame.draw.rect(self.screen, BORDER_DIM, bf, 2, border_radius=18)

        # Ground line
        pygame.draw.line(self.screen, lerp_color(BORDER_DIM, WHITE, 0.1),
                         (bf.x + 30, bf.y + bf.height - 60),
                         (bf.right - 30, bf.y + bf.height - 60), 1)

        player  = self.current_player()
        enemy   = self.current_enemy()

        if enemy:
            enemy_rect = pygame.Rect(628, 120, 400, 200)
            self.draw_pokemon_card(enemy, enemy_rect, show_moves=False,
                                   label_text="⚠  ENEMY")

        if player:
            player_rect = pygame.Rect(62, 282, 400, 200)
            self.draw_pokemon_card(player, player_rect, show_moves=False,
                                   label_text="YOU ▶")

            # VS label
            vs = self.big_font.render("VS", True, (255, 255, 255, 120))
            vs_a = pygame.Surface(vs.get_size(), pygame.SRCALPHA)
            vs_a.blit(vs, (0, 0))
            vs_a.set_alpha(60)
            self.screen.blit(vs_a, (490, 220))

            # Move buttons
            moves_panel = pygame.Rect(30, 496, 710, 120)
            self.draw_panel(moves_panel, PANEL_DARK, border_color=BORDER_DIM)
            ml = self.badge_font.render("SELECT MOVE", True, GOLD)
            self.screen.blit(ml, (50, 504))

            mouse_pos = pygame.mouse.get_pos()
            move_btns = self.active_move_buttons(player)
            for i, btn in enumerate(move_btns):
                btn.draw(self.screen, self.small_font,
                         hovered=btn.rect.collidepoint(mouse_pos))
                # Power label
                mv = player.moves[i]
                pw = self.tiny_font.render(f"PWR {mv.power}", True,
                                           lerp_color(WHITE, BLACK, 0.35))
                self.screen.blit(pw, (btn.rect.x + 6, btn.rect.y + 38))

        # Team status panel
        status = pygame.Rect(752, 496, 318, 120)
        self.draw_panel(status, PANEL_DARK, border_color=BORDER_DIM)
        yl = self.badge_font.render("TEAMS", True, GOLD)
        self.screen.blit(yl, (772, 504))

        # Player team dots
        sx = 762
        for j, p in enumerate(self.selected_player_team):
            c = GREEN_VIVID if not p.fainted else RED_VIVID
            pygame.draw.circle(self.screen, c, (sx + j * 22, 536), 8)
            pygame.draw.circle(self.screen, lerp_color(c, WHITE, 0.3),
                               (sx + j * 22, 536), 8, 2)
            pn = self.tiny_font.render(p.name[:4], True, lerp_color(c, WHITE, 0.4))
            self.screen.blit(pn, (sx + j * 22 - pn.get_width() // 2, 548))

        # Enemy team dots
        ex = 762
        for j, p in enumerate(self.enemy_team):
            c = RED_VIVID if not p.fainted else GRAY_DIM
            pygame.draw.circle(self.screen, c, (ex + j * 22, 580), 8)
            pygame.draw.circle(self.screen, lerp_color(c, WHITE, 0.3),
                               (ex + j * 22, 580), 8, 2)
            pn = self.tiny_font.render(p.name[:4], True, lerp_color(c, WHITE, 0.4))
            self.screen.blit(pn, (ex + j * 22 - pn.get_width() // 2, 592))

        pu = self.tiny_font.render("YOUR TEAM", True, GRAY_MID)
        en = self.tiny_font.render("ENEMY TEAM", True, GRAY_MID)
        self.screen.blit(pu, (920, 524))
        self.screen.blit(en, (916, 568))

        # Particles & flashes
        for p in self.particles:
            p.draw(self.screen)
        for f in self.flash_effects:
            f.draw(self.screen, self.header_font)

        self.draw_log()

    def draw_result(self):
        self.draw_header()

        # Centre card
        card = pygame.Rect(100, 130, 900, 370)
        tc_win = GREEN_VIVID if "VICTORY" in self.winner_text else RED_VIVID
        self.draw_panel(card, top_color=lerp_color(tc_win, BLACK, 0.65),
                        bot_color=lerp_color(tc_win, BLACK, 0.8),
                        border_color=tc_win)

        # Glow ring
        glow_r = card.inflate(12, 12)
        pygame.draw.rect(self.screen, lerp_color(tc_win, BLACK, 0.4),
                         glow_r, 4, border_radius=22)

        wt = self.big_font.render(self.winner_text, True, tc_win)
        self.screen.blit(wt, wt.get_rect(center=(card.centerx, card.y + 90)))

        # Divider
        pygame.draw.line(self.screen, BORDER_DIM,
                         (card.x + 60, card.y + 140),
                         (card.right - 60, card.y + 140), 1)

        p_alive = sum(not p.fainted for p in self.selected_player_team)
        e_alive  = sum(not p.fainted for p in self.enemy_team)
        lines = [
            f"Your remaining Pokémon : {p_alive} / {len(self.selected_player_team)}",
            f"Enemy remaining Pokémon : {e_alive} / {len(self.enemy_team)}",
        ]
        for i, ln in enumerate(lines):
            s = self.body_font.render(ln, True, OFF_WHITE)
            self.screen.blit(s, (card.x + 80, card.y + 165 + i * 42))

        # Team summary row
        y_row = card.y + 270
        for j, p in enumerate(self.selected_player_team):
            px = card.x + 80 + j * 140
            mini = pygame.Rect(px, y_row, 128, 62)
            tc2 = TYPE_COLORS[p.p_type]
            draw_gradient_rect(self.screen,
                               lerp_color(tc2, BLACK, 0.4),
                               lerp_color(tc2, BLACK, 0.65), mini, radius=10)
            pn = self.small_font.render(p.name, True, WHITE)
            st = self.tiny_font.render("FNT" if p.fainted else f"HP {p.hp}",
                                       True, RED_VIVID if p.fainted else GREEN_VIVID)
            self.screen.blit(pn, (px + 8, y_row + 6))
            self.screen.blit(st, (px + 8, y_row + 34))

        self.restart_button.draw(self.screen, self.header_font,
                                 hovered=self.restart_button.rect.collidepoint(
                                     pygame.mouse.get_pos()))
        self.draw_log()

    # ── Main draw & run ───────────────────────────────────────────────────────
    def draw(self):
        self.draw_bg()
        if self.state == "team_select":
            self.draw_team_select()
        elif self.state == "battle":
            self.draw_battle()
        else:
            self.draw_result()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            self.tick += 1
            self.update_particles()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            self.draw()
        pygame.quit()
        sys.exit()


def main():
    DuelGame().run()


if __name__ == "__main__":
    main()