import chess
from typing import List, Tuple
from ai import ChessAI

class MoveHelper:
    def __init__(self, ai: ChessAI):
        self.ai = ai

    def suggestions(self, board: chess.Board, k: int = 3) -> List[Tuple[chess.Move, int]]:
        return self.ai.top_moves(board, k)