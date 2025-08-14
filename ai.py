import chess
import math
import random
from typing import Optional, Tuple, List

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

PAWN_TABLE = [
      0,  0,  0,  0,  0,  0,  0,  0,
     50, 50, 50, 50, 50, 50, 50, 50,
     10, 10, 20, 30, 30, 20, 10, 10,
      5,  5, 10, 25, 25, 10,  5,  5,
      0,  0,  0, 20, 20,  0,  0,  0,
      5, -5,-10,  0,  0,-10, -5,  5,
      5, 10, 10,-20,-20, 10, 10,  5,
      0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_TABLE = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]
TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}

def evaluate(board: chess.Board) -> int:
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition():
        return 0
    score = 0
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if not p:
            continue
        val = PIECE_VALUES[p.piece_type]
        pst = TABLES[p.piece_type][sq if p.color == chess.WHITE else chess.square_mirror(sq)]
        score += (val + pst) if p.color == chess.WHITE else -(val + pst)
    return score

class ChessAI:
    def __init__(self, max_depth: int = 3, randomness: float = 0.0):
        self.max_depth = max_depth
        self.rand = randomness

    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        best = -math.inf
        best_moves: List[chess.Move] = []
        for mv in self._ordered_moves(board):
            board.push(mv)
            score = -self._alphabeta(board, self.max_depth - 1, -math.inf, math.inf)
            board.pop()
            if score > best:
                best = score
                best_moves = [mv]
            elif score == best:
                best_moves.append(mv)
        if not best_moves:
            return None
        if self.rand > 0 and len(best_moves) > 1 and random.random() < self.rand:
            return random.choice(best_moves)
        return random.choice(best_moves)

    def top_moves(self, board: chess.Board, k: int = 5) -> List[Tuple[chess.Move, int]]:
        out = []
        for mv in self._ordered_moves(board):
            board.push(mv)
            score = -self._alphabeta(board, self.max_depth - 1, -math.inf, math.inf)
            board.pop()
            out.append((mv, score))
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:k]

    def _alphabeta(self, board: chess.Board, depth: int, alpha: float, beta: float) -> int:
        if depth == 0 or board.is_game_over():
            return evaluate(board)
        val = -math.inf
        for mv in self._ordered_moves(board):
            board.push(mv)
            score = -self._alphabeta(board, depth - 1, -beta, -alpha)
            board.pop()
            if score > val:
                val = score
            if val > alpha:
                alpha = val
            if alpha >= beta:
                break
        return val if val != -math.inf else evaluate(board)

    def _ordered_moves(self, board: chess.Board):
        def mv_score(m: chess.Move):
            s = 0
            if board.is_capture(m): s += 1000
            if board.gives_check(m): s += 50
            if m.promotion: s += 900
            return s
        mv = list(board.legal_moves)
        mv.sort(key=mv_score, reverse=True)
        return mv
