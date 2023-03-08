from tkinter import Tk
import constants as constants
from main_menu import MainMenu

def create_window(width, height):
    """Returns a window with dimensions width x height centred on the screen

    Parameters:
        width (int): The width of the window
        height (int): The height of the window

    Returns:
        window (Tk): The window object that is created
    """

    # Creates a new window and sets its title to Breakout.
    window = Tk()
    window.title("Breakout")

    # Gets the dimensions of the screen so that the window can appear in the centre of the screen.
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Works out the coordinates for the top left of the window.
    x = int(screen_width/2 - width/2)
    y = int(screen_height/2 - height/2)

    # Changes the window size to width x height and moves the window to (x, y).
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.configure(width=width, height=height)

    return window

def main():
    """Starts the Breakout game"""

    # Creates a new window with dimensions 800x600 in the centre of the screen.
    window = create_window(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)

    # Creates a MainMenu object that represents when the program is in the main menu state.
    MainMenu(window)

    # Starts the window's game loop.
    window.mainloop()

if __name__ == "__main__":
    main()
