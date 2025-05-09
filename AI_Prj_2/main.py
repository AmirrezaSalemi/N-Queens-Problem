import asyncio
import random
import pygame
import numpy as np
import time

N = 100
CELL_SIZE = 20
MARGIN = 50

BOARD_WIDTH = N * CELL_SIZE
BOARD_HEIGHT = N * CELL_SIZE

WIDTH = BOARD_WIDTH + 2 * MARGIN
HEIGHT = BOARD_HEIGHT + 2 * MARGIN

# Get info of display with PyGame
pygame.init()
display_info = pygame.display.Info()
DISPLAY_WIDTH = display_info.current_w
DISPLAY_HEIGHT = display_info.current_h

VIRTUAL_WIDTH = BOARD_WIDTH + 2 * MARGIN
VIRTUAL_HEIGHT = BOARD_HEIGHT + 2 * MARGIN

FPS = 60
BACKGROUND_COLOR = (240, 240, 240)
LIGHT_SQUARE = (245, 245, 220)
DARK_SQUARE = (139, 69, 19)
BORDER_COLOR = (50, 50, 50)
GRID_COLOR = (100, 100, 100)
LABEL_COLOR = (0, 0, 0)

# Initialize Pygame window in fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("N-Queens Problem")
clock = pygame.time.Clock()

# Load and Set crown image
crown_image = pygame.image.load("crown.png")
crown_image = pygame.transform.scale(crown_image, (CELL_SIZE, CELL_SIZE))

# Load font for labels
font = pygame.font.SysFont("arial", 16, bold=True)


# Generate Row of each Queen in board
def generate_board():
    return np.random.permutation(N)


# Min-Conflicts algorithm
def min_conflicts(board):
    start_time = time.perf_counter()
    max_steps = N * 20
    row_counts = np.zeros(N, dtype=int)
    main_diameter_counts = np.zeros(2 * N - 1, dtype=int)
    sub_diameter_counts = np.zeros(2 * N - 1, dtype=int)

    for col in range(N):
        row = board[col]
        row_counts[row] += 1
        main_diameter_counts[row - col + N - 1] += 1
        sub_diameter_counts[row + col] += 1

    for step in range(max_steps):
        conflict_cols = []
        for col in range(N):
            row = board[col]
            if (row_counts[row] > 1 or
                    main_diameter_counts[row - col + N - 1] > 1 or
                    sub_diameter_counts[row + col] > 1):
                conflict_cols.append(col)

        if not conflict_cols:
            end_time = time.perf_counter()
            print(f"In step {step}: solution found")
            return board, end_time - start_time

        col = random.choice(conflict_cols)
        old_row = board[col]
        min_conflicts = N + 1
        best_rows = []
        for row in range(N):
            conflicts = (row_counts[row] - (1 if row == old_row else 0) +
                         main_diameter_counts[row - col + N - 1] - (1 if row == old_row else 0) +
                         sub_diameter_counts[row + col] - (1 if row == old_row else 0))
            if conflicts < min_conflicts:
                min_conflicts = conflicts
                best_rows = [row]
            elif conflicts == min_conflicts:
                best_rows.append(row)

        new_row = random.choice(best_rows)
        if new_row != old_row:
            board[col] = new_row
            row_counts[old_row] -= 1
            row_counts[new_row] += 1
            main_diameter_counts[old_row - col + N - 1] -= 1
            main_diameter_counts[new_row - col + N - 1] += 1
            sub_diameter_counts[old_row + col] -= 1
            sub_diameter_counts[new_row + col] += 1

    end_time = time.perf_counter()
    return generate_board(), end_time - start_time


# Draw chess board
def draw_board(board, offset_x=0, offset_y=0):
    screen.fill(BACKGROUND_COLOR)
    border_rect = pygame.Rect(MARGIN - 2, MARGIN - 2, BOARD_WIDTH + 4, BOARD_HEIGHT + 4)
    pygame.draw.rect(screen, BORDER_COLOR, border_rect, 2)
    for row in range(N):
        screen_y = MARGIN + row * CELL_SIZE - offset_y
        if -CELL_SIZE < screen_y < DISPLAY_HEIGHT:
            for col in range(N):
                screen_x = MARGIN + col * CELL_SIZE - offset_x
                if -CELL_SIZE < screen_x < DISPLAY_WIDTH:
                    color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                    pygame.draw.rect(screen, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, GRID_COLOR, (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)
                    if board[col] == row:
                        highlight_color = (255, 255, 0, 128)
                        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        pygame.draw.circle(highlight_surface, highlight_color,
                                           (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2)
                        screen.blit(highlight_surface, (screen_x, screen_y))
                        screen.blit(crown_image, (screen_x, screen_y))
    # Columns and Rows Number
    for i in range(N):
        screen_x = MARGIN + i * CELL_SIZE - offset_x
        if 0 <= screen_x < DISPLAY_WIDTH:
            label = font.render(str(i + 1), True, LABEL_COLOR)
            label_rect = label.get_rect(center=(screen_x + CELL_SIZE // 2, MARGIN // 2))
            screen.blit(label, label_rect)
        screen_y = MARGIN + i * CELL_SIZE - offset_y
        if 0 <= screen_y < DISPLAY_HEIGHT:
            label = font.render(str(i + 1), True, LABEL_COLOR)
            label_rect = label.get_rect(center=(MARGIN // 2, screen_y + CELL_SIZE // 2))
            screen.blit(label, label_rect)


async def main():
    board = generate_board()
    running = True
    solution_found = False
    offset_x = 0
    offset_y = 0
    scroll_speed = 50
    key_scroll_speed = 50
    dragging = False
    middle_scrolling = False
    last_mouse_pos = (0, 0)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    global DISPLAY_WIDTH, DISPLAY_HEIGHT
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((1280, 720))
                        DISPLAY_WIDTH = 1280
                        DISPLAY_HEIGHT = 720
                    else:
                        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        display_info = pygame.display.Info()
                        DISPLAY_WIDTH = display_info.current_w
                        DISPLAY_HEIGHT = display_info.current_h
                if event.key == pygame.K_LEFT:
                    offset_x -= key_scroll_speed
                if event.key == pygame.K_RIGHT:
                    offset_x += key_scroll_speed
                if event.key == pygame.K_UP:
                    offset_y -= key_scroll_speed
                if event.key == pygame.K_DOWN:
                    offset_y += key_scroll_speed
                offset_x = max(0, min(VIRTUAL_WIDTH - DISPLAY_WIDTH, offset_x))
                offset_y = max(0, min(VIRTUAL_HEIGHT - DISPLAY_HEIGHT, offset_y))
            if event.type == pygame.MOUSEWHEEL:
                dx = event.x * scroll_speed
                dy = event.y * scroll_speed
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT and event.x == 0:
                    dx = event.y * scroll_speed
                offset_x += dx
                offset_y -= dy
                offset_x = max(0, min(VIRTUAL_WIDTH - DISPLAY_WIDTH, offset_x))
                offset_y = max(0, min(VIRTUAL_HEIGHT - DISPLAY_HEIGHT, offset_y))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_pos = event.pos
                if event.button == 2:
                    middle_scrolling = True
                    last_mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                if event.button == 2:
                    middle_scrolling = False
            if event.type == pygame.MOUSEMOTION:
                if dragging or middle_scrolling:
                    current_pos = event.pos
                    delta_x = current_pos[0] - last_mouse_pos[0]
                    delta_y = current_pos[1] - last_mouse_pos[1]
                    offset_x -= delta_x
                    offset_y -= delta_y
                    last_mouse_pos = current_pos
                    offset_x = max(0, min(VIRTUAL_WIDTH - DISPLAY_WIDTH, offset_x))
                    offset_y = max(0, min(VIRTUAL_HEIGHT - DISPLAY_HEIGHT, offset_y))

        if not solution_found:
            board, elapsed_time = min_conflicts(board)
            row_counts = np.bincount(board, minlength=N)
            main_diags = np.bincount([board[i] - i + N - 1 for i in range(N)], minlength=2 * N - 1)
            anti_diags = np.bincount([board[i] + i for i in range(N)], minlength=2 * N - 1)
            if not (np.any(row_counts > 1) or np.any(main_diags > 1) or np.any(anti_diags > 1)):
                solution_found = True
                print(f"Time to find solution: {elapsed_time:.10f} seconds")
                draw_board(board, offset_x=offset_x, offset_y=offset_y)
                pygame.display.flip()
            else:
                draw_board(board, offset_x=offset_x, offset_y=offset_y)
                pygame.display.flip()

        if solution_found:
            draw_board(board, offset_x=offset_x, offset_y=offset_y)
            pygame.display.flip()

        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
