import csv
import json
import math
import os
from PIL import Image, ImageTk
from tkinter import Canvas, Entry, StringVar
from ball import Ball
from brick import Brick
import constants
from paddle import Paddle

class Game:
    """A class that represents when the program is in the game state

    Methods:
        game_loop(): Starts the game loop so that the paddle and ball start moving
    """

    def __init__(self, window, key_bindings, boss_key, lives=constants.DEFAULT_STARTING_LIVES,
                 level=constants.DEFAULT_STARTING_LEVEL):
        """Initialises Game and creates the paddle, ball and bricks for the game

        Parameters:
            window (Tk): The window that the game will be drawn on
            key_bindings (dict[str: str]): A dictionary that maps the commands for the game
                                           to the key binding
            boss_key (BossKey): A BossKey object that holds the boss key image and key bindings
            lives (int) (default 3): The number of lives the user has
            level (int) (default 1): The level the game is on
        """

        # Assigns values to the object's attributes based on the arguments to the initialiser.
        self.__window = window
        self.__key_bindings = key_bindings
        self.__lives = lives
        self.__level = level
        self.__boss_key = boss_key

        # Gets the window's width and height.
        window_width = window.winfo_reqwidth()
        window_height = window.winfo_reqheight()

        # Creates a canvas for the whole window where the game's basic shapes and text
        # will be drawn onto.
        self.__canvas = Canvas(window, background="#000000", width=window_width,
                               height=window_height)
        self.__canvas.pack()

        # Creates text in the top left corner of the canvas that tells the user
        # how many lives they have left.
        self.__lives_text = self.__canvas.create_text(10, 10, text=f"Lives: {self.__lives}",
                                                      fill="#FFFFFF", font=("TkDefaultFont", 20),
                                                      anchor="nw")

        # Gets the canvas's width and height.
        canvas_width = self.__canvas.winfo_reqwidth()
        canvas_height = self.__canvas.winfo_reqheight()

        # Creates text in the top middle of the canvas that tells the user the level they are on.
        self.__level_text = self.__canvas.create_text(canvas_width/2, 10, text=f"Level {level}",
                                                      fill="#FFFFFF", font=("TkDefaultFont", 20),
                                                      anchor="n")

        # Stores the user's score.
        self.__score = 0

        # Creates text in the top right corner of the canvas that tells the user their score.
        self.__score_text = self.__canvas.create_text(canvas_width - 10, 10,
                                                      text=f"Score: {self.__score}", fill="#FFFFFF",
                                                      font=("TkDefaultFont", 20), anchor="ne")

        # Stores whether or not the game is finished and should return back to the main menu state.
        self.__game_finished = False

        # Stores whether or not the game is over and the game over graphics should be displayed
        # or not.
        self.__game_over = False

        # Stores the ID of the game loop (when the game loop starts).
        self.__game_loop_id = None

        # Stores whether or not the game is in the paused state or not.
        self.__paused = False

        # Stores whether or not the game was paused or not before the boss key was called.
        self.__paused_before_boss_key = False

        # Stores a reference to the transparent background for the game's paused state.
        self.__transparent_image = None

        # Stores the object IDs of all objects used in the game's paused state in the stacking order
        # that they should be displayed in.
        self.__paused_object_ids = []

        # Stores the object ID of the transparent background for the game's paused state
        # and assigns the reference to the transparent background into self.__transparent_image.
        self.__paused_background = self.__create_transparent_background()
        self.__paused_object_ids.append(self.__paused_background)

        # Stores what the user is currently selecting on the pause menu.
        self.__pause_menu_selection = "Resume"

        # Stores the order in which the user can toggle through the pause menu options
        self.__pause_menu_selections = []

        # Maps the string selections of what the user is currently selecting to the object IDs
        # of the text option.
        self.__selection_to_object_id = {}

        # Stores the object ID of the pause menu background for the game's paused state.
        self.__pause_menu_background = self.__create_curved_rectangle_background(225, 150, 575, 350,
                                                                                 100,
                                                                                 fill="#696969",
                                                                                 state="hidden")
        self.__paused_object_ids.append(self.__pause_menu_background)

        # Creates the different options for the game's pause menu
        self.__create_menu_option(400, 200, "Resume")
        self.__create_menu_option(400, 250, "Save")
        self.__create_menu_option(400, 300, "Return to Main Menu")

        # Change the resume option for the game's pause menu text to > Resume as it is the first
        # option that should be selected.
        self.__canvas.itemconfigure(self.__selection_to_object_id["Resume"], text="> Resume")

        # Stores the Entry object for the game over screen when generated.
        self.__initials_entry = None

        # Stores a timer counter that is used to give the user time to prepare for the ball moving.
        self.__timer = 3

        # Stores whether or not a countdown is occuring or not.
        self.__countdown_occuring = False

        # Stores the countdowns after ID.
        self.__countdown_id = None

        # Stores the object ID of the text that displays the timer to the user.
        self.__timer_text = self.__canvas.create_text(canvas_width/2, canvas_height/2,
                                                      text=self.__timer, fill="#FFFFFF",
                                                      font=("TkDefualtFont", 50), state="hidden")

        # Creates a Paddle object to represent the paddle in the game.
        self.__paddle = Paddle(self.__canvas)

        # Creates multiple Brick objects to represent the bricks in the game
        # and then stores a list of those Brick objects.
        self.__bricks = self.__create_initial_bricks()

        # Creates a Ball object to represent the ball in the game.
        self.__ball = None
        self.__create_new_ball()

        # Assigns key bindings for the game
        self.__canvas.bind("<KeyPress-" + key_bindings["Move Paddle Left"] + ">",
                           self.__move_paddle_left)
        self.__canvas.bind("<KeyPress-" + key_bindings["Move Paddle Right"] + ">",
                           self.__move_paddle_right)
        self.__canvas.bind("<KeyRelease-" + key_bindings["Move Paddle Left"] + ">",
                           self.__stop_paddle)
        self.__canvas.bind("<KeyRelease-" + key_bindings["Move Paddle Right"] + ">",
                           self.__stop_paddle)
        self.__canvas.bind("<KeyPress-" + key_bindings["Pause Game"] + ">",
                           self.__toggle_pause)
        self.__canvas.bind("<KeyPress-" + key_bindings["Move Menu Pointer Up"] + ">",
                           self.__toggle_selection_up)
        self.__canvas.bind("<KeyPress-" + key_bindings["Move Menu Pointer Down"] + ">",
                           self.__toggle_selection_down)
        self.__canvas.bind("<KeyPress-" + key_bindings["Reset Ball Speed"] + ">",
                           self.__reset_ball_speed)
        self.__canvas.bind("<KeyPress-" + key_bindings["Set Lives to 10"] + ">",
                           lambda event : self.__set_lives(10))
        self.__canvas.bind("<KeyPress-" + key_bindings["Boss Key"] + ">", self.__show_boss_key)

        # Causes the canvas to start looking for key inputs.
        self.__canvas.focus_set()

    def __move_paddle_left(self, event=None):
        # Causes the paddle to move left.
        # The Paddle object's move method isn't directly called as otherwise the key bindings
        # would have to be rebound everytime the Paddle object instance changes.

        # Calls the Paddle object's method to move left.
        self.__paddle.move_left()

    def __move_paddle_right(self, event=None):
        # Causes the paddle to move right.
        # The Paddle object's move method isn't directly called as otherwise the key bindings
        # would have to be rebound everytime the Paddle object instance changes.

        # Calls the Paddle object's method to move right.
        self.__paddle.move_right()

    def __stop_paddle(self, event=None):
        # Causes the paddle to stop moving.
        # The Paddle object's move method isn't directly called as otherwise the key bindings
        # would have to be rebound everytime the Paddle object instance changes.

        # Calls the Paddle object's method to stop moving.
        self.__paddle.stop()

    def __create_initial_bricks(self, brick_height=constants.DEFAULT_BRICK_HEIGHT,
                      bricks_per_row=constants.DEFAULT_BRICKS_PER_ROW,
                      row_gap_from_top=constants.DEFAULT_ROW_GAP_FROM_TOP, colours=None):
        # Creates all of the initial bricks for the game and returns a list of the Brick objects.

        # Assigns the default value to the argument if one wasn't already given.
        if colours is None:
            colours = constants.DEFAULT_BRICK_COLOURS

        # A list that holds all of the bricks created.
        bricks = []

        # Gets the canvas's width.
        canvas_width = self.__canvas.winfo_reqwidth()

        # Calculates the width of each brick so that a row of bricks
        # takes up the whole canvas width.
        brick_width = int(canvas_width / bricks_per_row)

        # Iterates over the number of rows of bricks.
        for row, colour in enumerate(colours):

            # Iterates over the x coordinate of the top left corner of each brick.
            for x in range(0, bricks_per_row * brick_width, brick_width):

                # Calculates the x and y coordinates for the top left corner of the brick.
                # The coordinates are calculated so that a row of bricks takes up the
                # whole canvas width, and so that there is a space at the top of the canvas
                # for the ball to bounce in.
                brick_left_x = x
                brick_top_y = row * brick_height + row_gap_from_top * brick_height

                # Calculates the score that the brick will be worth based on which row it's in
                # (brick's in the top row will be worth more than bricks in the bottom row)
                brick_score = (len(colours) - row) * constants.DEFAULT_BRICK_SCORE

                # Creates a rectangle at the calculated coordinates in the right colour
                # for the row that the brick is in.
                # Appends the Brick object created to the bricks list.
                bricks.append(Brick(self.__canvas, brick_left_x, brick_top_y, brick_score, colour,
                                    brick_width, brick_height))

        # Returns the list of Brick objects.
        return bricks

    def __create_transparent_background(self, alpha=100, state="hidden"):
        # Creates the transparent background image for the game's paused state and stores the
        # reference to this image in the __transparent_image attribute, and then returns the
        # object ID for the transparent background image.

        # Gets the canvas's width and height.
        canvas_width = self.__canvas.winfo_reqwidth()
        canvas_height = self.__canvas.winfo_reqheight()

        # Creates a PIL image that is a mono-colour semi-transparent black image that takes
        # up the whole canvas with its size.
        # This is created through the Pillow module to allow alpha transparency.
        image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, alpha))

        # Converts the PIL image into a Tkinter PhotoImage and stores a reference to this image.
        self.__transparent_image = ImageTk.PhotoImage(image)

        # Returns the object ID of the transparent background image.
        return self.__canvas.create_image(0, 0, image=self.__transparent_image, anchor="nw",
                                          state=state)

    def __create_curved_rectangle_background(self, left_x, top_y, right_x, bottom_y, radius,
                                             **kwargs):
        # Creates the pause menu background for the game's paused state
        # and returns the object ID for it.
        # The coordinates passed in are the coordinates for the rectangle surrounding
        # the curved rectangle.
        # The radius is how much the corners of the curved rectangle should be curved.
        # The keyword arguments can be any optional arguments that would be passed
        # to Tkinter's canvas.create_polygon().

        # Calculates the points of the curved rectangle polygon that will be made.
        # Is in the form [x1, y1, x2, y2, x3, y3, ..., xn, yn].
        # Points that are repeated (e.g. [..., x1, y1, x1, y1, x2, y2, x2, y2...]) is
        # used by Tkinter to indicate that the line between (x1, y1) and (x2, y2)
        # is supposed to be straight.
        coordinates = [left_x + radius, top_y, left_x + radius, top_y, right_x - radius, top_y,
                       right_x - radius, top_y, right_x, top_y, right_x, top_y + radius, right_x,
                       top_y + radius, right_x, bottom_y - radius, right_x, bottom_y - radius,
                       right_x, bottom_y, right_x - radius, bottom_y, right_x - radius, bottom_y,
                       left_x + radius, bottom_y, left_x + radius, bottom_y, left_x, bottom_y,
                       left_x, bottom_y - radius, left_x, bottom_y - radius, left_x, top_y + radius,
                       left_x, top_y + radius, left_x, top_y]

        # Returns the object ID of the smooth curved rectangle polygon created
        return self.__canvas.create_polygon(coordinates, smooth=1, **kwargs)

    def __create_menu_option(self, x, y, text, colour="#FFFFFF", font=("TkDefaultFont", 20)):
        # Creates a new pause menu option.

        # Stores the object ID for the new option.
        text_object_id = self.__canvas.create_text(x, y, text=text, fill=colour, font=font)
        self.__paused_object_ids.append(text_object_id)
        self.__pause_menu_selections.append(text)
        self.__selection_to_object_id[text] = text_object_id

        # Gets the x and y coordinates for the centre of the new option.
        option_x = self.__canvas.coords(text_object_id)[0]
        option_y = self.__canvas.coords(text_object_id)[1]

        # Calculates the width of the new option.
        option_width = self.__canvas.bbox(text_object_id)[2] - self.__canvas.bbox(text_object_id)[0]

        # Changes the coordinates and anchor of the option text so that any characters
        # added to the left of the text won't move the rest of the text.
        # This is relevant when showing the user which option they have selected.
        # Also hides the new option text.
        self.__canvas.coords(text_object_id, option_x + option_width/2, option_y)
        self.__canvas.itemconfigure(text_object_id, anchor="e", state="hidden")

    def __move_to_top(self, object_id):
        # Moves the object with the object ID passed in to the top of the stacking order.

        # Gets the object ID of the object above the object ID passed into the method
        # in the stacking order.
        object_above = self.__canvas.find_above(object_id)

        # Iterates whilst the object with the object ID passed into the method
        # isn't at the top the stacking order (isn't in the foreground).
        while object_above:

            # Moves the object with the object ID passed into the method above the object above it
            # in the stacking order.
            self.__canvas.tag_raise(object_id, object_above)

            # Gets the object ID of the next object above the object ID passed into the method
            # in the stacking order.
            object_above = self.__canvas.find_above(object_id)

    def __lose_life(self):
        # Makes the user lose 1 life and displays a game over message if neccessary.

        # Makes the player lose a life and updates the lives text in the game.
        self.__lives -= 1
        self.__canvas.itemconfigure(self.__lives_text, text=f"Lives: {self.__lives}")

        # Resets the paddle back to the middle of the game.
        self.__reset_paddle()

        # Resets the ball back to the middle of the game.
        self.__create_new_ball()

        # If the player has no more lives then display the game over menu.
        if self.__lives == 0:
            self.__show_game_over()

        # If the game isn't over, then start a 1.5 second countdown.
        else:
            self.__timer = 3
            self.countdown()

    def __reset_paddle(self):
        # Resets the paddle back to the starting position.

        # Removes the old paddle from the game.
        self.__canvas.delete(self.__paddle.id)

        # Creates a new paddle with the default arguments
        # so that it's created at the default starting position.
        new_paddle = Paddle(self.__canvas)

        # Copies all of the relevant attributes of the new paddle to the current paddle
        # so that the current instance of the paddle acts as the new instance of the paddle.
        # This is done so that the instance of the Paddle object stored in the Ball object
        # won't have to change.
        self.__paddle.id = new_paddle.id
        self.__paddle.left_x = new_paddle.left_x
        self.__paddle.top_y = new_paddle.top_y
        self.__paddle.right_x = new_paddle.right_x
        self.__paddle.bottom_y = new_paddle.bottom_y
        self.__paddle.width = new_paddle.width

    def __create_new_ball(self):
        # Resets the ball back to the starting position and applies level scaling.

        # Removes the old ball from the game if there was a ball previously.
        if self.__ball is not None:
            self.__canvas.delete(self.__ball.id)

        # Adjusts some of the default arguments for the Ball object to make further levels harder.
        ball_bounces_until_speed_up = max(1, constants.DEFAULT_BOUNCES_UNTIL_SPEED_UP
                                             - self.__level + 1)
        ball_speed_up_amount = constants.DEFAULT_SPEED_UP_AMOUNT * 1.2**(self.__level - 1)
        ball_y_velocity = constants.DEFAULT_BALL_SPEED * 1.2**(self.__level - 1)

        # Creates a new ball with the default arguments so that it's created at the default
        # starting position.
        self.__ball = Ball(self.__canvas, self.__paddle, self.__bricks, self.__level,
                           y_velocity=ball_y_velocity,
                           bounces_until_speed_up=ball_bounces_until_speed_up,
                           speed_up_amount=ball_speed_up_amount)

        # Adjusts some of the ball's attributes to make the game exponentially more difficult
        # in further levels.
        self.__ball.speed = constants.DEFAULT_BALL_SPEED *  1.2 ** (self.__level - 1)

    def __show_game_over(self):
        # Shows the game over menu, prompts the user to enter their initials
        # and then returns to the main menu.

        # Causes the main game loop to stop.
        self.__game_over = True

        # Covers the screen in a semi-transparent black background.
        self.__create_transparent_background(210, "normal")

        # Creates a grey curved rectangle background for the game over screen.
        self.__create_curved_rectangle_background(250, 100, 550, 400, 100, fill="#696969")

        # Creates a Tkinter string variable which will store what the user inputs.
        initials = StringVar()

        # Whenever the Tkinter string variable is written to,
        # call __check_valid() to make sure it's only 2 characters long and upper case letters.
        initials.trace("w", lambda *args : self.__check_valid(initials))

        # Creates the text and input box for the game over screen.
        self.__canvas.create_text(400, 150, fill="#FFFFFF", font=("TkDefaultFont", 20),
                                  text="Game Over")
        self.__canvas.create_text(400, 200, fill="#FFFFFF", font=("TkDefaultFont", 20),
                                  text=f"Score: {self.__score}")
        self.__canvas.create_text(400, 250, fill="#FFFFFF", font=("TkDefaultFont", 20),
                                  text="Enter your initials:")
        self.__initials_entry = Entry(self.__window, background="#000000", foreground="#FFFFFF",
                                    insertbackground="#FFFFFF", font=("TkDefaultFont", 20),
                                    textvariable=initials, width=3, justify="center")
        self.__canvas.create_window(400, 300, window=self.__initials_entry)

        # Configures the "> Done" text so that the "Done" is centred
        # and the "> " is to the left of it.
        done_text_id = self.__canvas.create_text(400, 350, fill="#FFFFFF",
                                                 font=("TkDefaultFont", 20), text="Done")
        done_text_x = self.__canvas.coords(done_text_id)[0]
        done_text_y = self.__canvas.coords(done_text_id)[1]
        done_text_width = self.__canvas.bbox(done_text_id)[2] - self.__canvas.bbox(done_text_id)[0]
        self.__canvas.coords(done_text_id, done_text_x + done_text_width/2, done_text_y)
        self.__canvas.itemconfigure(done_text_id, anchor="e", text="> Done")

        # Unbinds the old keybinds.
        self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Paddle Left"] + ">")
        self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Paddle Right"] + ">")
        self.__canvas.unbind("<KeyRelease-" + self.__key_bindings["Move Paddle Left"] + ">")
        self.__canvas.unbind("<KeyRelease-" + self.__key_bindings["Move Paddle Right"] + ">")
        self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Pause Game"] + ">")
        self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Up"] + ">")
        self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Down"] + ">")

        # Binds new keybinds to confirm what the user inputted.
        self.__canvas.bind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">",
                           lambda event : self.__finish_game(initials.get()))
        self.__initials_entry.bind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">",
                                 lambda event : self.__finish_game(initials.get()))
        self.__initials_entry.bind("<KeyPress-" + self.__key_bindings["Boss Key"] + ">",
                                   self.__show_boss_key)

        # Causes the text cursor to automatically start in the Entry box
        # without needing the user to click in it.
        self.__initials_entry.focus_set()

    def __check_valid(self, variable):
        # Makes the Tkinter string variable only contain the first 2 characters
        # and makes it uppercase.

        # Gets the value of the Tkinter string variable.
        text = variable.get()

        # Overwrites the string with the first 2 characters of itself and makes it uppercase.
        text = text[:2]
        text = text.upper()
        variable.set(text)

    def __finish_game(self, initials):
        # Stores the user's score on the leaderboard with their initials if they entered any
        # and their score is within the top 10, and then returns the program back to the main menu.

        # If the user entered some initials, then store their score on the leaderboard
        # if their score is within the top 10.
        if initials:
            self.__store_on_leaderboard(initials)

        # Causes the game's canvas to not be drawn to the window.
        self.__canvas.pack_forget()

        # Tells the program that the game has finished and to switch back to
        # the main menu state.
        self.__game_finished = True

    def __store_on_leaderboard(self, initials):
        # Stores the user's score on the leaderboard with their initials
        # if their score is within the top 10.

        # Open the leaderboard.csv file to check that the user is in the top 10.
        try:

            # Opens leaderboard.csv and appends the data into a list.
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                     "leaderboard.csv")
            with open(file_path, "rt", encoding="utf-8") as f:
                csv_reader = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
                scores = []
                for row in csv_reader:
                    scores.append(row)

        # If the leaderboard file doesn't exist then create a new file.
        except FileNotFoundError:

            # Writes the user's inputted initials and score to the csv file.
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                     "leaderboard.csv")
            with open(file_path, "wt", encoding="utf-8", newline="") as f:
                csv_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
                csv_writer.writerow([initials, self.__score])

        # If the file did exist, then check if the user's score should be added to the leaderboard
        else:

            # If there are less than 10 scores in the leaderboard, or the user's score is greater
            # than or equal to the 10th score on the leaderboard, then add the user's score
            # to the leaderboard.
            if len(scores) < 10 or self.__score >= scores[9][1]:
                self.__insert_into_list(scores, [initials, self.__score])

                # Makes it so that only the top 10 scores are stored on the leaderboard.
                scores = scores[:10]

                # Writes the new top 10 scores to the leaderboard.
                file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                         "leaderboard.csv")
                with open(file_path, "wt", encoding="utf-8", newline="") as f:
                    csv_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
                    for row in scores:
                        csv_writer.writerow(row)

    def __insert_into_list(self, two_d_list, list_to_insert):
        # Inserts a list into the 2d list based on the second index of each element.

        # i holds the end index of the sorted part of the list.
        i = len(two_d_list) - 1

        # Increase the 2d list's size to allow the list to be inserted.
        two_d_list.append([])

        # Moves all elements in the sorted part of the 2d list that have a lower second
        # index value than the list argument's second index to the right.
        while i >= 0 and list_to_insert[1] >= two_d_list[i][1]:
            two_d_list[i + 1] = two_d_list[i]
            i -= 1

        # Inserts the list argument where the last element that moved originally was.
        two_d_list[i + 1] = list_to_insert

    def __toggle_pause(self, event=None):
        # Toggles whether the game is in the paused state or not.

        # If the game wasn't in the paused state then set it into the paused state
        # and show the relevant paused state objects in the foreground.
        if not self.__paused:
            self.__paused = True
            for object_id in self.__paused_object_ids:
                self.__canvas.itemconfigure(object_id, state="normal")
                self.__move_to_top(object_id)

            # If there is a countdown, then stop it.
            if self.__countdown_occuring:
                self.__canvas.after_cancel(self.__countdown_id)
                self.__countdown_occuring = False

            # Binds the user pressing the relevant key binding to selecting the pause menu option
            # they have selected.
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">",
                               self.__confirm_selection)

            # Set the initial option the user has selected in the pause menu to the Resume option
            # if it isn't already.
            if self.__pause_menu_selection != "Resume":
                self.__canvas.itemconfigure(self.__selection_to_object_id[self.__pause_menu_selection],
                                            text=self.__pause_menu_selection)
                self.__pause_menu_selection = "Resume"
                self.__canvas.itemconfigure(self.__selection_to_object_id[self.__pause_menu_selection],
                                            text=f"> {self.__pause_menu_selection}")

        # If the game was in the paused state then set it out of the paused state
        # and hide the relevant paused state objects.
        else:
            self.__paused = False
            for object_id in self.__paused_object_ids:
                self.__canvas.itemconfigure(object_id, state="hidden")

            # Unbinds the user pressing the relevant key binding to selecting the pause menu option
            # they have selected so that the user can't select options when the game is unpaused.
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">")

            # Starts a 1.5 second countdown.
            self.__timer = 3
            self.countdown()

    def __toggle_selection_up(self, event=None):
        # Changes the user's selection in the pause menu to the one
        # above they have currently selected.

        # Gets the index of the option that the user has currently selected.
        selection_index = self.__pause_menu_selections.index(self.__pause_menu_selection)

        # If the user isn't trying to change to an option that is above the top option,
        # then change the text of the current selected option back to normal and
        # change to the option above the one they have selected.
        if selection_index != 0:
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__pause_menu_selection],
                                        text=self.__pause_menu_selection)
            self.__pause_menu_selection = self.__pause_menu_selections[selection_index - 1]
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__pause_menu_selection],
                                        text=f"> {self.__pause_menu_selection}")

    def __toggle_selection_down(self, event=None):
        # Changes the user's selection in the pause menu to the one
        # below they have currently selected.

        # Gets the index of the option that the user has currently selected.
        selection_index = self.__pause_menu_selections.index(self.__pause_menu_selection)

        # If the user isn't trying to change to an option that is below the bottom option,
        # then change the text of the current selected option back to normal and
        # change to the option below the one they have selected.
        if selection_index != len(self.__pause_menu_selections) - 1:
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__pause_menu_selection],
                                        text=self.__pause_menu_selection)
            self.__pause_menu_selection = self.__pause_menu_selections[selection_index + 1]
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__pause_menu_selection],
                                        text=f"> {self.__pause_menu_selection}")

    def __confirm_selection(self, event=None):
        # Calls methods to execute the pause menu option that the user currently has selected.

        # If the user's currently selected option is Resume then unpause the game.
        if self.__pause_menu_selection == "Resume":
            self.__toggle_pause()

        # If the user's currently selected option is Save the save the game.
        elif self.__pause_menu_selection == "Save":
            self.__save_game()

        # If the user's currently selected option is Return to Main Menu then
        # return to the main menu by ending the game loop.
        elif self.__pause_menu_selection == "Return to Main Menu":
            self.__canvas.after_cancel(self.__game_loop_id)

            # Causes the game's canvas to not be drawn to the window.
            self.__canvas.pack_forget()

            # Tells the program that the game has finished and to switch back to
            # the main menu state.
            self.__game_finished = True

    def __save_game(self):
        # Saves all of the relevant game information into data.json.

        # Data structures that will store all of the data necessary to save the game.
        data = {}
        game_data = {}
        paddle_data = {}
        ball_data = {}
        bricks_data = []

        # Stores all of the relevant game data into the data dictionary.
        game_data["lives"] = self.__lives
        game_data["score"] = self.__score
        game_data["level"] = self.__level
        data["game"] = game_data

        # Stores all of the relevant paddle data into the data dictionary.
        paddle_data["left_x"] = self.__paddle.left_x
        paddle_data["top_y"] = self.__paddle.top_y
        paddle_data["right_x"] = self.__paddle.right_x
        paddle_data["bottom_y"] = self.__paddle.bottom_y
        paddle_data["width"] = self.__paddle.width
        paddle_data["height"] = self.__paddle.height
        paddle_data["colour"] = self.__paddle.colour
        paddle_data["canvas_gap"] = self.__paddle.canvas_gap
        data["paddle"] = paddle_data

        # Stores all of the relevant ball data into the data dictionary.
        ball_data["x_velocity"] = self.__ball.x_velocity
        ball_data["y_velocity"] = self.__ball.y_velocity
        ball_data["speed"] = self.__ball.speed
        ball_data["bounces_until_speed_up"] = self.__ball.bounces_until_speed_up
        ball_data["speed_up_amount"] = self.__ball.speed_up_amount
        ball_data["radius"] = self.__ball.radius
        ball_data["left_x"] = self.__ball.left_x
        ball_data["top_y"] = self.__ball.top_y
        ball_data["right_x"] = self.__ball.right_x
        ball_data["bottom_y"] = self.__ball.bottom_y
        ball_data["colour"] = self.__ball.colour
        ball_data["paddle_gap"] = self.__ball.paddle_gap
        data["ball"] = ball_data

        # Iterates over each Brick object in the game.
        for brick in self.__bricks:

            # Stores all of the relevant brick data into the bricks_data list.
            brick_data = {}
            brick_data["x"] = brick.left_x
            brick_data["y"] = brick.top_y
            brick_data["width"] = brick.width
            brick_data["height"] = brick.height
            brick_data["score"] = brick.score
            brick_data["colour"] = brick.colour
            bricks_data.append(brick_data)

        # Stores the bricks data into the data dictionary.
        data["bricks"] = bricks_data

        # Writes the data necessary to save the game into a JSON file.
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                 "data.json")
        with open(file_path, "wt", encoding="utf-8") as f:
            json.dump(data, f)

    def __next_level(self):
        # Causes the game to go onto the next level.

        # Increases the game's level.
        self.__level += 1
        self.__canvas.itemconfigure(self.__level_text, text=f"Level {self.__level}")

        # Creates a new set of bricks for the game.
        self.__bricks = self.__create_initial_bricks()

        # Resets the paddle back to the middle of the game.
        self.__reset_paddle()

        # Resets the ball back to the middle of the game and applies level scaling.
        self.__create_new_ball()

        # Starts a 1.5 second countdown.
        self.__timer = 3
        self.countdown()

    def __reset_ball_speed(self, event=None):
        # Resets the ball's speed back to the default value.

        # Sets the ball's speed back to the default value.
        self.__ball.speed = constants.DEFAULT_BALL_SPEED

        # Calculates the angle that the ball is travelling at.
        # The angle is taken anti-clockwise from the positive x-axis.
        angle = math.atan2(self.__ball.y_velocity, self.__ball.x_velocity)

        # Updates the ball's velocities so that it still travels in the same direction but
        # with the updated speed.
        self.__ball.x_velocity = self.__ball.speed * math.cos(angle)
        self.__ball.y_velocity = self.__ball.speed * math.sin(angle)

    def __set_lives(self, value):
        # Sets the number of lives the user has to the argument.

        self.__lives = value
        self.__canvas.itemconfigure(self.__lives_text, text=f"Lives: {self.__lives}")

    def __show_boss_key(self, event=None):
        # Shows the boss key on the screen and pauses the game processes.

        # Causes the game to pause without displaying the pause menu and keeps track of
        # whether the game was paused or not before the boss key was called.
        self.__paused_before_boss_key = self.__paused
        self.__paused = True

        # If there is a countdown, then stop it.
        if self.__countdown_occuring:
            self.__canvas.after_cancel(self.__countdown_id)
            self.__countdown_occuring = False

        # When the game's canvas gets the focus again (which will happen when the boss
        # key image is hidden), call a method that causes the game to resume as normal.
        self.__canvas.bind("<FocusIn>", self.__hide_boss_key)

        # Causes the boss key image to be shown over the game.
        self.__boss_key.show_boss_key(self.__canvas)

    def __hide_boss_key(self, event=None):
        # Causes the game to resume as normal after the boss key image has been hidden.

        # Unbinds the binding that is intended to trigger when the boss key image is hidden.
        self.__canvas.unbind("<FocusIn>")

        # Causes the game to unpause or pause depending on what state it was before the boss
        # key was called.
        self.__paused = self.__paused_before_boss_key

        # If the game is in the game over state, then set the focus to the user input entry.
        if self.__game_over:
            self.__initials_entry.focus_set()

        # Otherwise, start a 1.5 second countdown.
        else:
            self.__timer = 3
            self.countdown()

    def countdown(self, event=None):
        """Causes a countdown to appear on the centre of the screen based on the timer attribute,
        makes it so that the user can't move the paddle, and makes the ball not move

        The length of the countdown is half the value of the timer attribute in seconds.

        Parameters:
            event (Event) (default None): The Event object that is passed in by default
                                          due to Tkinter key bindings.
                                          This can be any value or data type if you aren't
                                          using Tkinter key bindings.
        """

        # The countdown only appears if the game isn't paused.
        if not self.__paused:

            # Unbinds the keys that move the paddle.
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Paddle Left"] + ">")
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Paddle Right"] + ">")

            # Shows the timer in the middle of the screen with a transparent background.
            self.__canvas.itemconfigure(self.__paused_background, state="normal")
            self.__move_to_top(self.__paused_background)
            self.__canvas.itemconfigure(self.__timer_text, state="normal", text=self.__timer)
            self.__move_to_top(self.__timer_text)

            # Decrements the timer.
            self.__timer -= 1

            # Sets the attribute that keeps track of if there is a countdown or not to True.
            self.__countdown_occuring = True

            # If the timer is less than 0, then hide the timer and background and rebind the keys to
            # move the paddle.
            if self.__timer < 0:
                self.__canvas.bind("<KeyPress-" + self.__key_bindings["Move Paddle Left"] + ">",
                                   self.__move_paddle_left)
                self.__canvas.bind("<KeyPress-" + self.__key_bindings["Move Paddle Right"] + ">",
                                   self.__move_paddle_right)
                self.__canvas.itemconfigure(self.__paused_background, state="hidden")
                self.__canvas.itemconfigure(self.__timer_text, state="hidden")
                self.__countdown_occuring = False

            # If the timer is greater than or equal to 0, then call this method again
            # in 1 second to update the timer on screen.
            else:
                self.__countdown_id = self.__canvas.after(500, self.countdown)

    def game_loop(self):
        """Continuously calls methods that move the ball and paddle,
        and displays the pause menu when the game is paused

        This only needs to be called once as it repeatedly calls itself until the program ends.
        """

        # If the game isn't paused and a countdown isn't occuring, then move the ball and
        # paddle and update lives and score accordingly.
        if not self.__paused and not self.__countdown_occuring:

            # Causes the paddle to move based on its speed.
            self.__paddle.move()

            # Causes the ball to move based on its velocity,
            # and then return whether the user should lose lives or not
            # and any score the user gained from destroying bricks.
            lose_life, score = self.__ball.move()

            # Add the score that the player gained from destroying bricks to their total score
            # with higher level bricks being worth a higher score.
            self.__score += self.__level * score

            # Updates the score text in the game.
            self.__canvas.itemconfigure(self.__score_text, text=f"Score: {self.__score}")

            # If the user should lose lives then call the method for that to happen.
            if lose_life:
                self.__lose_life()

            # If there are no more bricks left, then go onto the next level
            # and fill the screen with bricks again.
            if not self.__bricks:
                self.__next_level()

        # If the game isn't over, then repeatedly call the game loop.
        if not self.__game_over:

            # Makes it so that the paddle and ball are moved every 17ms
            # (approximately 60 times per second).
            self.__game_loop_id = self.__canvas.after(17, self.game_loop)

    @property
    def game_finished(self):
        """(bool): Whether the game is finished or not and should return back to the
        main menu state"""

        return self.__game_finished

    @property
    def lives(self):
        """(int): The number of lives the user has"""

        return self.__lives

    @lives.setter
    def lives(self, value):

        self.__lives = value

    @property
    def lives_text(self):
        """(int): The object ID for the text displaying the user's lives in the game"""

        return self.__lives_text

    @property
    def score(self):
        """(int): The score the user has"""

        return self.__score

    @score.setter
    def score(self, value):

        self.__score = value

    @property
    def score_text(self):
        """(int): The object ID for the text displaying the user's score in the game"""

        return self.__score_text

    @property
    def level(self):
        """(int): The level that the game is on."""

        return self.__level

    @property
    def level_text(self):
        """(int): The object ID for the text displaying the game's level"""

        return self.__level_text

    @level.setter
    def level(self, value):

        self.__level = value

    @property
    def canvas(self):
        """(Canvas): The Canvas object that the game's objects are drawn on"""

        return self.__canvas

    @property
    def paddle(self):
        """(Paddle): The Paddle object that represents the game's paddle"""

        return self.__paddle

    @paddle.setter
    def paddle(self, value):

        self.__paddle = value

    @property
    def bricks(self):
        """(List[Brick]): A list of Brick objects that represents the game's bricks"""

        return self.__bricks

    @bricks.setter
    def bricks(self, value):

        self.__bricks = value

    @property
    def ball(self):
        """(Ball): The Ball object that represets the game's ball"""

        return self.__ball

    @ball.setter
    def ball(self, value):

        self.__ball = value

    @property
    def timer(self):
        """(int): The number the countdown should be when the countdown() method is called.

        The length of the countdown is half the value of the timer attribute in seconds."""

        return self.__timer

    @timer.setter
    def timer(self, value):

        self.__timer = value

if __name__ == "__main__":
    print("Please run main.py")
