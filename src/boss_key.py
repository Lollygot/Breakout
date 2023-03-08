import os
from PIL import Image, ImageTk
from tkinter import Canvas

class BossKey:
    """A class that represents when the program is in the boss key state"""

    def __init__(self, window, key_bindings):

        # Gets the window's width and height.
        window_width = window.winfo_reqwidth()
        window_height = window.winfo_reqheight()

        # Creates a canvas where the boss key will be drawn on.
        self.__canvas = Canvas(window, background="#000000", width=window_width,
                               height=window_height)

        # Stores a reference to the boss image.
        self.__boss_key_image = None
        self.__load_boss_key_image()

        # Stores the previous canvas that was being shown before the boss key was activated.
        self.__previous_canvas = None

        # Assigns key bindings for the boss key.
        self.__canvas.bind("<KeyPress-" + key_bindings["Boss Key"] + ">",
                           lambda event : self.hide_boss_key())

    def __load_boss_key_image(self):
        # Loads the boss key image.

        # Gets the canvas's width and height.
        canvas_width = self.__canvas.winfo_reqwidth()
        canvas_height = self.__canvas.winfo_reqheight()

        # Tries to open the boss key image
        try:

            # Taken and modified from
            # https://commons.wikimedia.org/wiki/File:Simple_budgeting_spreadsheet_eg.jpg
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets",
                                     "boss_key.jpg")
            image = Image.open(file_path)

        # If the file can't be found or opened then just create a black screen for the
        # boss key image.
        except FileNotFoundError:
            image = Image.new("RGB", (canvas_width, canvas_height), (0, 0, 0))

        # If the image was opened successfully, then resize it to fit the whole canvas.
        else:

            # Calculates how much the height of the image needs to be multiplied by to make the
            # image fit the canvas's width.
            height_scaling_factor = canvas_width / image.width

            # Calculates how much the width of the image needs to be multiplied by to make the image
            # fit the canvas's height.
            width_scaling_factor = canvas_height / image.height

            # Scales the image whilst keeping the same aspect ratio in the direction where the most
            # scaling needs to be applied in the other direction.
            # This is to make sure that the image covers the whole canvas whilst keeping the
            # same aspect ratio.
            if height_scaling_factor > width_scaling_factor:
                image = image.resize((canvas_width, int(height_scaling_factor * image.height)))
            else:
                image = image.resize((int(width_scaling_factor * image.width), canvas_height))

        # Converts the PIL image into a Tkinter PhotoImage and stores a reference to this image.
        self.__boss_key_image = ImageTk.PhotoImage(image)

        # Creates the image onto the BossKey's canvas.
        self.__canvas.create_image(0, 0, image=self.__boss_key_image, anchor="nw")

    def hide_boss_key(self):
        """Hides the boss key image and returns to what the user was doing before"""

        # Hides the boss key image.
        self.__canvas.pack_forget()

        # Shows the canvas of what the user was doing before.
        self.__previous_canvas.pack()
        self.__previous_canvas.focus_set()
        self.__previous_canvas = None

    def show_boss_key(self, previous_canvas):
        """Shows the boss key image over what the user was doing before the boss key was activated

        Parameters:
            previous_canvas (Canvas): The canvas that was being shown before the boss key
                                      was activated.
        """

        # Stores the canvas that was being shown before the boss key was activated.
        self.__previous_canvas = previous_canvas

        # Hides the canvas that was being shown before.
        previous_canvas.pack_forget()

        # Shows the boss key image and causes the canvas to start looking for key inputs.
        self.__canvas.pack()
        self.__canvas.focus_set()

    @property
    def canvas(self):
        """(Canvas): The canvas that the boss key's image will be drawn on"""

        return self.__canvas

if __name__ == "__main__":
    print("Please run main.py")
