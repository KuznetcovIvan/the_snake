from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Изгиб питона')

# Настройка времени:
clock = pygame.time.Clock()

# Классы игры:


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
        pass


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
        possible_widh = [value for value in range(0, SCREEN_WIDTH, GRID_SIZE)]
        possible_height = [value for value in range(0, SCREEN_HEIGHT, GRID_SIZE)]

        return ((choice(possible_widh)), (choice(possible_height)))

    def draw(self):
        """
        Метод который отрисовывает яблоко
        на игровой поверхности.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


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
        next_direction = None
        self.last = None

    def draw(self):
        """
        Метод который отрисовывает змейку
        на игровой поверхности, затирая след.
        """
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

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
        self.positions = self.positions.insert(0, to_add)
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
        self.direction = choice(UP, DOWN, LEFT, RIGHT)
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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Функция - точка входа программы,
    выполняет основную логику игры.
    """
    # Инициализация PyGame:
    pygame.init()
    # Экземпляры классов:
    apple = Apple()
    snake = Snake()
    # snake = Snake()
    # Основная логика игры:
    while True:
        clock.tick(SPEED)
        apple.draw()
        snake.draw()
        handle_keys(snake)
        apple.draw()
        # snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()


#     # Отрисовка головы змейки
#     head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
#     pygame.draw.rect(screen, self.body_color, head_rect)
#     pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

#     # Затирание последнего сегмента
#     if self.last:
#         last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
#         pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
