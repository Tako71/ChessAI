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
    -30,  5, 15, 20, 20, 15,  5,-30,
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
        piece = board.piece_at(sq)
        if not piece:
            continue
        val = PIECE_VALUES[piece.piece_type]
        pst = TABLES[piece.piece_type][sq if piece.color == chess.WHITE else chess.square_mirror(sq)]
        score += (val + pst) if piece.color == chess.WHITE else -(val + pst)
    return score

class ChessAI:
    def __init__(self, max_depth: int = 2, randomness: float = 0.0):
        self.max_depth = max_depth
        self.rand = randomness

    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        best_score = -math.inf
        best_moves: List[chess.Move] = []
        for move in self._ordered_moves(board):
            board.push(move)
            score = -self._alphabeta(board, self.max_depth - 1, -math.inf, math.inf)
            board.pop()
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        if not best_moves:
            return None
        if self.rand > 0 and random.random() < self.rand and len(best_moves) > 1:
            return random.choice(best_moves)
        return random.choice(best_moves)

    def top_moves(self, board: chess.Board, k: int = 3) -> List[Tuple[chess.Move, int]]:
        scored = []
        for move in self._ordered_moves(board):
            board.push(move)
            score = -self._alphabeta(board, self.max_depth - 1, -math.inf, math.inf)
            board.pop()
            scored.append((move, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def _alphabeta(self, board: chess.Board, depth: int, alpha: float, beta: float) -> int:
        if depth == 0 or board.is_game_over():
            return evaluate(board)
        value = -math.inf
        for move in self._ordered_moves(board):
            board.push(move)
            score = -self._alphabeta(board, depth - 1, -beta, -alpha)
            board.pop()
            if score > value:
                value = score
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break
        return value if value != -math.inf else evaluate(board)

    def _ordered_moves(self, board: chess.Board):
        def mv_score(m: chess.Move):
            s = 0
            if board.is_capture(m):
                s += 1000
            if board.gives_check(m):
                s += 50
            if m.promotion:
                s += 900
            return s
        moves = list(board.legal_moves)
        moves.sort(key=mv_score, reverse=True)
        return moves