import csv
import os
from tkinter import Canvas

class Leaderboard:
    """A class that represents when the program is in the leaderboard state"""

    def __init__(self, window, key_bindings, boss_key):
        """Initialises Leaderboard and creates text on the screen to represent the data
        in the leaderboard

        Parameters:
            window (Tk): The window that the leaderboard will be drawn on
            key_bindings (dict[str: str]): A dictionary that maps the commands for the
                                           leaderboard to the key binding
            boss_key (BossKey): A BossKey object that holds the boss key image and key bindings
        """

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

        # Loads the leaderboard data and shows it on the screen.
        self.__load_leaderboard()

        # Binds the keybinds for the leaderboard.
        self.__canvas.bind("<KeyPress-" + key_bindings["Confirm Option"] + ">",
                           self.__exit_leaderboard)
        self.__canvas.bind("<KeyPress-" + key_bindings["Boss Key"] + ">",
                           lambda event : boss_key.show_boss_key(self.__canvas))

        # Causes the canvas to start looking for key inputs.
        self.__canvas.focus_set()

    def __load_leaderboard(self):
        # Loads the leaderboard from leaderboard.csv and shows the information on the screen.

        # Loads the data in leaderboard.csv.
        data = self.__load_leaderboard_information()

        # Gets the width and height of the canvas.
        canvas_width = self.__canvas.winfo_reqwidth()
        canvas_height = self.__canvas.winfo_reqheight()

        # Calculates the x coordinate of the initials column
        initials_x = canvas_width / 4

        # Calculates the x coordinate of the score column
        score_x = canvas_width * 3 / 4

        # Creates a "INITIALS" heading text.
        self.__canvas.create_text(initials_x, 30, text="INITIALS", fill="#FFFFFF",
                                  font=("TkDefaultFont", 20), anchor="n")

        # Creates a "SCORE" heading text.
        score_text = self.__canvas.create_text(score_x, 30, text="SCORE", fill="#FFFFFF",
                                               font=("TkDefaultFont", 20), anchor="n")

        # Calculates the height of the headings.
        heading_height = self.__canvas.bbox(score_text)[3] - self.__canvas.bbox(score_text)[1]

        # Stores the total heights of the previously created texts.
        # heading_height is multiplied by 1.5 to leave a small gap between the heading and entries.
        total_previous_object_height = 30 + 1.5 * heading_height

        # Iterates over each of the entries in the data read from leaderboard.csv.
        for entry in data:

            # Creates the initials of the entry as text on the screen underneath
            # the "INITIALS" heading.
            self.__canvas.create_text(initials_x, total_previous_object_height, text=entry[0],
                                      fill="#FFFFFF", font=("TkDefaultFont", 20), anchor="n")

            # Creates the score of the entry as text on the screen underneath the "SCORE" heading.
            score_text = self.__canvas.create_text(score_x, total_previous_object_height,
                                                   text=int(entry[1]), fill="#FFFFFF",
                                                   font=("TkDefaultFont", 20), anchor="n")

            # Adds the height of the newly created text to the total object height so that new text
            # is created underneath the newly created text.
            total_previous_object_height += (self.__canvas.bbox(score_text)[3]
                                             - self.__canvas.bbox(score_text)[1])

        # Temporarily creates text on the canvas to get the height of an entry.
        empty_text = self.__canvas.create_text(100, 100, text="", font=("TkDefaultFont", 20))
        entry_height = self.__canvas.bbox(empty_text)[3] - self.__canvas.bbox(empty_text)[1]
        self.__canvas.delete(empty_text)

        # Calculates the gap from the bottom of the tenth entry (even if it's not there)
        # to the bottom of the canvas.
        gap_from_canvas_bottom = canvas_height - heading_height - 30 - 10 * entry_height

        # Configures the "> Back" text so that the "Back" is centred
        # and the "> " is to the left of it.
        back_text = self.__canvas.create_text(canvas_width/2, (canvas_height
                                              - gap_from_canvas_bottom/2),text="Back",
                                              fill="#FFFFFF", font=("TkDefaultFont", 20))
        back_text_x = self.__canvas.coords(back_text)[0]
        back_text_y = self.__canvas.coords(back_text)[1]
        back_text_width = self.__canvas.bbox(back_text)[2] - self.__canvas.bbox(back_text)[0]
        self.__canvas.coords(back_text, back_text_x + back_text_width/2, back_text_y)
        self.__canvas.itemconfigure(back_text, anchor="e", text="> Back")

    def __load_leaderboard_information(self):
        # Loads the data from the leaderboard.csv file and returns the data.

        # Stores the data in the leaderboard.csv file.
        data = []

        # Try to open the file and read the data into the data list.
        try:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                     "leaderboard.csv")
            with open(file_path, "rt", encoding="utf-8") as f:
                csv_reader = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
                for row in csv_reader:
                    data.append(row)

        # If the file can't be found, then don't do anything.
        except FileNotFoundError:
            pass

        # Returns the data in leaderboard.csv.
        return data

    def __exit_leaderboard(self, event=None):
        # Exits the leaderboard and tells the program to go back to the main menu.

        # Causes the leaderboard's canvas to not be drawn to the window.
        self.__canvas.pack_forget()

        # Tells the program that it should switch back to the main menu state.
        self.__finished = True

    @property
    def finished(self):
        """(bool): Whether or not the program should return to the main menu state or not"""

        return self.__finished

if __name__ == "__main__":
    print("Please run main.py")
