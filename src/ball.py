import math
import random
import constants

class Ball:
    """A class that represents the ball of the game"""

    def __init__(self, canvas, paddle, bricks, level, x_velocity=0.0,
                 y_velocity=constants.DEFAULT_BALL_SPEED,
                 bounces_until_speed_up=constants.DEFAULT_BOUNCES_UNTIL_SPEED_UP,
                 speed_up_amount=constants.DEFAULT_SPEED_UP_AMOUNT,
                 radius=constants.DEFAULT_BALL_RADIUS, paddle_gap=constants.DEFAULT_PADDLE_GAP,
                 colour=constants.DEFAULT_BALL_COLOUR):
        """Initialises Ball and creates a sphere on the canvas centred horizontally
        and slightly above the paddle to represent this

        Parameters:
            canvas (Canvas): The canvas that the ball will be drawn on
            paddle (Paddle): The paddle is being used in the game
            bricks (List[Brick]): A list that contains the Brick objects in the game
            level (int): The level of the game
            x_velocity (float) (default 0.0): The initial velocity of the ball
                                              in the x direction (can be negative)
            y_velocity (float) (default 8.0): The initial velocity of the ball
                                              in the y direction (can be negative)
            bounces_until_speed_up (int) (default 3): How many times the ball has to
                                                      bounce off the paddle to speed the ball up
            speed_up_amount (float) (default 1.0): How much the ball should speed up by when it does
            radius (int) (default 8): The radius of the ball
            paddle_gap (int) (default 100): The initial gap between the top of the paddle
                                            and the bottom of the ball
            colour (str) (default "white"): The colour of the ball.
                                            This can be in the form "#RRGGBB"
                                            or any locally defined standard colour name.
        """

        # Assigns values to the object's attributes based on the arguments to the initialiser.
        self.__canvas = canvas
        self.__paddle = paddle
        self.__bricks = bricks
        self.__x_velocity = x_velocity
        self.__y_velocity = y_velocity
        self.__speed = math.sqrt(x_velocity**2 + y_velocity**2)
        self.__original_bounces_until_speed_up = max(1, constants.DEFAULT_BOUNCES_UNTIL_SPEED_UP
                                                        - level + 1)
        self.__bounces_until_speed_up = bounces_until_speed_up
        self.__speed_up_amount = speed_up_amount
        self.__radius = radius

        # Gets the canvas's width.
        canvas_width = canvas.winfo_reqwidth()

        # Calculates the x and y coordinates for the top, bottom, left and right edges of the ball
        # (if you place a square around it).
        # The coordinates are calculated so that the ball is centred horizontally
        # and slightly above the paddle.
        self.__left_x = int(canvas_width/2 - radius)
        self.__top_y = int(paddle.top_y - paddle_gap - radius)
        self.__right_x = int(canvas_width/2 + radius)
        self.__bottom_y = int(paddle.top_y - paddle_gap + radius)

        # Creates a white circle at the coordinates calculated that represents the ball
        # and stores the object ID of the ball.
        self.__id = canvas.create_oval(self.__left_x, self.__top_y, self.__right_x, self.__bottom_y,
                                     fill=colour)

    def move(self):
        """Causes the ball to move based on its velocity

        This also checks if the ball collides with anything relevant (bricks, paddle, walls)
        and calls the relevant functions to deal with this.

        Returns:
            new_lives (int): The number of lives the user has after the ball has moved
        """

        # Moves the ball according to its speed.
        self.__canvas.move(self.__id, self.__x_velocity, self.__y_velocity)

        # Updates the x and y coordinates of the top, bottom, left and right edges of the ball.
        self.__left_x = self.__canvas.coords(self.__id)[0]
        self.__top_y = self.__canvas.coords(self.__id)[1]
        self.__right_x = self.__canvas.coords(self.__id)[2]
        self.__bottom_y = self.__canvas.coords(self.__id)[3]

        # Gets the canvas's width and height.
        canvas_width = self.__canvas.winfo_reqwidth()
        canvas_height = self.__canvas.winfo_reqheight()

        # If the ball moves past the left side of the canvas
        # then reverse its x direction and move it to be within the canvas.
        if self.__left_x < 0:
            self.__x_velocity = -self.__x_velocity
            self.__left_x = 0
            self.__right_x = 2 * self.__radius
            self.__canvas.coords(self.__id, self.__left_x, self.__top_y, self.__right_x,
                                 self.__bottom_y)

        # If the ball moves past the right side of the canvas
        # then reverse its x direction and move it to be within the canvas.
        if self.__right_x > canvas_width:
            self.__x_velocity = -self.__x_velocity
            self.__left_x = canvas_width - 2 * self.__radius
            self.__right_x = canvas_width
            self.__canvas.coords(self.__id, self.__left_x, self.__top_y, self.__right_x,
                                 self.__bottom_y)

        # If the ball moves past the top side of the canvas
        # then reverse its y direction and move it to be within the canvas.
        if self.__top_y < 0:
            self.__y_velocity = -self.__y_velocity
            self.__top_y = 0
            self.__bottom_y = 2 * self.__radius
            self.__canvas.coords(self.__id, self.__left_x, self.__top_y, self.__right_x,
                                 self.__bottom_y)

        # Stores whether the user should lose a life or not
        # and is returned at the end of the function.
        lose_life = False

        # If the ball moves past the bottom side of the canvas
        # then change the return value to make the user lose a life
        # and reset the ball back to its starting position.
        if self.__bottom_y > canvas_height:

            # Changes the return value to make the user to lose a life and reset the ball.
            lose_life = True

        # Gets a list of object IDs that the ball is overlapping with.
        overlapping_objects = self.__canvas.find_overlapping(self.__left_x, self.__top_y,
                                                             self.__right_x, self.__bottom_y)

        # If the ball hits the paddle then calculate the new direction of the ball
        # based on which edge the ball hit the paddle.
        if self.__paddle.id in overlapping_objects:

            # If the ball hit the paddle's left or right side then reverse the ball's x direction.
            if ((self.__left_x < self.__paddle.left_x
                    and self.__x_velocity > 0)
                    or (self.__right_x > self.__paddle.right_x
                        and self.__x_velocity < 0)):
                self.__x_velocity = -self.__x_velocity

            # If the ball hit the paddle's top side then call a subroutine
            # that calculates how the ball should be rebounded.
            elif (self.__top_y < self.__paddle.top_y
                and self.__y_velocity > 0):
                self.__bounce_ball_off_paddle()

            # If the ball hit the paddle's bottom side (somehow)
            # then reverse the ball's y direction.
            elif (self.__bottom_y > self.__paddle.bottom_y
                and self.__y_velocity < 0):
                self.__y_velocity = -self.__y_velocity

        # Checks for any collisions with bricks and resolves them.
        # Stores the score the player gained from destroying any bricks.
        score = self.__check_brick_collisions(overlapping_objects)

        # Returns whether the user should lives or not after the ball moved
        # and the score the player gained from destroying any bricks.
        return lose_life, score

    def __bounce_ball_off_paddle(self):
        # Causes the ball to rebound off of the paddle.

        # Calculates the x coordinate of the paddle's centre.
        paddle_centre_x = (self.__paddle.left_x + self.__paddle.right_x)/2

        # Calculates the x coordinate of the centre of the ball.
        ball_centre_x = (self.__left_x + self.__right_x)/2

        # Calculates the absolute horizontal distance from the paddle's centre to the ball's centre.
        ball_distance_from_centre = abs(paddle_centre_x - ball_centre_x)

        # If the ball's centre is outside of the paddle
        # then treat it as if the centre was on the edge of the paddle for calculations.
        # This can happen if the ball only just collides with paddle.
        ball_distance_from_centre = min(ball_distance_from_centre, self.__paddle.width/2)

        # Calculate the ball's angle in degrees when it was travelling towards the paddle.
        # The angle is taken anti-clockwise from the positive x-axis.
        ball_angle = math.atan2(self.__y_velocity, -self.__x_velocity)
        ball_angle = math.degrees(ball_angle)

        # If the ball was travelling at a very gradual angle
        # then randomly generate an offset to make it less gradual.
        if 0 <= ball_angle <= 20:
            random_angle_change = random.uniform(-45, -20)
        elif 160 <= ball_angle <= 180:
            random_angle_change = random.uniform(20, 45)

        # If the ball was travelling at a very steep angle
        # then randomly generate an offset to make it less steep.
        elif 80 <= ball_angle <= 100:
            random_angle_change = random.uniform(-45, 45)

            # Keeps on generating random offsets until one is generated
            # that is either in the range [-45, -20] or [20, 45].
            while -20 < random_angle_change < 20:
                random_angle_change = random.uniform(-45, 45)

        # If the ball was travelling from left to right then randomly generate an offset
        # to make it more likely that it will rebound in the same direction.
        elif ball_angle >= 90:
            random_angle_change = random.uniform(-30, 10)

        # If the ball was travelling from right to left then randomly generate an offset
        # to make it more likely that it will rebound in the same direction.
        else:
            random_angle_change = random.uniform(-10, 30)

        # Causes the random offset to be scaled to a greater value the further away the ball was
        # from the paddle's centre when it hit the paddle.
        # The offset is scaled up to 1.5x when the ball hits the edge of the paddle
        # and is 1x when the ball hits the centre of the paddle.
        random_angle_change *= (ball_distance_from_centre / (self.__paddle.width/2)) * 0.5 + 1

        # Calculates the new angle that the ball should be travelling in
        # after rebounding off the paddle.
        # It calculates the angle as if the ball had rebounded perfectly off
        # and then applies the random offset.
        ball_angle = 180 - ball_angle + random_angle_change

        # If the new angle that the ball is travelling at is at a very gradual angle
        # or outside of the range [0, 180] then set the ball's new angle to a lesser gradual angle.
        ball_angle = min(ball_angle, 160)
        ball_angle = max(ball_angle, 20)

        # Converts the ball's angle to radians.
        ball_angle = math.radians(ball_angle)

        # Decrements the counter that keeps track of when the ball should speed up.
        self.__bounces_until_speed_up -= 1

        # If the ball should speed up then increase the ball's speed and then reset the counter.
        if self.__bounces_until_speed_up == 0:
            self.__speed += self.__speed_up_amount
            self.__bounces_until_speed_up = self.__original_bounces_until_speed_up

        # Calculates the new velocities for the ball using trigonometry and the ball's speed.
        self.__x_velocity = self.__speed * math.cos(ball_angle)
        self.__y_velocity = -(self.__speed * math.sin(ball_angle))

        # Moves the ball to be right above the paddle in the same x coordinates.
        self.__canvas.coords(self.__id, self.__left_x, self.__paddle.top_y - 2 * self.__radius,
                             self.__right_x, self.__paddle.top_y)

    def __check_brick_collisions(self, overlapping_objects):
        # Checks for any collisions with bricks, resolves them
        # and returns any score the player gained from destoying any bricks.

        # Stores the Brick objects that were hit by the ball and need to be removed.
        # This is done outside of the loop to ensure that all bricks are iterated over properly.
        bricks_to_delete = []

        # Iterates over all the Brick objects.
        for brick in self.__bricks:

            # If the ball collided with the brick then bounce the ball off of the brick
            # and then remove the brick from the game.
            if brick.id in overlapping_objects:

                # Stores how in the ball is overlapping with each edge of the brick
                # (if the ball is overlapping with that edge of the brick)
                collision_depth = {}

                # If the ball collided with the left side of the brick
                # then store how far in it collided with that side of the brick.
                if (self.__left_x < brick.left_x
                        and self.__x_velocity > 0):
                    collision_depth["left"] = self.__right_x - brick.left_x

                # If the ball collided with the right side of the brick
                # then store how far in it collided with that side of the brick.
                if (self.__right_x + self.__radius > brick.right_x
                        and self.__x_velocity < 0):
                    collision_depth["right"] = brick.right_x - self.__left_x

                # If the ball collided with the top side of the brick
                # then store how far in it collided with that side of the brick.
                if (self.__top_y + self.__radius < brick.top_y
                        and self.__y_velocity > 0):
                    collision_depth["top"] = self.__bottom_y - brick.top_y

                # If the ball collided with the bottom side of the brick
                # then store how far in it collided with that side of the brick.
                if(self.__bottom_y + self.__radius > brick.bottom_y
                        and self.__y_velocity < 0):
                    collision_depth["bottom"] = brick.bottom_y - self.__top_y

                # Appends the Brick object and its collision depth in relevant directions
                # to the list of bricks that are to be removed.
                # The collision depths are stored to calculate which way the ball should bounce off.
                bricks_to_delete.append((brick, collision_depth))

        # If the ball hit 3 bricks, then reverse its x and y velocity so that
        # it goes back the way it came.
        # It compares to >= in case the ball somehow manages to hit more than 3 bricks.
        if len(bricks_to_delete) >= 3:
            self.__x_velocity = -self.__x_velocity
            self.__y_velocity = -self.__y_velocity

        # If the ball hit 2 bricks, then check if the bricks are in the same column or the same row.
        elif len(bricks_to_delete) == 2:

            # If the bricks are in the same column, then reverse the ball's x velocity.
            if bricks_to_delete[0][0].left_x == bricks_to_delete[1][0].left_x:
                self.__x_velocity = -self.x_velocity

            # If the bricks are in the same row, then reverse the ball's y velocity.
            elif bricks_to_delete[0][0].top_y == bricks_to_delete[1][0].top_y:
                self.__y_velocity = -self.__y_velocity

            # If the bricks aren't in the same row or column then that must mean that
            # they are diagonally adjacent and the ball hit the corner joining them,
            # so reverse the ball's x and y velocity.
            else:
                self.__x_velocity = -self.__x_velocity
                self.__y_velocity = -self.__y_velocity

        # If the ball hit 1 brick, then check how many edges of the brick that the ball
        # collided with.
        elif len(bricks_to_delete) == 1:

            # If the ball only collided with 1 edge of the brick, then change its velocity
            # depending on the edge hit.
            if len(bricks_to_delete[0][1]) == 1:

                # If the ball collided with the left or right edge of the brick,
                # then reverse its x velocity.
                if list(bricks_to_delete[0][1])[0] in ("left", "right"):
                    self.__x_velocity = -self.__x_velocity

                # If the ball collided with the top or bottom edge of the brick,
                # then reverse its y velocity.
                elif list(bricks_to_delete[0][1])[0] in ("top", "bottom"):
                    self.__y_velocity = -self.__y_velocity

            # If the ball collided with more than 1 edge, then change its velocity based on the edge
            # it collided least deeply with.
            else:

                # Stores the lowest depth that the ball collided into an edge with.
                lowest_collision_depth = None

                # Stores the edge that the ball collided with the lowest depth.
                direction = None

                # Iterates over the edges that the ball collided with.
                for key in bricks_to_delete[0][1]:

                    # If a lowest depth hasn't been stored yet, then store this depth and edge
                    # as the lowest depth.
                    if lowest_collision_depth is None:
                        lowest_collision_depth = bricks_to_delete[0][1][key]
                        direction = key

                    # Otherwise check that the collision depth for this edge is lower
                    # than the current lowest collision depth.
                    else:

                        # If the collision depth for this edge is lower than the current lowest
                        # collision depth, then store this depth and edge as the lowest depth.
                        if bricks_to_delete[0][1][key] < lowest_collision_depth:
                            lowest_collision_depth = bricks_to_delete[0][1][key]
                            direction = key

                # If the ball had the lowest collision depth with the left or right
                # edge of the brick, then reverse its x velocity.
                if direction in ("left", "right"):
                    self.__x_velocity = -self.__x_velocity

                # If the ball had the lowest collision depth with the top or bottom
                # edge of the brick, then reverse its y velocity.
                elif direction in ("top", "bottom"):
                    self.__y_velocity = -self.__y_velocity

        # Stores the score the player gained from destroying any bricks.
        score = 0

        # Iterates over the Brick objects that were hit by the ball.
        for brick in bricks_to_delete:

            # Adds the brick's score value to the score that the user wil gain.
            score += brick[0].score

            # Removes the brick from the canvas.
            self.__canvas.delete(brick[0].id)

            # Removes the Brick object from the list of all Brick objects in the game.
            self.__bricks.remove(brick[0])

        # Returns how much score the player gained from destroying any bricks.
        return score

    @property
    def id(self):
        """(int): The object ID of the ball when it is created on the canvas"""

        return self.__id

    @property
    def x_velocity(self):
        """(float): The velocity of the ball in the x direction (can be negative)"""

        return self.__x_velocity

    @x_velocity.setter
    def x_velocity(self, value):

        self.__x_velocity = value

    @property
    def y_velocity(self):
        """(float): The velocity of the ball in the y direction (can be negative)"""

        return self.__y_velocity

    @y_velocity.setter
    def y_velocity(self, value):

        self.__y_velocity = value

    @property
    def speed(self):
        """(float): The speed of the ball, or the magnitude of the ball's velocity"""

        return self.__speed

    @speed.setter
    def speed(self, value):

        self.__speed = value

    @property
    def bounces_until_speed_up(self):
        """(int): A counter that keeps track of how many more times the ball has to hit the paddle
                  before increasing the ball's speed"""

        return self.__bounces_until_speed_up

    @property
    def speed_up_amount(self):
        """(float): How much the ball will speed up by when it does"""

        return self.__speed_up_amount

    @property
    def radius(self):
        """(int): The radius of the ball"""

        return self.__radius

    @property
    def left_x(self):
        """(int): The x coordinate of the left edge of the ball"""

        return self.__left_x

    @left_x.setter
    def left_x(self, value):

        self.__left_x = value

    @property
    def top_y(self):
        """(int): The y coordinate of the top edge of the ball"""

        return self.__top_y

    @top_y.setter
    def top_y(self, value):

        self.__top_y = value

    @property
    def right_x(self):
        """(int): The x coordinate of the right edge of the ball"""

        return self.__right_x

    @right_x.setter
    def right_x(self, value):

        self.__right_x = value

    @property
    def bottom_y(self):
        """(int): The y coordinate of the bottom edge of the ball"""

        return self.__bottom_y

    @bottom_y.setter
    def bottom_y(self, value):

        self.__bottom_y = value

    @property
    def colour(self):
        """(str): The colour of the ball in the form #RRGGBB
        or any locally defined standard colour name"""

        return self.__canvas.itemcget(self.__id, "fill")

    @property
    def paddle_gap(self):
        """(int): The initial gap between the top of the paddle and the bottom of the ball"""

        return self.__paddle.top_y - self.__bottom_y

if __name__ == "__main__":
    print("Please run main.py")
