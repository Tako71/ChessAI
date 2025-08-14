# ui.py
import pygame
import chess
from typing import Tuple, Optional, List, Dict

# ----- поле и панель -----
BOARD_SIZE = 640
MARGIN = 56
WIDTH = BOARD_SIZE + MARGIN * 2
HEIGHT = BOARD_SIZE + MARGIN * 2
PANEL_H = 170
WIN_W, WIN_H = WIDTH, HEIGHT + PANEL_H
SQ = BOARD_SIZE // 8

LIGHT = (240, 217, 181)
DARK  = (181, 136,  99)
EDGE  = (92, 64, 51)
HINT  = (135, 206, 250)
MOVE  = (246, 246, 105)
SEL   = (106, 246, 105)
TEXT  = (30, 30, 30)
PANEL = (247, 247, 247)
LABEL = (60, 60, 60)

# ----- рендер фигур -----
SPRITE_MODE = True  # если False — векторный рендер (фолбэк)
PIECE_THEME_DIR = "assets/pieces/merida"  # папка со спрайтами PNG
SPRITE_PAD = 0.10  # доля от клетки как отступ вокруг спрайта

# палитра для векторного фолбэка (контрастные силуэты)
W_FILL, W_OUT = (250, 250, 250), (55, 55, 55)
B_FILL, B_OUT = (28, 28, 28), (230, 230, 230)

class UI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Шахматы — ИИ")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.small  = self._pick_font(18)
        self.medium = self._pick_font(24)
        self.large  = self._pick_font(44)
        self.button_rect = pygame.Rect(WIDTH - 210 - 20, HEIGHT + 18, 210, 42)

        # кэш спрайтов (или None, если папки нет)
        self._sprite_cache: Dict[str, pygame.Surface] = {}
        self._try_load_sprites()

    # -------------------- шрифты --------------------
    def _pick_font(self, size: int) -> pygame.font.Font:
        for fam in ["Inter", "Montserrat", "Nunito", "DejaVu Sans", None]:
            try:
                path = pygame.font.match_font(fam) if fam else None
                f = pygame.font.Font(path, size)
                if f: return f
            except Exception:
                pass
        return pygame.font.SysFont(None, size)

    # -------------------- ориентация / клетки --------------------
    @staticmethod
    def _file_rank_from_square(square: int, white_bottom: bool) -> Tuple[int, int]:
        if white_bottom:   return square % 8, 7 - (square // 8)
        else:              return 7 - (square % 8), square // 8

    @staticmethod
    def _square_from_file_rank(file_: int, rank_: int, white_bottom: bool) -> int:
        if white_bottom:   return (7 - rank_) * 8 + file_
        else:              return rank_ * 8 + (7 - file_)

    @staticmethod
    def _cell_rect(file_: int, rank_: int) -> pygame.Rect:
        return pygame.Rect(MARGIN + file_ * SQ, MARGIN + rank_ * SQ, SQ, SQ)

    # -------------------- главный рендер --------------------
    def draw_board(self, board: chess.Board, selected: Optional[int], legal_sqs: List[int],
                   hints: List[int], last_move: Optional[chess.Move], white_bottom: bool):
        # поле
        for r in range(8):
            for f in range(8):
                rect = self._cell_rect(f, r)
                pygame.draw.rect(self.screen, LIGHT if (r + f) % 2 == 0 else DARK, rect)
        pygame.draw.rect(self.screen, EDGE, pygame.Rect(MARGIN, MARGIN, BOARD_SIZE, BOARD_SIZE), 2)

        # подсветки
        if last_move:
            for sq in (last_move.from_square, last_move.to_square):
                f, r = self._file_rank_from_square(sq, white_bottom)
                pygame.draw.rect(self.screen, MOVE, self._cell_rect(f, r), 6, border_radius=10)
        if selected is not None:
            f, r = self._file_rank_from_square(selected, white_bottom)
            pygame.draw.rect(self.screen, SEL, self._cell_rect(f, r), 4, border_radius=10)
        for sq in legal_sqs:
            f, r = self._file_rank_from_square(sq, white_bottom)
            pygame.draw.circle(self.screen, MOVE, self._cell_rect(f, r).center, 9)
        for sq in hints:
            f, r = self._file_rank_from_square(sq, white_bottom)
            pygame.draw.circle(self.screen, HINT, self._cell_rect(f, r).center, 8, 2)

        # фигуры
        for sq in chess.SQUARES:
            p = board.piece_at(sq)
            if not p: continue
            f, r = self._file_rank_from_square(sq, white_bottom)
            self._draw_piece(self._cell_rect(f, r), p)

        self._draw_coords(white_bottom)

    # -------------------- разметка координат --------------------
    def _draw_coords(self, white_bottom: bool):
        files = ['A','B','C','D','E','F','G','H']
        ranks = ['8','7','6','5','4','3','2','1']
        if not white_bottom:
            files.reverse()
            ranks.reverse()
        for i, ch in enumerate(files):
            s_top = self.small.render(ch, True, LABEL)
            s_bot = self.small.render(ch, True, LABEL)
            x = MARGIN + i*SQ + SQ//2 - s_top.get_width()//2
            self.screen.blit(s_top, (x, MARGIN - s_top.get_height() - 6))
            self.screen.blit(s_bot, (x, MARGIN + BOARD_SIZE + 6))
        for i, ch in enumerate(ranks):
            s_l = self.small.render(ch, True, LABEL)
            s_r = self.small.render(ch, True, LABEL)
            y = MARGIN + i*SQ + SQ//2 - s_l.get_height()//2
            self.screen.blit(s_l, (MARGIN - s_l.get_width() - 8, y))
            self.screen.blit(s_r, (MARGIN + BOARD_SIZE + 8, y))

    # -------------------- спрайты: загрузка и рендер --------------------
    def _try_load_sprites(self):
        """Пробует загрузить PNG спрайты. Если не найдены — остаёмся в векторном режиме."""
        if not SPRITE_MODE:
            return
        import os
        if not os.path.isdir(PIECE_THEME_DIR):
            return
        names = "PNBRQK"
        for color, prefix in ((chess.WHITE, "w"), (chess.BLACK, "b")):
            for ch in names:
                filename = os.path.join(PIECE_THEME_DIR, f"{prefix}{ch}.png")
                try:
                    surf = pygame.image.load(filename).convert_alpha()
                except Exception:
                    self._sprite_cache.clear()
                    return  # что-то не так — выключаем спрайты
                key = f"{prefix}{ch}"
                self._sprite_cache[key] = surf

    def _get_piece_sprite(self, piece: chess.Piece, cell_rect: pygame.Rect) -> Optional[pygame.Surface]:
        if not self._sprite_cache:
            return None
        prefix = "w" if piece.color else "b"
        ch = {chess.PAWN:"P", chess.KNIGHT:"N", chess.BISHOP:"B", chess.ROOK:"R", chess.QUEEN:"Q", chess.KING:"K"}[piece.piece_type]
        key = f"{prefix}{ch}"
        src = self._sprite_cache.get(key)
        if not src:
            return None
        # подготавливаем к размеру клетки (с паддингом)
        target_w = int(cell_rect.width * (1.0 - SPRITE_PAD * 2))
        target_h = int(cell_rect.height * (1.0 - SPRITE_PAD * 2))
        # сохраняем пропорции
        ratio = min(target_w / src.get_width(), target_h / src.get_height())
        size = (max(1, int(src.get_width() * ratio)), max(1, int(src.get_height() * ratio)))
        return pygame.transform.smoothscale(src, size)

    # -------------------- фигуры: спрайты или векторный фолбэк --------------------
    def _draw_piece(self, rect: pygame.Rect, piece: chess.Piece):
        spr = self._get_piece_sprite(piece, rect)
        if spr:
            dest = spr.get_rect(center=rect.center)
            self.screen.blit(spr, dest)
            return
        # векторный фолбэк с суперсэмплингом (3x, затем даунскейл)
        hi = pygame.Surface((rect.width*3, rect.height*3), pygame.SRCALPHA)
        cx, cy = hi.get_width()//2, hi.get_height()//2
        s = rect.width * 0.45 * 3
        fill, out = (W_FILL, W_OUT) if piece.color else (B_FILL, B_OUT)

        def circle(x, y, r, w=4):
            pygame.draw.circle(hi, fill, (x, y), int(r))
            pygame.draw.circle(hi, out,  (x, y), int(r), w)

        def rects(x, y, w_, h_, radius=8, lw=4):
            rr = pygame.Rect(int(x - w_//2), int(y - h_//2), int(w_), int(h_))
            pygame.draw.rect(hi, fill, rr, border_radius=radius)
            pygame.draw.rect(hi, out,  rr, width=lw, border_radius=radius)

        t = piece.piece_type
        if t == chess.PAWN:
            circle(cx, int(cy - s*0.35), int(s*0.24))
            rects(cx, cy, int(s*0.72), int(s*0.48), radius=14)
            rects(cx, int(cy + s*0.46), int(s*0.9), int(s*0.16), radius=10)
        elif t == chess.ROOK:
            rects(cx, int(cy + s*0.06), int(s*0.86), int(s*0.74), radius=12)
            cren_w = int(s*0.18); gap = int(s*0.02)
            for i in (-1, 0, 1, 2):
                rects(int(cx + i*(cren_w+gap) - cren_w//2), int(cy - s*0.42), cren_w, int(s*0.18), radius=6)
            rects(cx, int(cy + s*0.52), int(s*0.98), int(s*0.14), radius=10)
        elif t == chess.KNIGHT:
            poly = [
                (cx - int(s*0.50), cy + int(s*0.48)),
                (cx - int(s*0.10), cy + int(s*0.10)),
                (cx - int(s*0.04), cy - int(s*0.18)),
                (cx + int(s*0.22),  cy - int(s*0.44)),
                (cx + int(s*0.44), cy - int(s*0.12)),
                (cx + int(s*0.08), cy + int(s*0.06)),
                (cx + int(s*0.28),  cy + int(s*0.46)),
            ]
            pygame.draw.polygon(hi, fill, poly)
            pygame.draw.polygon(hi, out,  poly, 6)
        elif t == chess.BISHOP:
            ellipse = pygame.Rect(cx-int(s*0.34), cy-int(s*0.40), int(s*0.68), int(s*0.78))
            pygame.draw.ellipse(hi, fill, ellipse)
            pygame.draw.ellipse(hi, out,  ellipse, 6)
            pygame.draw.line(hi, (255,255,255) if piece.color else (220,220,220),
                             (cx - int(s*0.20), cy - int(s*0.06)),
                             (cx + int(s*0.20), cy + int(s*0.18)), 7)
            rects(cx, int(cy + s*0.52), int(s*0.95), int(s*0.14), radius=10)
        elif t == chess.QUEEN:
            rects(cx, int(cy + s*0.52), int(s*1.00), int(s*0.14), radius=10)
            spikes = [-int(s*0.36), -int(s*0.18), 0, int(s*0.18), int(s*0.36)]
            for dx in spikes:
                crown = [(cx+dx-int(s*0.12), cy),
                         (cx+dx, cy-int(s*0.46)),
                         (cx+dx+int(s*0.12), cy)]
                pygame.draw.polygon(hi, fill, crown)
                pygame.draw.polygon(hi, out,  crown, 6)
        elif t == chess.KING:
            rects(cx, cy, int(s*0.64), int(s*0.70), radius=12)
            rects(cx, int(cy + s*0.52), int(s*1.02), int(s*0.14), radius=10)
            pygame.draw.line(hi, out, (cx - int(s*0.30), cy - int(s*0.50)),
                             (cx + int(s*0.30), cy - int(s*0.50)), 8)
            pygame.draw.line(hi, out, (cx, cy - int(s*0.70)),
                             (cx, cy - int(s*0.28)), 8)

        # даунскейл без «пилы»
        lo = pygame.transform.smoothscale(hi, (rect.width, rect.height))
        self.screen.blit(lo, rect)
    # -------------------- панель --------------------
    def draw_panel(self, text_main: str, text_sub: str, button_on: bool, tips: List[str]):
        pygame.draw.rect(self.screen, PANEL, pygame.Rect(0, HEIGHT, WIN_W, PANEL_H))
        label = self.medium.render(text_main, True, TEXT)
        self.screen.blit(label, (MARGIN, HEIGHT + 10))
        hint = self.small.render(text_sub, True, TEXT)
        self.screen.blit(hint, (MARGIN, HEIGHT + 40))

        # кнопка справа
        br = self.button_rect
        shadow = br.move(0, 2)
        srf = pygame.Surface((br.width+8, br.height+8), pygame.SRCALPHA)
        pygame.draw.rect(srf, (0,0,0,60), pygame.Rect(4, 2, br.width, br.height), border_radius=18)
        self.screen.blit(srf, (br.x - 4, br.y - 2))
        pygame.draw.rect(self.screen, (210,235,255) if button_on else (235,235,235), br, border_radius=18)
        pygame.draw.rect(self.screen, (80,120,180), br, 2, border_radius=18)
        t = self.medium.render('Подсказки: ВКЛ' if button_on else 'Подсказки: ВЫКЛ', True, (20,40,80))
        self.screen.blit(t, (br.centerx - t.get_width() // 2, br.centery - t.get_height() // 2))

        if tips:
            x = br.x
            y = br.bottom + 12
            for s in tips:
                self.screen.blit(self.small.render(s, True, TEXT), (x, y))
                y += 20

    # -------------------- меню --------------------
    def prompt_menu(self) -> Tuple[str, int, float]:
        clock = pygame.time.Clock()
        choice = 0
        opts = [("Легко", 2, 0.2), ("Средне", 3, 0.1), ("Сложно", 4, 0.0)]
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); raise SystemExit
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE: pygame.quit(); raise SystemExit
                    if e.key == pygame.K_UP: choice = (choice - 1) % len(opts)
                    if e.key == pygame.K_DOWN: choice = (choice + 1) % len(opts)
                    if e.key == pygame.K_RETURN: name, d, r = opts[choice]; return name, d, r
            self.screen.fill((25,25,25))
            title = self.large.render("Выберите сложность", True, (230,230,230))
            self.screen.blit(title, (WIN_W // 2 - title.get_width() // 2, 80))
            for i, (name, _, _) in enumerate(opts):
                col = (255,255,255) if i == choice else (160,160,160)
                txt = self.large.render(name, True, col)
                self.screen.blit(txt, (WIN_W // 2 - txt.get_width() // 2, 160 + i*60))
            helper = self.small.render("↑/↓ — выбор, Enter — подтвердить, Esc — выход", True, (200,200,200))
            self.screen.blit(helper, (WIN_W // 2 - helper.get_width() // 2, HEIGHT - 80))
            pygame.display.flip(); clock.tick(60)

    def prompt_side(self) -> bool:
        clock = pygame.time.Clock()
        choice = 0
        opts = ["Белыми", "Чёрными"]
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); raise SystemExit
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE: pygame.quit(); raise SystemExit
                    if e.key == pygame.K_UP: choice = (choice - 1) % len(opts)
                    if e.key == pygame.K_DOWN: choice = (choice + 1) % len(opts)
                    if e.key == pygame.K_RETURN: return choice == 0
            self.screen.fill((25,25,25))
            title = self.large.render("Выберите сторону", True, (230,230,230))
            self.screen.blit(title, (WIN_W // 2 - title.get_width() // 2, 80))
            for i, name in enumerate(opts):
                col = (255,255,255) if i == choice else (160,160,160)
                txt = self.large.render(name, True, col)
                self.screen.blit(txt, (WIN_W // 2 - txt.get_width() // 2, 160 + i*60))
            helper = self.small.render("↑/↓ — выбор, Enter — подтвердить", True, (200,200,200))
            self.screen.blit(helper, (WIN_W // 2 - helper.get_width() // 2, HEIGHT - 80))
            pygame.display.flip(); clock.tick(60)

    def mouse_to_square(self, pos, white_bottom: bool) -> Optional[int]:
        x, y = pos
        if not (MARGIN <= x < MARGIN + BOARD_SIZE and MARGIN <= y < MARGIN + BOARD_SIZE):
            return None
        file_ = int((x - MARGIN) // SQ)
        rank_ = int((y - MARGIN) // SQ)
        return self._square_from_file_rank(file_, rank_, white_bottom)
