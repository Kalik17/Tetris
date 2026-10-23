import pygame
import random

# ---------- Настройки ----------
CELL = 30
COLS, ROWS = 10, 20
PLAY_W, PLAY_H = COLS * CELL, ROWS * CELL
PANEL_W = 160
SCREEN_W, SCREEN_H = PLAY_W + PANEL_W, PLAY_H

COLORS = {
    'I': (0, 240, 240), 'O': (240, 240, 0), 'T': (160, 0, 240),
    'S': (0, 240, 0),   'Z': (240, 0, 0),   'J': (0, 0, 240),
    'L': (240, 160, 0),
}

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]],
}


def rotate_cw(shape):
    """Поворот матрицы фигуры на 90° по часовой стрелке."""
    return [list(row) for row in zip(*shape[::-1])]


class Tetris:
    def __init__(self):
        self.board = [[None] * COLS for _ in range(ROWS)]
        self.bag = []
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.fall_timer = 0
        self.fall_delay = 500          # мс на одну клетку вниз
        self.spawn()

    # --- генерация фигур (7-bag: каждая фигура раз в 7 ходов) ---
    def next_kind(self):
        if not self.bag:
            self.bag = list(SHAPES.keys())
            random.shuffle(self.bag)
        return self.bag.pop()

    def spawn(self):
        self.kind = self.next_kind()
        self.shape = [row[:] for row in SHAPES[self.kind]]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0
        if not self.valid(self.shape, self.x, self.y):
            self.game_over = True

    # --- проверка, можно ли поставить фигуру в позицию ---
    def valid(self, shape, x, y):
        for r, row in enumerate(shape):
            for c, v in enumerate(row):
                if not v:
                    continue
                bx, by = x + c, y + r
                if bx < 0 or bx >= COLS or by >= ROWS:
                    return False
                if by >= 0 and self.board[by][bx] is not None:
                    return False
        return True

    def move(self, dx, dy):
        if self.valid(self.shape, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def rotate(self):
        new_shape = rotate_cw(self.shape)
        # простые "wall kicks": если при повороте упираемся в стену — сдвигаем
        for kick in (0, -1, 1, -2, 2):
            if self.valid(new_shape, self.x + kick, self.y):
                self.shape = new_shape
                self.x += kick
                return

    def lock(self):
        """Фигура останавливается — записываем её в поле."""
        for r, row in enumerate(self.shape):
            for c, v in enumerate(row):
                if v and self.y + r >= 0:
                    self.board[self.y + r][self.x + c] = COLORS[self.kind]
        self.clear_lines()
        self.spawn()

    def clear_lines(self):
        kept = [row for row in self.board if any(v is None for v in row)]
        cleared = ROWS - len(kept)
        if cleared:
            self.board = [[None] * COLS for _ in range(cleared)] + kept
            self.lines += cleared
            self.score += [0, 100, 300, 500, 800][cleared]

    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.lock()

    def update(self, dt):
        if self.game_over:
            return
        self.fall_timer += dt
        if self.fall_timer >= self.fall_delay:
            self.fall_timer = 0
            if not self.move(0, 1):
                self.lock()


def draw_cell(surf, cx, cy, color):
    rect = pygame.Rect(cx * CELL, cy * CELL, CELL, CELL)
    pygame.draw.rect(surf, color, rect)
    pygame.draw.rect(surf, (0, 0, 0), rect, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Тетрис")
    pygame.key.set_repeat(150, 50)      # автоповтор при удержании клавиши
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)
    small = pygame.font.SysFont("consolas", 18)

    game = Tetris()

    while True:
        dt = clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if game.game_over:
                    if e.key == pygame.K_r:
                        game = Tetris()
                    continue
                if e.key == pygame.K_LEFT:
                    game.move(-1, 0)
                elif e.key == pygame.K_RIGHT:
                    game.move(1, 0)
                elif e.key == pygame.K_DOWN:
                    if game.move(0, 1):
                        game.score += 1
                elif e.key == pygame.K_UP:
                    game.rotate()
                elif e.key == pygame.K_SPACE:
                    game.hard_drop()

        game.update(dt)

        # --- отрисовка ---
        screen.fill((20, 20, 20))
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, PLAY_W, PLAY_H))

        # стакан
        for r in range(ROWS):
            for c in range(COLS):
                if game.board[r][c]:
                    draw_cell(screen, c, r, game.board[r][c])

        # текущая фигура
        for r, row in enumerate(game.shape):
            for c, v in enumerate(row):
                if v and game.y + r >= 0:
                    draw_cell(screen, game.x + c, game.y + r, COLORS[game.kind])

        # сетка
        for c in range(COLS + 1):
            pygame.draw.line(screen, (60, 60, 60), (c*CELL, 0), (c*CELL, PLAY_H))
        for r in range(ROWS + 1):
            pygame.draw.line(screen, (60, 60, 60), (0, r*CELL), (PLAY_W, r*CELL))

        # панель
        px = PLAY_W + 15
        screen.blit(font.render("Очки", True, (255, 255, 255)), (px, 15))
        screen.blit(small.render(str(game.score), True, (255, 255, 255)), (px, 45))
        screen.blit(font.render("Линии", True, (255, 255, 255)), (px, 90))
        screen.blit(small.render(str(game.lines), True, (255, 255, 255)), (px, 120))
        screen.blit(small.render("←→ двигать", True, (180, 180, 180)), (px, 180))
        screen.blit(small.render("↑ поворот", True, (180, 180, 180)), (px, 205))
        screen.blit(small.render("↓ вниз", True, (180, 180, 180)), (px, 230))
        screen.blit(small.render("Space сброс", True, (180, 180, 180)), (px, 255))

        if game.game_over:
            txt = font.render("GAME OVER", True, (255, 80, 80))
            screen.blit(txt, (PLAY_W // 2 - txt.get_width() // 2, PLAY_H // 2 - 20))
            txt2 = small.render("R — заново", True, (255, 255, 255))
            screen.blit(txt2, (PLAY_W // 2 - txt2.get_width() // 2, PLAY_H // 2 + 15))

        pygame.display.flip()


if __name__ == "__main__":
    main()