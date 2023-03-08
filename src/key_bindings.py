import json
import os
from PIL import Image, ImageTk
from tkinter import Canvas
import constants

class KeyBindings:
    """A class that represents when the program is in the edit key bindings state"""

    def __init__(self, window, key_bindings, boss_key):
        """Initialises KeyBindings and creates text on the screen to represent the key bindings
        the user can edit

        Parameters:
            window (Tk): The window that the key binding information will be drawn on
            key_bindings (dict[str: str]): A dictionary that maps the commands for the key
                                           bindings screen to the key binding
            boss_key (BossKey): A BossKey object that holds the boss key image and key bindings
        """

        # Assigns values to the object's attributes based on the arguments to the initialiser.
        self.__boss_key = boss_key

        # Loads the key bindings and stores them in a dictionary.
        self.__key_bindings = key_bindings

        # Gets the window's width and height.
        window_width = window.winfo_reqwidth()
        window_height = window.winfo_reqheight()

        # Stores whether or not the program should return to the main menu state or not.
        self.__finished = False

        # Creates a canvas for the whole window where the leaderboard's basic shapes and
        # text will be drawn onto.
        self.__canvas = Canvas(window, background="#000000", width=window_width,
                               height=window_height)
        self.__canvas.pack()

        # Gets the canvas's width and height.
        canvas_width = self.__canvas.winfo_reqwidth()
        canvas_height = self.__canvas.winfo_reqheight()

        # Stores which key binding the user is currently selecting.
        self.__selection = constants.KEY_BINDINGS_COMMANDS_ORDER[0]

        # Stores the order in which the user can toggle through the options in the key bindings.
        self.__selections = []

        # Maps the string key binding of what the user is currently selecting to the object IDs
        # of the text object commands and key bindings.
        self.__selection_to_object_id = {}

        # Creates the text objects on the canvas
        self.__create_text_objects()

        # Stores the object ID of the transparent background for the edit key binding state.
        self.__edit_key_binding_background = self.__create_transparent_background()

        # Stores the object ID for the text that tells the user to input their key binding.
        self.__user_prompt_message = self.__canvas.create_text(canvas_width/2, canvas_height/2 - 15,
                                                               text="Input your key binding",
                                                               fill="#FFFFFF",
                                                               font=("TkDefaultFont", 20),
                                                               state="hidden", anchor="s")

        # Stores the object ID for the error message text when the user inputs an invalid
        # key binding.
        self.__error_message = self.__canvas.create_text(canvas_width/2, canvas_height/2 + 15,
                                                         text="", fill="#FFFFFF",
                                                         font=("TkDefaultFont", 20), state="hidden",
                                                         anchor="n")

        # Binds the keybinds for the key bindings canvas.
        self.__canvas.bind("<KeyPress-" + key_bindings["Move Menu Pointer Up"] + ">",
                           self.__toggle_selection_up)
        self.__canvas.bind("<KeyPress-" + key_bindings["Move Menu Pointer Down"] + ">",
                           self.__toggle_selection_down)
        self.__canvas.bind("<KeyPress-" + key_bindings["Confirm Option"] + ">",
                           self.__confirm_selection)
        self.__canvas.bind("<KeyPress-" + key_bindings["Boss Key"] + ">",
                           lambda event : boss_key.show_boss_key(self.__canvas))

        # Causes the canvas to start looking for key inputs.
        self.__canvas.focus_set()

    def __create_text_objects(self):
        # Shows the key bindings on the screen.

        # Gets the width and height of the canvas.
        canvas_width = self.__canvas.winfo_reqwidth()
        canvas_height = self.__canvas.winfo_reqheight()

        # Calculates the x coordinate of the commands column.
        commands_x = canvas_width / 4

        # Calculates the x coordinate of the key binding column.
        key_binding_x = canvas_width * 3 / 4

        # Creates a "Command" heading text.
        self.__canvas.create_text(commands_x, 30, text="Command", fill="#FFFFFF",
                                  font=("TkDefaultFont", 20), anchor="n")

        # Creates a "Key Binding" heading text.
        key_binding_text = self.__canvas.create_text(key_binding_x, 30, text="Key Binding",
                                                     fill="#FFFFFF", font=("TkDefaultFont", 20),
                                                     anchor="n")

        # Calculates the height of the headings.
        heading_height = (self.__canvas.bbox(key_binding_text)[3]
                          - self.__canvas.bbox(key_binding_text)[1])

        # Stores the total heights of the previously created texts.
        # heading_height is multiplied by 1.5 to leave a small gap between the heading and entries.
        total_previous_object_height = 30 + 1.5 * heading_height

        # Stores the lowest value for a command's x coordinate.
        lowest_command_x = None

        # Iterates over each key binding command.
        for command in constants.KEY_BINDINGS_COMMANDS_ORDER:

            # Creates the command as text on the screen underneath the "Command" heading.
            command_text = self.__canvas.create_text(commands_x, total_previous_object_height,
                                                     text=command, fill="#FFFFFF",
                                                     font=("TkDefaultFont", 20), anchor="n")
            self.__selections.append(command)

            # Creates the key binding as text on the screen underneath the "Key Binding" heading.
            # The extra formatting for the text argument is needed as some Tkinter key binding names
            # are in all lowercase and not in the same format as others.
            key_binding_text = self.__canvas.create_text(key_binding_x,
                                                         total_previous_object_height,
                                                         text=(self.__key_bindings[command][0].upper()
                                                               + self.__key_bindings[command][1:].lower()),
                                                         fill="#FFFFFF", font=("TkDefaultFont", 20),
                                                         anchor="n")
            self.__selection_to_object_id[command] = (command_text, key_binding_text)

            # Adds the height of the newly created text to the total object height
            # so that new text is created underneath the newly created text.
            total_previous_object_height += (self.__canvas.bbox(command_text)[3]
                                             - self.__canvas.bbox(command_text)[1])

            # If there isn't a stored value for the lowest value for a command's x
            # coordinate, then store this command's x coordinate.
            if lowest_command_x is None:
                lowest_command_x = self.__canvas.bbox(command_text)[0]

            # If there is a stored value, then take the lowest of this command's
            # x coordinate and the stored x coordinate.
            else:
                lowest_command_x = min(lowest_command_x, self.__canvas.bbox(command_text)[0])

        # Iterates over all of the command text object IDs.
        for object_ids in self.__selection_to_object_id.values():

            # Makes it so that all of the commands line up on the left side.
            text_y = self.__canvas.coords(object_ids[0])[1]
            self.__canvas.coords(object_ids[0], lowest_command_x, text_y)
            self.__canvas.itemconfigure(object_ids[0], anchor="nw")

            # Makes it so that any text added to the left of the command text objects
            # won't move the rest of the text.
            text_x = self.__canvas.coords(object_ids[0])[0]
            text_width = self.__canvas.bbox(object_ids[0])[2] - self.__canvas.bbox(object_ids[0])[0]
            self.__canvas.coords(object_ids[0], text_x + text_width, text_y)
            self.__canvas.itemconfigure(object_ids[0], anchor="ne")

        # Calculates the gap from the bottom key binding to the bottom of the canvas.
        gap_from_canvas_bottom = canvas_height - total_previous_object_height

        # Creates the "Done" text centred below the key bindings and configures it so that
        # any text added to the left of the "Done" won't move it.
        done_text = self.__canvas.create_text(canvas_width/2,
                                              canvas_height - gap_from_canvas_bottom/2,
                                              text="Done", fill="#FFFFFF",
                                              font=("TkDefaultFont", 20))
        done_text_x = self.__canvas.coords(done_text)[0]
        done_text_y = self.__canvas.coords(done_text)[1]
        done_text_width = self.__canvas.bbox(done_text)[2] - self.__canvas.bbox(done_text)[0]
        self.__canvas.coords(done_text, done_text_x + done_text_width/2, done_text_y)
        self.__canvas.itemconfigure(done_text, anchor="e")
        self.__selections.append("Done")
        self.__selection_to_object_id["Done"] = (done_text,)

        # Makes it so that the selected option starts with "> ".
        self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection][0],
                                    text=f"> {self.__selection}")

    def __toggle_selection_up(self, event=None):
        # Changes the user's selection in the main menu to the one
        # above they have currently selected.

        # Gets the index of the option that the user has currently selected.
        selection_index = self.__selections.index(self.__selection)

        # If the user isn't trying to change to an option that is above the top option,
        # then change the text of the current selected option back to normal and
        # change to the option above the one they have selected.
        if selection_index != 0:
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection][0],
                                        text=self.__selection)
            self.__selection = self.__selections[selection_index - 1]
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection][0],
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
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection][0],
                                        text=self.__selection)
            self.__selection = self.__selections[selection_index + 1]
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection][0],
                                        text=f"> {self.__selection}")

    def __confirm_selection(self, event=None):
        # Calls methods to either return to the main menu or change a key binding based on what
        # the user currently has selected.

        # If the user's currently selected option is Done, then return to the main menu.
        if self.__selection == "Done":
            self.__exit_key_bindings()

        # If the user didn't select Done, then prompt the user to enter a key to replace
        # the key binding with.
        else:

            # Unbinds the old key binds.
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Up"] + ">")
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Down"] + ">")
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">")
            self.__canvas.unbind("<KeyPress-" + self.__key_bindings["Boss Key"] + ">")

            # Greys out the rest of the screen and tells the user to input their key binding.
            self.__canvas.itemconfigure(self.__edit_key_binding_background, state="normal")
            self.__move_to_top(self.__edit_key_binding_background)
            self.__canvas.itemconfigure(self.__user_prompt_message, state="normal")
            self.__move_to_top(self.__user_prompt_message)

            # Binds the next key that the user presses to be the new key binding for the selected
            # command if valid.
            self.__canvas.bind("<KeyPress>", self.__change_key_binding)

    def __change_key_binding(self, event):
        # Changes the key bindings for the command the user has selected to the key they inputted
        # unless it results in a key conflict in which case an error message is shown to the user.

        # Stores the user's inputted key bind.
        key_bind = None

        # If the user inputted an ASCII input on the computer, then the key bind is the non-shifted
        # version of that (e.g. ! would be 1).
        # [33, 126] are normal keyboard ASCII characters, 163 is £ and 172 is ¬.
        if 33 <= event.keysym_num <= 126 or event.keysym_num == 163 or event.keysym_num == 172:
            key_bind = chr(event.keysym_num).lower()
            key_bind = constants.SHIFT_CHARACTERS_TO_NON_SHIFT.get(key_bind, key_bind)

        # If the user inputted a non-ASCII character that is accepted, then that is the key bind.
        elif event.keysym in constants.ACCEPTED_KEYBIND_SPECIAL_CHARACTERS:
            key_bind = event.keysym

        # Stores the key bindings dictionary without the currently selected key binding in it.
        key_bindings_without_selection = self.__key_bindings.copy()
        key_bindings_without_selection.pop(self.__selection)

        # If the key bind that the user inputted is already binded to another command, then display
        # an error message to the user telling them this.
        if key_bind in key_bindings_without_selection.values():
            self.__canvas.itemconfigure(self.__error_message, state="normal",
                                        text="ERROR: That key is already bound to another command")
            self.__move_to_top(self.__error_message)
            key_bind = None

        # If the key bind the user inputted is valid then save it and reset the window to show the
        # key bindings and rebind the normal key bindings.
        if key_bind is not None:

            # Saves the new key binding.
            self.__key_bindings[self.__selection] = key_bind
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                     "key_bindings.json")
            with open(file_path, "wt", encoding="utf-8") as f:
                json.dump(self.__key_bindings, f)

            # Resets the window back to show the key bindings.
            self.__canvas.itemconfigure(self.__edit_key_binding_background, state="hidden")
            self.__canvas.itemconfigure(self.__user_prompt_message, state="hidden")
            self.__canvas.itemconfigure(self.__error_message, state="hidden", text="")

            # Updates the key binds on the key binding screen to show the updated one.
            self.__canvas.itemconfigure(self.__selection_to_object_id[self.__selection][1],
                                        text=(self.__key_bindings[self.__selection][0].upper()
                                              + self.__key_bindings[self.__selection][1:].lower()))

            # Unbinds the old key binds.
            self.__canvas.unbind("<KeyPress>")

            # Rebinds the normal key bindings.
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Up"] + ">",
                               self.__toggle_selection_up)
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Move Menu Pointer Down"] + ">",
                               self.__toggle_selection_down)
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Confirm Option"] + ">",
                               self.__confirm_selection)
            self.__canvas.bind("<KeyPress-" + self.__key_bindings["Boss Key"] + ">",
                               lambda event : self.__boss_key.show_boss_key(self.__canvas))

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

    def __create_transparent_background(self, alpha=220):
        # Creates the transparent background image for the game's edit key binding state
        # and stores the reference to this image in the __transparent_image attribute,
        # and then returns the object ID for the transparent background image.

        # Gets the canvas's width and height
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
                                          state="hidden")

    def __exit_key_bindings(self):
        # Exits the key binding editing screen and tells the program to go back to the main menu.

        # Causes the key binding canvas to not be drawn to the window.
        self.__canvas.pack_forget()

        # Tells the program that it should switch back to the main menu state.
        self.__finished = True

    @property
    def finished(self):
        """(bool): Whether or not the program should return to the main menu state or not"""

        return self.__finished

if __name__ == "__main__":
    print("Please run main.py")
