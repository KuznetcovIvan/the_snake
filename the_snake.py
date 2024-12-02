from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
POSSIBLE_WIDTH = [value for value in range(0, SCREEN_WIDTH, GRID_SIZE)]
POSSIBLE_HEIGHT = [value for value in range(0, SCREEN_HEIGHT, GRID_SIZE)]

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (255, 255, 155)
BORDER_COLOR = (0, 0, 0)
APPLE_COLOR = (255, 25, 25)
BAD_APPLE_COLOR = (150, 25, 25)
POISONED_APPLE_COLOR = (50, 25, 25)
SNAKE_COLOR = (25, 255, 25)

# Начальная скорость движения змейки:
SPEED = 18

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Изгиб питона')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """
    Это базовый класс игровых объектов, от которого наследуются другие
    классы игровых объектов. Он содержит общие атрибуты игровых объектов.
    """

    def __init__(self):
        """
        Метод инициализирует базовые атрибуты объекта,
        такие как его позиция и цвет.
        """
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = None

    def draw(self):
        """
        Метод, предназначенный для переопределения в
        дочерних классах. Определяет, как объект будет
        отрисовываться на экране.
        """
        raise NotImplementedError(
            f'У класса \'{self.__class__.__name__}\' не переопределен '
            'метод \'draw\'!')


class Apple(GameObject):
    """
    Класс, унаследованный от GameObject,
    описывающий яблоко и действия с ним.
    """

    def __init__(self):
        """
        Метод инициализирует базовые атрибуты объекта.
        Задаёт цвет яблока и вызывает метод randomize_position,
        чтобы установить начальную позицию яблока.
        """
        super().__init__()
        self.body_color = APPLE_COLOR
        self.position = self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает случайное положение яблока на игровом поле,
        задаёт атрибуту position новое значение.
        Координаты выбираются так, чтобы яблоко оказалось
        в пределах игрового поля.
        """
        return ((choice(POSSIBLE_WIDTH)), (choice(POSSIBLE_HEIGHT)))

    def draw(self):
        """
        Метод который отрисовывает яблоко
        на игровой поверхности.
        """
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class BadApple(Apple):
    """
    Класс, унаследованный от Aplle,
    описывающий плохое яблоко.
    """

    def __init__(self):
        super().__init__()
        self.body_color = BAD_APPLE_COLOR


class PoisonedApple(Apple):
    """
    Класс, унаследованный от Aplle,
    описывающий отравленное яблоко.
    """

    def __init__(self):
        super().__init__()
        self.body_color = POISONED_APPLE_COLOR


class Snake(GameObject):
    """
    Класс, унаследованный от GameObject, описывающий змейку и её поведение.
    Этот класс управляет её движением, отрисовкой,
    а также обрабатывает действия пользователя.
    """

    def __init__(self):
        """
        Метод инициализирует базовые атрибуты объекта.
        Задаёт цвет змейки.
        """
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = (1, 0)
        self.next_direction = None
        self.last = None

    def draw(self):
        """
        Метод который отрисовывает змейку
        на игровой поверхности, затирая след.
        """
        head_rect = pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        for position in self.positions[:]:
            rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def move(self):
        """
        Метод который обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions
        и удаляя последний элемент, если длина змейки не увеличилась.
        """
        # Нахождение координат новой головы:
        direction_width, direction_height = self.direction
        head_position_width, head_position_height = self.get_head_position()
        to_add = [(direction_width * GRID_SIZE + head_position_width)
                  % SCREEN_WIDTH,
                  (direction_height * GRID_SIZE + head_position_height)
                  % SCREEN_HEIGHT]
        # Добавление в начало списка:
        self.positions.insert(0, to_add)
        # Удаление последнего элемента если длинна змейки не увеличилась:
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def reset(self):
        """
        Метод reset отвечает за сброс змейки в начальное состояние
        после столкновения с собой или другого события,
        требующего перезапуска змейки.
        """
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.length = 1

    def get_head_position(self):
        """
        Метод который возвращает текущее положение головы змейки
        (первый элемент в списке positions).
        """
        return (self.positions[0][0], self.positions[0][1])

    def update_direction(self):
        """
        Метод обновления направления
        после нажатия на кнопку.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(game_object):
    """
    Функция обработки действий пользователя.
    обрабатывает нажатия клавиш, чтобы изменить направление движения змейки.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Функция - точка входа программы,
    выполняет основную логику игры.
    """
    # Инициализация pg:
    pg.init()
    # Экземпляры классов:
    apple = Apple()
    bad_apple = BadApple()
    poisoned_apple = PoisonedApple()
    snake = Snake()
    # Создаю шрифт для вывода очков:
    font = pg.font.SysFont('Arial', 32)
    # Основная логика игры:
    while True:
        screen.fill(BOARD_BACKGROUND_COLOR)
        clock.tick(SPEED)
        apple.draw()
        bad_apple.draw()
        poisoned_apple.draw()
        snake.draw()
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.position = apple.randomize_position()

        if snake.get_head_position() == bad_apple.position:
            if snake.length > 1:
                snake.length -= 1
                end_snake = snake.positions.pop()
                last_rect = pg.Rect(end_snake, (GRID_SIZE, GRID_SIZE))
                pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            else:
                snake.reset()
                screen.fill(BOARD_BACKGROUND_COLOR)
            bad_apple.position = bad_apple.randomize_position()

        if snake.get_head_position() == poisoned_apple.position:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            poisoned_apple.position = poisoned_apple.randomize_position()

        if snake.positions[0] in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        score = font.render(str((snake.length) - 1), 1, (0, 0, 0))
        screen.blit(score, (20, 15))
        pg.display.update()


if __name__ == '__main__':
    main()
