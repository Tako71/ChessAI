import pygame
import chess
from ai import ChessAI
from move_helper import MoveHelper
from ui import UI
from tips import top_tips

def main():
    ui = UI()
    label, depth, rand = ui.prompt_menu()
    play_white = ui.prompt_side()

    ai = ChessAI(max_depth=depth, randomness=rand)
    helper = MoveHelper(ai)

    white_bottom = play_white
    board = chess.Board()
    selected = None
    show_hints = False
    legal_targets = []
    last_move = None
    clock = pygame.time.Clock()

    if not play_white:
        ai_move = ai.choose_move(board)
        if ai_move:
            board.push(ai_move)
            last_move = ai_move

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); raise SystemExit
                if e.key == pygame.K_h:
                    show_hints = not show_hints
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if ui.button_rect.collidepoint(e.pos):
                    show_hints = not show_hints
                    continue
                sq = ui.mouse_to_square(e.pos, white_bottom)
                if sq is None:
                    continue
                if selected is None:
                    p = board.piece_at(sq)
                    if p and p.color == board.turn:
                        selected = sq
                        legal_targets = [m.to_square for m in board.legal_moves if m.from_square == sq]
                else:
                    mv = chess.Move(selected, sq)
                    if mv in board.legal_moves:
                        board.push(mv)
                        last_move = mv
                        selected = None
                        legal_targets = []
                        if not board.is_game_over():
                            ai_mv = ai.choose_move(board)
                            if ai_mv:
                                board.push(ai_mv)
                                last_move = ai_mv
                    else:
                        selected = None
                        legal_targets = []

        ui.draw_board(
            board,
            selected,
            legal_targets,
            [m[0].to_square for m in helper.suggestions(board)] if show_hints and not board.is_game_over() else [],
            last_move,
            white_bottom
        )
        main_text = status_text(board, label, show_hints)
        sub_text = last_move_text(board)
        tips = top_tips(board, ai, 5) if show_hints and not board.is_game_over() else []
        ui.draw_panel(main_text, sub_text, show_hints, tips)
        pygame.display.flip()
        clock.tick(60)

def move_to_alg(m: chess.Move) -> str:
    return f"{chess.square_name(m.from_square)}→{chess.square_name(m.to_square)}" + (f"={chess.piece_symbol(m.promotion).upper()}" if m.promotion else "")

def last_move_text(board: chess.Board) -> str:
    if board.move_stack:
        last = board.peek()
        return f"Последний ход: {move_to_alg(last)}"
    return "Последний ход: —"

def status_text(board: chess.Board, label: str, show_hints: bool) -> str:
    if board.is_checkmate():
        return "Мат. Вы выиграли!" if not board.turn else "Мат. ИИ победил."
    if board.is_stalemate():
        return "Пат. Ничья."
    if board.is_insufficient_material():
        return "Ничья: недостаточно материала."
    base = f"Ход: {'Белые' if board.turn else 'Чёрные'}  •  Сложность: {label}  •  Подсказки: {'ВКЛ' if show_hints else 'ВЫКЛ'}"
    if board.is_check():
        base += "  •  Шах!"
    return base

if __name__ == "__main__":
    main()
