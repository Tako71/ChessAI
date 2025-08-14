import chess
from typing import List, Tuple
from ai import ChessAI

PIECE_RU = {
    chess.PAWN: "пешкой",
    chess.KNIGHT: "конём",
    chess.BISHOP: "слоном",
    chess.ROOK: "ладьёй",
    chess.QUEEN: "ферзём",
    chess.KING: "королём",
}

def score_to_str(score: int) -> str:
    if abs(score) >= 90000:
        return "#"
    return f"{score:+d}"

def top_tips(board: chess.Board, ai: ChessAI, k: int = 5) -> List[str]:
    items: List[Tuple[chess.Move, int]] = ai.top_moves(board, k)
    tips: List[str] = []
    for i, (mv, sc) in enumerate(items, 1):
        piece = board.piece_at(mv.from_square)
        name = PIECE_RU.get(piece.piece_type, "фигурой") if piece else "фигурой"
        dest = chess.square_name(mv.to_square)
        tips.append(f"{i}) Лучше сходить {name} на {dest}  {score_to_str(sc)}")
    return tips
