import constants

class Brick:
    """A class that represents the bricks in the game"""

    def __init__(self, canvas, x, y, score, colour, width, height=constants.DEFAULT_BRICK_HEIGHT):
        """Initialises Brick and creates a rectangle on the canvas to represent the brick

        Parameters:
            canvas (Canvas): The canvas that the brick will be drawn on
            x (int): The x coordinate of the top left corner of the brick
            y (int): The y coordinate of the top left corner of the brick
            score (int): How much score the brick is worth when destroyed
            colour (str): The colour of the brick.
                          This can be in the form "#RRGGBB"
                          or any locally defined standard colour name.
            width (int): The width of the brick
            height (int): The height of the brick
        """

        # Assigns values to the object's attributes based on the arguments to the initialiser.
        self.__canvas = canvas
        self.__score = score

        # Calculates the x and y coordinates for the top, bottom, left
        # and right edges of the paddle.
        self.__left_x = x
        self.__top_y = y
        self.__right_x = x + width
        self.__bottom_y = y + height

        # Creates a rectangle at the coordinates calculated that represents the brick
        # and stores the object ID of the brick.
        self.__id = canvas.create_rectangle(x, y, self.__right_x, self.__bottom_y, fill=colour)

    @property
    def id(self):
        """(int): The object ID of the brick when it is created on the canvas"""

        return self.__id

    @property
    def score(self):
        """(int): How much score the brick is worth when destroyed"""

        return self.__score

    @property
    def left_x(self):
        """(int): The x coordinate of the left edge of the brick"""

        return self.__left_x

    @property
    def top_y(self):
        """(int): The y coordinate of the top edge of the brick"""

        return self.__top_y

    @property
    def right_x(self):
        """(int): The x coordinate of the right edge of the brick"""

        return self.__right_x

    @property
    def bottom_y(self):
        """(int): The y coordinate of the bottom edge of the brick"""

        return self.__bottom_y

    @property
    def colour(self):
        """(str): The colour of the brick in the form #RRGGBB
        or any locally defined standard colour name"""

        return self.__canvas.itemcget(self.__id, "fill")

    @property
    def width(self):
        """(int): The width of the brick"""

        return int(self.__right_x - self.__left_x)

    @property
    def height(self):
        """(int): The height of the brick"""

        return int(self.__bottom_y - self.__top_y)

if __name__ == "__main__":
    print("Please run main.py")
