import json
import os
from tkinter import Canvas
import sys
from ball import Ball
from brick import Brick
from boss_key import BossKey
import constants
from game import Game
from key_bindings import KeyBindings
from leaderboard import Leaderboard
from paddle import Paddle

class MainMenu:
    """A class that represents when the program is in the main menu state"""

    def __init__(self, window):
        """Initialises MainMenu and creates text on the screen to represent the
        different options of the main menu

        Parameters:
            window (Tk): The window that the main menu will be drawn on"""

        # Assigns values to the object's attributes based on the arguments to the initialiser.
        self.__window = window

        # Gets the window's width and height.
        window_width = window.winfo_reqwidth()
        window_height = window.winfo_reqheight()

        # Creates a canvas for the whole window where the main menu's basic shapes and text
        # will be drawn onto.
        self.__canvas = Canvas(window, background="#000000", width=window_width,
                               height=window_height)
        self.__canvas.pack()

        # Stores the key bindings for the program.
        self.__key_bindings = self.__load_key_bindings()

        # Stores a BossKey object that holds the information for the boss key.
        self.__boss_key = BossKey(window, self.__key_bindings)

        # Stores the Game object (when the game starts).
        self.__game = None

        # Stores the Leaderboard object (when the leaderboard starts).
        self.__leaderboard = None

        # Stores the key bindings object (when the key bindings window is shown).
        self.__key_binding_object = None

        # Stores the ID of the main menu's game loop (when the game loop starts).
        self.__game_loop_id = None

        # Stores what the user is currently selecting on the main menu.
        self.__selection = "New Game"

        # Stores the order in which the user can toggle through the main menu options.
        self.__selections = []

        # Maps the string selections of what the user is currently selecting to the object IDs
        # of the text option.
        self.__selection_to_object_id = {}

        # Creates the different options for the main menu.
        self.__create_menu_option(400, 150, "New Game")
        self.__create_menu_option(400, 200, "Load Game")
        self.__create_menu_option(400, 250, "Leaderboard")
        self.__create_menu_option(400, 300, "Change Key Bindings")
        self.__create_menu_option(400, 350, "Quit")

        # Change the new game option for the main menu to > New Game as it is the first
        # option that should be selected.
        self.__canvas.itemconfigure(self.__selection_to_object_id["New Game"], text="> New Game")

        # Assigns key bindings for the main menu.
        self.__canvas.bind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Up"] + ">",
                           self.__toggle_selection_up)
        self.__canvas.bind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Down"] + ">",
                           self.__toggle_selection_down)
        self.__canvas.bind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">",
                           self.__confirm_selection)
        self.__canvas.bind("<KeyPress-" + self.__key_bindings["Boss Key"] + ">",
                           lambda event : self.__boss_key.show_boss_key(self.__canvas))

        # Causes the canvas to start looking for key inputs.
        self.__canvas.focus_set()

    def __create_menu_option(self, x, y, text, colour="#FFFFFF", font=("TkDefaultFont", 20)):
        # Creates a new menu option.

        # Stores the object ID for the new option.
        text_object_id = self.__canvas.create_text(x, y, text=text, fill=colour, font=font)
        self.__selections.append(text)
        self.__selection_to_object_id[text] = text_object_id

        # Gets the x and y coordinates for the centre of the new option.
        option_x = self.__canvas.coords(text_object_id)[0]
        option_y = self.__canvas.coords(text_object_id)[1]

        # Calculates the width of the new option.
        option_width = (self.__canvas.bbox(text_object_id)[2]
                        - self.__canvas.bbox(text_object_id)[0])

        # Changes the coordinates and anchor of the option text so that any characters
        # added to the left of the text won't move the rest of the text.
        # This is relevant when showing the user which option they have selected.
        self.__canvas.coords(text_object_id, option_x + option_width/2, option_y)
        self.__canvas.itemconfigure(text_object_id, anchor="e")

    def __toggle_selection_up(self, event=None):
        # Changes the user's selection in the main menu to the one
        # above they have currently selected.

        # Gets the index of the option that the user has currently selected.
        selection_index = self.__selections.index(self.__selection)

        # If the user isn't trying to change to an option that is above the top option,
        # then change the text of the current selected option back to normal and
        # change to the option above the one they have selected.
        if selection_index != 0:
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=self.__selection)
            self.__selection = self.__selections[selection_index - 1]
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=f"> {self.__selection}")

    def __toggle_selection_down(self, event=None):
        # Changes the user's selection in the main menu to the one
        # below they have currently selected.

        # Gets the index of the option that the user has currently selected.
        selection_index = self.__selections.index(self.__selection)

        # If the user isn't trying to change to an option that is below the bottom option,
        # then change the text of the current selected option back to normal and
        # change to the option below the one they have selected.
        if selection_index != len(self.__selections) - 1:
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=self.__selection)
            self.__selection = self.__selections[selection_index + 1]
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=f"> {self.__selection}")

    def __confirm_selection(self, event=None):
        # Calls methods to execute the main menu option that the user currently has selected.

        # If the user's currently selected option is New Game then start a new game.
        if self.__selection == "New Game":
            self.__new_game()

        # If the user's currently selected option is Load Game the load the saved game.
        # If there isn't a saved game then just start a new game.
        elif self.__selection == "Load Game":
            self.__new_game(load=True)

        # If the user's currently selected option is Leaderboard then show the leaderboard.
        elif self.__selection == "Leaderboard":
            self.__show_leaderboard()

        # If the user's currently selected option is Change Key Bindings then let the user
        # change the key bindings.
        elif self.__selection == "Change Key Bindings":
            self.__show_key_bindings()

        # If the user's currently selected option is Quit then quit the game.
        elif self.__selection == "Quit":
            self.__quit()

    def __new_game(self, load=False):
        # Creates a new game and blocks further MainMenu processes until the game is finished.

        # If there isn't a currently running game, then start a new game.
        if self.__game is None:

            # Causes the main menu's canvas to not be drawn to the window.
            self.__canvas.pack_forget()

            # Creates a new game.
            self.__game = Game(self.__window, self.__key_bindings, self.__boss_key)

            # If the game should be loaded then load the saved game data into the Game object.
            if load:
                self.__load_game()

            # Start a 1.5 second countdown in the game.
            self.__game.timer = 3
            self.__game.countdown()

            # Start the game's game loop.
            self.__game.game_loop()

            # Makes it so that the main menu checks if the game has finished every 17ms
            # (approximately 60 times per second).
            self.__game_loop_id = self.__canvas.after(17, self.__new_game)

        # If there is a currently running game and the game is finished,
        # then end the main menu's game loop, show the main menu,
        # and start looking for key inputs again.
        elif self.__game.game_finished:
            self.__canvas.after_cancel(self.__game_loop_id)
            self.__game = None
            self.__canvas.pack()
            self.__canvas.focus_set()

            # Changes the user's selected option to the New Game option.
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=self.__selection)
            self.__selection = "New Game"
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=f"> {self.__selection}")

        # If there is a currently running game and the game hasn't finished,
        # then check again later to see if the game has finished then.
        else:

            # Makes it so that the main menu checks if the game has finished every 17ms
            # (approximately 60 times per second).
            self.__game_loop_id = self.__canvas.after(17, self.__new_game)

    def __load_game(self):
        # Changes the attributes of the Game object in self.__game to match the saved game data.

        # Try to read the saved game data.
        try:

            # Read the saved game data into the data variable.
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                     "data.json")
            with open(file_path, "rt", encoding="utf-8") as f:
                data = json.load(f)

            # Split the saved game data into various different data dictionaries.
            game_data = data["game"]
            paddle_data = data["paddle"]
            ball_data = data["ball"]
            bricks_data = data["bricks"]

            # Gets the score and number of lives the user has.
            lives = game_data["lives"]
            score = game_data["score"]
            level = game_data["level"]

            # Gets the saved paddle data.
            paddle_width = paddle_data["width"]
            paddle_height = paddle_data["height"]
            paddle_canvas_gap = paddle_data["canvas_gap"]
            paddle_colour = paddle_data["colour"]
            paddle_left_x = paddle_data["left_x"]
            paddle_top_y = paddle_data["top_y"]
            paddle_right_x = paddle_data["right_x"]
            paddle_bottom_y = paddle_data["bottom_y"]

            # Gets the saved ball data.
            ball_x_velocity = ball_data["x_velocity"]
            ball_y_velocity = ball_data["y_velocity"]
            ball_bounces_until_speed_up = ball_data["bounces_until_speed_up"]
            ball_speed_up_amount = ball_data["speed_up_amount"]
            ball_radius = ball_data["radius"]
            ball_paddle_gap = ball_data["paddle_gap"]
            ball_colour = ball_data["colour"]
            ball_left_x = ball_data["left_x"]
            ball_top_y = ball_data["top_y"]
            ball_right_x = ball_data["right_x"]
            ball_bottom_y = ball_data["bottom_y"]
            ball_speed = ball_data["speed"]

            # Stores lists of the different attribute values for the bricks.
            bricks_attribute_values = []

            # Gets the saved data for each brick and stores it in a list.
            for brick_data in bricks_data:

                # Stores the different attribute values for the brick.
                brick_attribute_values = []

                # Gets the saved brick data and appends it to the list.
                brick_attribute_values.append(brick_data["x"])
                brick_attribute_values.append(brick_data["y"])
                brick_attribute_values.append(brick_data["score"])
                brick_attribute_values.append(brick_data["colour"])
                brick_attribute_values.append(brick_data["width"])
                brick_attribute_values.append(brick_data["height"])

                # Appends the list of saved brick data to the list of all saved brick datas.
                bricks_attribute_values.append(brick_attribute_values)

        # If the file can't be read or the data in the file isn't correctly formatted,
        # then stop trying to load the game.
        except (FileNotFoundError, KeyError):
            pass

        # If there were no errors, then change the values of the Game object's
        # attributes to the data in the saved file.
        else:

            # Changes the Game object attributes to the saved attribute values.
            self.__game.lives = lives
            self.__game.canvas.itemconfigure(self.__game.lives_text, text=f"Lives: {lives}")
            self.__game.score = score
            self.__game.canvas.itemconfigure(self.__game.score_text, text=f"Score: {score}")
            self.__game.level = level
            self.__game.canvas.itemconfigure(self.__game.level_text, text=f"Level {level}")

            # Creates a new Paddle with the saved attribute values.
            paddle = Paddle(self.__game.canvas, paddle_width, paddle_height, paddle_canvas_gap,
                            paddle_colour)

            # Changes the new Paddle object's attributes to the saved attribute values.
            paddle.left_x = paddle_left_x
            paddle.top_y = paddle_top_y
            paddle.right_x = paddle_right_x
            paddle.bottom_y = paddle_bottom_y
            self.__game.canvas.coords(paddle.id, paddle_left_x, paddle_top_y, paddle_right_x,
                                      paddle_bottom_y)

            # Removes the game's old paddle and replaces it with this new paddle.
            self.__game.canvas.delete(self.__game.paddle.id)
            self.__game.paddle = paddle

            # Holds all of the saved Brick objects.
            bricks = []

            # Iterates over all of the saved Brick object datas.
            for brick_attribute_values in bricks_attribute_values:

                # Creates a new Brick with the saved attributes and appends it to the list of
                # saved Bricks.
                brick = Brick(self.__game.canvas, brick_attribute_values[0],
                              brick_attribute_values[1], brick_attribute_values[2],
                              brick_attribute_values[3], brick_attribute_values[4],
                              brick_attribute_values[5])
                bricks.append(brick)

            # Iterates over all of the old bricks and deletes them
            for brick in self.__game.bricks:
                self.__game.canvas.delete(brick.id)

            # Replaces the old bricks list with the new bricks list.
            self.__game.bricks = bricks

            # Creates a new Ball with the saved attribute values.
            ball = Ball(self.__game.canvas, self.__game.paddle, self.__game.bricks,
                        self.__game.level, ball_x_velocity, ball_y_velocity,
                        ball_bounces_until_speed_up, ball_speed_up_amount, ball_radius,
                        ball_paddle_gap, ball_colour)

            # Changes the new Ball object's attributes to the saved attribute values.
            ball.left_x = ball_left_x
            ball.top_y = ball_top_y
            ball.right_x = ball_right_x
            ball.bottom_y = ball_bottom_y
            ball.speed = ball_speed
            self.__game.canvas.coords(ball.id, ball_left_x, ball_top_y, ball_right_x, ball_bottom_y)

            # Removes the game's old ball and replaces it with this new ball.
            self.__game.canvas.delete(self.__game.ball.id)
            self.__game.ball = ball

    def __show_leaderboard(self):
        # Shows the leaderboard on the screen and blocks further MainMenu processes
        # until the user exits the leaderboard.

        # If there isn't currently a leaderboard being shown, then show the leaderboard.
        if self.__leaderboard is None:

            # Causes the main menu's canvas to not be drawn to the window.
            self.__canvas.pack_forget()

            # Shows the leaderboard on the window.
            self.__leaderboard = Leaderboard(self.__window, self.__key_bindings, self.__boss_key)

            # Makes it so that the main menu checks if the user has exited
            # the leaderboard every 17ms
            # (approximately 60 times per second).
            self.__game_loop_id = self.__window.after(17, self.__show_leaderboard)

        # If there is a leaderboard being shown and the user has exited the leaderboard,
        # then end the main menu's game loop, show the main menu, and start looking
        # for key inputs again.
        elif self.__leaderboard.finished:
            self.__canvas.after_cancel(self.__game_loop_id)
            self.__leaderboard = None
            self.__canvas.pack()
            self.__canvas.focus_set()

            # Changes the user's selected option to the New Game option.
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=self.__selection)
            self.__selection = "New Game"
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=f"> {self.__selection}")

        # If there is a leaderboard being shown and the user hasn't exited the leaderboard,
        # then check again later to see if the user has exited the leaderboard then.
        else:

            # Makes it so that the main menu checks if the user has exited the leaderboard
            # every 17ms (approximately 60 times per second).
            self.__game_loop_id = self.__canvas.after(17, self.__show_leaderboard)

    def __show_key_bindings(self):
        # Shows the key bindings on the screen and blocks further MainMenu processes
        # until the user exits the key bindings screen.

        # If there isn't currently a key binding screen being shown, then show the
        # key binding screen.
        if self.__key_binding_object is None:

            # Unbinds the old key bindings for the main menu in case they are changed.
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Up"] + ">")
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Down"] + ">")
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">")
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Boss Key"] + ">")

            # Causes the main menu's canvas to not be drawn to the window.
            self.__canvas.pack_forget()

            # Shows the leaderboard on the window.
            self.__key_binding_object = KeyBindings(self.__window, self.__key_bindings,
                                                    self.__boss_key)

            # Makes it so that the main menu checks if the user has exited
            # the key binding screen every 17ms
            # (approximately 60 times per second).
            self.__game_loop_id = self.__window.after(17, self.__show_key_bindings)

        # If there is a key binding screen being shown and the user has exited
        # the key binding screen, then end the main menu's game loop, show the main menu,
        # and start looking for key inputs again.
        elif self.__key_binding_object.finished:
            self.__canvas.after_cancel(self.__game_loop_id)
            self.__key_binding_object = None
            self.__canvas.pack()
            self.__canvas.focus_set()

            # Rebinds the main menu's key bindings in case they were changed.
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Up"] + ">",
                               self.__toggle_selection_up)
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Down"] + ">",
                               self.__toggle_selection_down)
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">",
                               self.__confirm_selection)
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Boss Key"] + ">",
                               lambda event : self.__boss_key.show_boss_key(self.__canvas))

            # Also rebinds the boss key object's key bindings in case they were changed.
            self.__boss_key.canvas.bind("<KeyPress-" + self.__key_bindings["Boss Key"] + ">",
                                        lambda event : self.__boss_key.hide_boss_key())

            # Changes the user's selected option to the New Game option.
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=self.__selection)
            self.__selection = "New Game"
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection],
                                        text=f"> {self.__selection}")

        # If there is a key binding screen being shown and the user hasn't exited the key
        # binding screen, then check again later to see if the user has exited the key binding
        # screen then.
        else:

            # Makes it so that the main menu checks if the user has exited the key binding screen
            # every 17ms (approximately 60 times per second).
            self.__game_loop_id = self.__canvas.after(17, self.__show_key_bindings)

    def __quit(self):
        # Exits the program.

        # Destroys the window and then exits the program.
        self.__window.destroy()
        sys.exit()

    def __load_key_bindings(self):
        # Loads the key bindings from key_bindings.json and returns them,
        # or returns a set of default key bindings if the file can't be accessed.

        # Try to read the contents of key_bindings.json.
        try:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                     "key_bindings.json")
            with open(file_path, "rt", encoding="utf-8") as f:
                key_bindings = json.load(f)

        # If the contents of key_bindings.json can't be read, then create some default key bindings,
        # write them to key_bindings.json and return them.
        except FileNotFoundError:
            key_bindings = constants.DEFAULT_KEY_BINDINGS
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                     "key_bindings.json")
            with open(file_path, "wt", encoding="utf-8") as f:
                json.dump(key_bindings, f)
            return key_bindings

        # If key_bindings.json could be read, then set any non-defined commands in there with the
        # default key bindings and then return the key bindings.
        else:

            # Gets the keys of the loaded data.
            commands = key_bindings.keys()

            # Stores whether additional data had to be added to the loaded data to make it valid.
            data_added = False

            # Iterates over each of the key-value pairs in the default key bindings.
            for command, key_binding in constants.DEFAULT_KEY_BINDINGS.items():

                # If one of the default commands isn't given a key binding in the loaded data,
                # then add the default key binding to the loaded data.
                if command not in commands:
                    key_bindings[command] = key_binding
                    data_added = True

            # If data did have to be added to the loaded data to make it valid,
            # then write this new valid data to key_bindings.json.
            if data_added:
                file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                         "key_bindings.json")
                with open(file_path, "wt", encoding="utf-8") as f:
                    json.dump(key_bindings, f)

            return key_bindings

if __name__ == "__main__":
    print("Please run main.py")
