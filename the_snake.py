from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
POSSIBLE_WIDTH = [value for value in range(0, SCREEN_WIDTH, GRID_SIZE)]
POSSIBLE_HEIGHT = [value for value in range(0, SCREEN_HEIGHT, GRID_SIZE)]
CENTRAL_CELL = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
ALL_CELLS = set((w, h) for w in POSSIBLE_WIDTH for h in POSSIBLE_HEIGHT)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
TURNS = {(LEFT, pg.K_UP): UP,
         (RIGHT, pg.K_UP): UP,
         (UP, pg.K_LEFT): LEFT,
         (DOWN, pg.K_LEFT): LEFT,
         (LEFT, pg.K_DOWN): DOWN,
         (RIGHT, pg.K_DOWN): DOWN,
         (UP, pg.K_RIGHT): RIGHT,
         (DOWN, pg.K_RIGHT): RIGHT}

# Цвета:
BOARD_BACKGROUND_COLOR = (255, 255, 155)
BORDER_COLOR = (0, 0, 0)
APPLE_COLOR = (255, 25, 25)
BAD_APPLE_COLOR = (150, 25, 25)
POISONED_APPLE_COLOR = (50, 25, 25)
SNAKE_COLOR = (25, 255, 25)

# Cкорость движения змейки и рекордная длинна:
speed = 20
record_length = 1
# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """
    Это базовый класс игровых объектов, от которого наследуются другие
    классы игровых объектов. Он содержит общие атрибуты игровых объектов.
    """

    def __init__(self, body_color=None):
        """
        Метод инициализирует базовые атрибуты объекта,
        такие как его позиция и цвет.
        """
        self.position = CENTRAL_CELL
        self.body_color = body_color

    def draw(self):
        """
        Метод, предназначенный для переопределения в
        дочерних классах. Определяет, как объект будет
        отрисовываться на экране.
        """
        raise NotImplementedError(
            f'В классе \'{type(self).__name__}\' '
            'не переопределен метод \'draw\'!')

    def draw_cell(self, position, body_color=None):
        """
        Метод принимает параметры позицию и цвет и закрашивает ячейку.
        Если цвет не задан, то используется body_color объекта, обрамленный
        рамкой. Если цвет задан - рисует ячейку но без рамки.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect) if body_color else (
            pg.draw.rect(screen, self.body_color, rect))
        if not body_color:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """
    Класс, унаследованный от GameObject,
    описывающий яблоко и действия с ним.
    """

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=None):
        """
        Метод инициализирует базовые атрибуты объекта.
        Задаёт цвет яблока и вызывает метод randomize_position,
        чтобы установить начальную позицию яблока.
        """
        super().__init__(body_color)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """
        Устанавливает случайное положение яблока на игровом поле,
        задаёт атрибуту position новое значение.
        Координаты выбираются так, чтобы яблоко оказалось
        в пределах игрового поля.
        """
        self.position = choice(tuple(
            ALL_CELLS - set(map(tuple, occupied_positions))))

    def draw(self):
        """
        Метод который отрисовывает яблоко
        на игровой поверхности.
        """
        self.draw_cell(self.position)


class Snake(GameObject):
    """
    Класс, унаследованный от GameObject, описывающий змейку и её поведение.
    Этот класс управляет её движением, отрисовкой,
    а также обрабатывает действия пользователя.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        """
        Метод инициализирует базовые атрибуты объекта.
        Задаёт цвет змейки.
        """
        super().__init__(body_color)
        self.reset()

    def draw(self):
        """
        Метод который отрисовывает змейку
        на игровой поверхности, затирая след.
        """
        self.draw_cell(self.get_head_position())

        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def move(self):
        """
        Метод который обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions
        и удаляя последний элемент, если длина змейки не увеличилась.
        """
        # Нахождение координат новой головы:
        direction_width, direction_height = self.direction
        head_position_width, head_position_height = self.get_head_position()

        # Добавление в начало списка:
        self.positions.insert(0, [
            (direction_width * GRID_SIZE + head_position_width)
            % SCREEN_WIDTH,
            (direction_height * GRID_SIZE + head_position_height)
            % SCREEN_HEIGHT
        ])
        # Удаление последнего элемента если длинна змейки не увеличилась:
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def reset(self):
        """
        Метод reset отвечает за сброс змейки в начальное состояние
        после столкновения с собой или другого события,
        требующего перезапуска змейки.
        """
        self.length = 1
        self.positions = [CENTRAL_CELL]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None

    def get_head_position(self):
        """
        Метод который возвращает текущее положение головы змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def update_direction(self, new_direction):
        """
        Метод обновления направления
        после нажатия на кнопку.
        """
        self.direction = new_direction


def handle_keys(snake):
    """
    Функция обработки действий пользователя.
    обрабатывает нажатия клавиш, чтобы изменить направление движения змейки.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN
                                     and event.key == pg.K_ESCAPE):
            pg.quit()
            raise SystemExit

        if event.type == pg.KEYDOWN:
            snake.update_direction(
                TURNS.get((snake.direction, event.key), snake.direction))

        global speed
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LSHIFT:
                speed = min(speed + 5, 50)
            elif event.key == pg.K_LCTRL:
                speed = max(speed - 5, 5)


def main():
    """
    Функция - точка входа программы,
    выполняет основную логику игры.
    """
    # Инициализация pg:
    pg.init()
    # Экземпляры классов:
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    bad_apple = Apple(BAD_APPLE_COLOR, (*snake.positions, apple.position))
    poisoned_apple = Apple(POISONED_APPLE_COLOR, (
        *snake.positions, apple.position, bad_apple.position))
    # Основная логика игры:
    screen.fill(BOARD_BACKGROUND_COLOR)
    while True:
        clock.tick(speed)
        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == list(apple.position):
            snake.length += 1
            apple.randomize_position((
                *snake.positions, bad_apple.position, poisoned_apple.position))
            global record_length
            record_length = max(record_length, snake.length)

        elif snake.get_head_position() == list(bad_apple.position):
            if snake.length > 1:
                snake.length -= 1
                snake.draw_cell(snake.positions.pop(),
                                BOARD_BACKGROUND_COLOR)
            else:
                snake.reset()
                screen.fill(BOARD_BACKGROUND_COLOR)
            bad_apple.randomize_position(
                (*snake.positions, apple.position, poisoned_apple.position))

        elif snake.get_head_position() == list(poisoned_apple.position):
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            poisoned_apple.randomize_position((
                *snake.positions, apple.position, bad_apple.position))

        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        bad_apple.draw()
        poisoned_apple.draw()
        snake.draw()
        pg.display.set_caption(f'Snake! Esc-quit // '
                               f'Speed:{speed} ↑-lshift, ↓-lctrl // '
                               f'Length: {snake.length} // '
                               f'Record: {record_length}')
        pg.display.update()


if __name__ == '__main__':
    main()
