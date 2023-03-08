import constants

class Paddle:
    """A class that represents the paddle of the game"""

    def __init__(self, canvas, paddle_width=constants.DEFAULT_PADDLE_WIDTH,
                 paddle_height=constants.DEFAULT_PADDLE_HEIGHT,
                 canvas_gap=constants.DEFAULT_CANVAS_GAP, colour=constants.DEFAULT_PADDLE_COLOUR):
        """Initialises Paddle and creates a rectangle on the canvas centred horizontally
        and slightly above the bottom of the canvas

        Parameters:
            canvas (Canvas): The canvas that the ball will be drawn on
            paddle_width (int) (default 150): The width of the paddle
            paddle_height (int) (default 10): The height of the paddle
            canvas_gap (int) (default 40): The gap between the bottom of the canvas
                                           and the bottom of the paddle
            colour (str) (default "white"): The colour of the paddle.
                                            This can be in the form "#RRGGBB"
                                            or any locally defined standard colour name.
        """

        # Assigns values to the object's attributes based on the arguments to the initialiser.
        self.__canvas = canvas
        self.__width = paddle_width

        # Gets the canvas's width and height.
        canvas_width = canvas.winfo_reqwidth()
        canvas_height = canvas.winfo_reqheight()

        # Calculates the x and y coordinates for the top, bottom, left
        # and right edges of the paddle.
        # The coordinates are calculated so that the paddle is centred horizontally
        # and slightly above the bottom of the canvas.
        self.__left_x = int(canvas_width/2 - paddle_width/2)
        self.__top_y = canvas_height - canvas_gap - paddle_height
        self.__right_x = int(canvas_width/2 + paddle_width/2)
        self.__bottom_y = canvas_height - canvas_gap

        # Stores the paddle's speed which is based on if the user is pressing a key or not.
        self.__speed = 0

        # Creates a rectangle at the coordinates calculated that represents the paddle
        # and stores the object ID of the paddle.
        self.__id = canvas.create_rectangle(self.__left_x, self.__top_y, self.__right_x,
                                            self.__bottom_y, fill=colour)

    def move(self):
        """Causes the paddle to move based on its speed attribute

        This also checks if the paddle collides with the walls of the canvas
        and makes sure that the paddle doesn't go outside the canvas.
        """

        # Moves the paddle left or right according to its speed.
        self.__canvas.move(self.__id, self.__speed, 0)

        # Gets the canvas's width.
        canvas_width = self.__canvas.winfo_reqwidth()

        # Updates the x and y coordinates of the top, bottom, left
        # and right edges of the new position of the paddle.
        self.__left_x = self.__canvas.coords(self.__id)[0]
        self.__top_y = self.__canvas.coords(self.__id)[1]
        self.__right_x = self.__canvas.coords(self.__id)[2]
        self.__bottom_y = self.__canvas.coords(self.__id)[3]

        # If the paddle is outside of the canvas on the left,
        # then move it so that it is on the left inside of the canvas.
        if self.__left_x < 0:

            # Updates the x coordinates of the left and right edges of the paddle
            # so that it is inside the canvas.
            self.__left_x = 0
            self.__right_x = self.__width
            self.__canvas.coords(self.__id, self.__left_x, self.__top_y, self.__right_x,
                                 self.__bottom_y)

        # If the paddle is outside of the canvas on the right,
        # then move it so that is is on the right inside of the canvas.
        elif self.__right_x > canvas_width:

            # Updates the x coordinates of the left and right edges of the paddle
            # so that it is inside the canvas.
            self.__left_x = canvas_width - self.__width
            self.__right_x = canvas_width

            self.__canvas.coords(self.__id, self.__left_x, self.__top_y, self.__right_x,
                                 self.__bottom_y)

    def move_left(self, speed=constants.DEFAULT_PADDLE_SPEED):
        """Moves the paddle left the next time the move() method is called
        by changing the paddle's speed

        Parameters:
            event (Event) (default None): The Event object that is passed in by default
                                          due to Tkinter key bindings.
                                          This can be any value or data type if you aren't
                                          using Tkinter key bindings.
            speed (int) (default 15): The number of pixels that the paddle should move left by.
                                      You do not need to make this negative
                                      as the subroutine does this for you.
        """

        # Sets the paddle's speed so that it moves left.
        self.__speed = -speed

    def move_right(self, speed=constants.DEFAULT_PADDLE_SPEED):
        """Moves the paddle right the next time the move() method is called
        by changing the paddle's speed

        Parameters:
            event (Event) (default None): The Event object that is passed in by default
                                          due to Tkinter key bindings.
                                          This can be any value or data type if you aren't
                                          using Tkinter key bindings.
            speed (int) (default 15): The number of pixels that the paddle should move right by
        """

        # Sets the paddle's speed so that it moves right.
        self.__speed = speed

    def stop(self):
        """Makes the paddle stop the next time the move() method is called
        by setting the paddle's speed to 0

        Parameters:
            event (Event) (default None): The Event object that is passed in by default
                                          due to Tkinter key bindings.
                                          This can be any value or data type if you aren't
                                          using Tkinter key bindings.
        """

        # Sets the paddle's speed to 0 so that it stops moving.
        self.__speed = 0

    @property
    def id(self):
        """(int): The object ID of the paddle when it is created on the canvas"""

        return self.__id

    @id.setter
    def id(self, value):

        self.__id = value

    @property
    def left_x(self):
        """(float): The x coordinate of the left edge of the paddle"""

        return self.__left_x

    @left_x.setter
    def left_x(self, value):

        self.__left_x = value

    @property
    def top_y(self):
        """(float): The y coordinate of the top edge of the paddle"""

        return self.__top_y

    @top_y.setter
    def top_y(self, value):

        self.__top_y = value

    @property
    def right_x(self):
        """(float): The x coordinate of the right edge of the paddle"""

        return self.__right_x

    @right_x.setter
    def right_x(self, value):

        self.__right_x = value

    @property
    def bottom_y(self):
        """(float): The y coordinate of the bottom edge of the paddle"""

        return self.__bottom_y

    @bottom_y.setter
    def bottom_y(self, value):

        self.__bottom_y = value

    @property
    def width(self):
        """(int): The width of the paddle"""

        return self.__width

    @width.setter
    def width(self, value):

        self.__width = value

    @property
    def height(self):
        """(int): The height of the paddle"""

        return int(self.__bottom_y - self.__top_y)

    @property
    def colour(self):
        """(str): The colour of the paddle in the form #RRGGBB
        or any locally defined standard colour name"""

        return self.__canvas.itemcget(self.__id, "fill")

    @property
    def canvas_gap(self):
        """(int): The gap between the bottom of the canvas and the bottom of the paddle"""

        return int(self.__canvas.winfo_reqheight() - self.__bottom_y)

if __name__ == "__main__":
    print("Please run main.py")
