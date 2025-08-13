import pygame
import chess
from typing import Tuple, Optional, List

WIDTH, HEIGHT = 640, 640
SQ = WIDTH // 8
BG_LIGHT = (240, 217, 181)
BG_DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
SELECT = (106, 246, 105)
HINT = (135, 206, 250)
TEXT = (30, 30, 30)
PANEL = (245, 245, 245)

# Цвета фигур (вдохновлено настольными наборами)
W_FILL = (243, 206, 173)
W_STROKE = (120, 70, 40)
B_FILL = (120, 66, 48)
B_STROKE = (255, 230, 210)
TOKEN_SHADOW = (0, 0, 0, 60)
TOKEN_BORDER = (60, 40, 30)

class UI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Шахматы — ИИ")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + 110))
        self.small = pygame.font.SysFont(None, 20)
        self.medium = pygame.font.SysFont(None, 24)

    def draw_board(self, board: chess.Board, selected: Optional[int], legal_sqs: List[int], hints: List[int], last_move: Optional[chess.Move]):
        for r in range(8):
            for f in range(8):
                rect = pygame.Rect(f*SQ, r*SQ, SQ, SQ)
                color = BG_LIGHT if (r+f) % 2 == 0 else BG_DARK
                pygame.draw.rect(self.screen, color, rect)
        if last_move:
            fs, ts = last_move.from_square, last_move.to_square
            for sq in (fs, ts):
                f, r = sq % 8, 7 - (sq // 8)
                pygame.draw.rect(self.screen, (255, 230, 140), pygame.Rect(f*SQ, r*SQ, SQ, SQ), 6, border_radius=10)
        if selected is not None:
            f, r = selected % 8, 7 - (selected // 8)
            pygame.draw.rect(self.screen, SELECT, pygame.Rect(f*SQ, r*SQ, SQ, SQ), 4, border_radius=10)
        for sq in legal_sqs:
            f, r = sq % 8, 7 - (sq // 8)
            pygame.draw.circle(self.screen, HIGHLIGHT, (f*SQ + SQ//2, r*SQ + SQ//2), 10)
        for sq in hints:
            f, r = sq % 8, 7 - (sq // 8)
            pygame.draw.circle(self.screen, HINT, (f*SQ + SQ//2, r*SQ + SQ//2), 8, 2)
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if not piece:
                continue
            f, r = sq % 8, 7 - (sq // 8)
            rect = pygame.Rect(f*SQ, r*SQ, SQ, SQ)
            self._draw_token_piece(rect, piece)

    def _draw_token_piece(self, rect: pygame.Rect, piece: chess.Piece):
        is_white = piece.color
        fill = W_FILL if is_white else B_FILL
        stroke = W_STROKE if is_white else B_STROKE
        # Токен с тенью
        token = rect.inflate(-SQ*0.24, -SQ*0.24)
        shadow = token.move(2, 2)
        srf = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
        pygame.draw.rect(srf, TOKEN_SHADOW, shadow, border_radius=12)
        pygame.draw.rect(srf, fill, token, border_radius=12)
        pygame.draw.rect(srf, TOKEN_BORDER, token, width=2, border_radius=12)
        self.screen.blit(srf, rect.topleft)
        # Иконка фигуры
        cx, cy = rect.centerx, rect.centery
        size = SQ * 0.42
        t = piece.piece_type
        if t == chess.PAWN:
            self._draw_pawn(cx, cy, size, stroke, is_white)
        elif t == chess.ROOK:
            self._draw_rook(cx, cy, size, stroke, is_white)
        elif t == chess.KNIGHT:
            self._draw_knight(cx, cy, size, stroke, is_white)
        elif t == chess.BISHOP:
            self._draw_bishop(cx, cy, size, stroke, is_white)
        elif t == chess.QUEEN:
            self._draw_queen(cx, cy, size, stroke, is_white)
        elif t == chess.KING:
            self._draw_king(cx, cy, size, stroke, is_white)

    # Ниже — простые «векторные» иконки на примитивах Pygame
    def _draw_pawn(self, cx, cy, s, color, white):
        head_r = int(s*0.22)
        body_w, body_h = int(s*0.55), int(s*0.45)
        base_w, base_h = int(s*0.7), int(s*0.16)
        pygame.draw.circle(self.screen, color, (cx, int(cy-s*0.25)), head_r, width=3)
        pygame.draw.ellipse(self.screen, color, pygame.Rect(cx-body_w//2, cy-body_h//2, body_w, body_h), width=3)
        pygame.draw.rect(self.screen, color, pygame.Rect(cx-base_w//2, int(cy+s*0.25), base_w, base_h), width=3, border_radius=4)

    def _draw_rook(self, cx, cy, s, color, white):
        w, h = int(s*0.65), int(s*0.55)
        x, y = cx - w//2, cy - h//2
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y+int(h*0.15), w, int(h*0.75)), width=3)
        cren = w//4
        for i in range(3):
            pygame.draw.rect(self.screen, color, pygame.Rect(x+cren*(i+0.25), y, cren//2, int(h*0.2)), width=3)
        pygame.draw.rect(self.screen, color, pygame.Rect(cx-int(w*0.45), int(cy+h*0.35), int(w*0.9), int(h*0.18)), width=3, border_radius=3)

    def _draw_knight(self, cx, cy, s, color, white):
        px = [
            (cx - int(s*0.45), cy + int(s*0.35)),
            (cx - int(s*0.15), cy + int(s*0.05)),
            (cx - int(s*0.05), cy - int(s*0.15)),
            (cx + int(s*0.2),  cy - int(s*0.35)),
            (cx + int(s*0.35), cy - int(s*0.15)),
            (cx + int(s*0.05), cy + int(s*0.1)),
            (cx + int(s*0.2),  cy + int(s*0.35)),
        ]
        pygame.draw.lines(self.screen, color, True, px, 3)
        pygame.draw.circle(self.screen, color, (cx + int(s*0.05), cy - int(s*0.22)), 3)

    def _draw_bishop(self, cx, cy, s, color, white):
        body_w, body_h = int(s*0.55), int(s*0.6)
        pygame.draw.ellipse(self.screen, color, pygame.Rect(cx-body_w//2, cy-body_h//2, body_w, body_h), width=3)
        pygame.draw.circle(self.screen, color, (cx, int(cy - s*0.42)), 4)
        pygame.draw.line(self.screen, color, (cx - int(s*0.15), cy - int(s*0.05)), (cx + int(s*0.15), cy + int(s*0.15)), 3)

    def _draw_queen(self, cx, cy, s, color, white):
        base_w, base_h = int(s*0.9), int(s*0.16)
        pygame.draw.rect(self.screen, color, pygame.Rect(cx-base_w//2, int(cy+s*0.35), base_w, base_h), width=3, border_radius=3)
        for dx in (-int(s*0.3), 0, int(s*0.3)):
            crown = [
                (cx + dx - int(s*0.12), cy),
                (cx + dx, cy - int(s*0.35)),
                (cx + dx + int(s*0.12), cy),
            ]
            pygame.draw.lines(self.screen, color, False, crown, 3)

    def _draw_king(self, cx, cy, s, color, white):
        body_w, body_h = int(s*0.5), int(s*0.55)
        pygame.draw.rect(self.screen, color, pygame.Rect(cx-body_w//2, cy-body_h//2, body_w, body_h), width=3)
        pygame.draw.line(self.screen, color, (cx - int(s*0.28), cy - int(s*0.35)), (cx + int(s*0.28), cy - int(s*0.35)), 3)
        pygame.draw.line(self.screen, color, (cx, cy - int(s*0.55)), (cx, cy - int(s*0.2)), 3)
        pygame.draw.circle(self.screen, color, (cx, int(cy - s*0.6)), 4)

    def draw_panel(self, text_main: str, text_sub: str):
        pygame.draw.rect(self.screen, PANEL, pygame.Rect(0, HEIGHT, WIDTH, 110))
        label = self.medium.render(text_main, True, TEXT)
        self.screen.blit(label, (10, HEIGHT + 8))
        hint = self.small.render(text_sub, True, TEXT)
        self.screen.blit(hint, (10, HEIGHT + 45))

    def prompt_menu(self) -> Tuple[str, int, float]:
        clock = pygame.time.Clock()
        choice = 0
        options = [
            ("Легко", 2, 0.2),
            ("Средне", 3, 0.1),
            ("Сложно", 4, 0.0),
        ]
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit(); raise SystemExit
                    if e.key == pygame.K_UP:
                        choice = (choice - 1) % len(options)
                    if e.key == pygame.K_DOWN:
                        choice = (choice + 1) % len(options)
                    if e.key == pygame.K_RETURN:
                        name, depth, rand = options[choice]
                        return name, depth, rand
            self.screen.fill((25, 25, 25))
            title = pygame.font.SysFont(None, 44).render("Выберите сложность", True, (230,230,230))
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
            for i, (name, _, _) in enumerate(options):
                color = (255,255,255) if i == choice else (160,160,160)
                txt = pygame.font.SysFont(None, 44).render(name, True, color)
                self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 160 + i*60))
            hint = self.small.render("↑/↓ — выбор, Enter — подтвердить, Esc — выход", True, (200,200,200))
            self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-80))
            pygame.display.flip(); clock.tick(60)

    @staticmethod
    def mouse_to_square(pos) -> Optional[int]:
        x, y = pos
        if y >= HEIGHT:
            return None
        file = x // SQ
        rank = 7 - (y // SQ)
        return rank * 8 + file