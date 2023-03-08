# Constants:
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
DEFAULT_PADDLE_WIDTH = 150
DEFAULT_PADDLE_HEIGHT = 10
DEFAULT_CANVAS_GAP = 40
DEFAULT_PADDLE_COLOUR = "#FFFFFF"
DEFAULT_PADDLE_SPEED = 15
DEFAULT_BALL_RADIUS = 8
DEFAULT_PADDLE_GAP = 200
DEFAULT_BOUNCES_UNTIL_SPEED_UP = 3
DEFAULT_SPEED_UP_AMOUNT = 1.0
DEFAULT_BALL_COLOUR = "#FFFFFF"
DEFAULT_BALL_SPEED = 8.0
DEFAULT_BRICK_HEIGHT = 20
DEFAULT_BRICKS_PER_ROW = 10
DEFAULT_ROW_GAP_FROM_TOP = 4
DEFAULT_BRICK_COLOURS = ["#FF0000", "#FFA500", "#FFFF00", "#008000"]
DEFAULT_BRICK_SCORE = 10
DEFAULT_STARTING_LIVES = 3
DEFAULT_STARTING_LEVEL = 1
KEY_BINDINGS_COMMANDS_ORDER = ["Move Paddle Left",
                               "Move Paddle Right",
                               "Move Menu Pointer Up",
                               "Move Menu Pointer Down",
                               "Confirm Option",
                               "Pause Game",
                               "Reset Ball Speed",
                               "Set Lives to 10",
                               "Boss Key"
                              ]
DEFAULT_KEY_BINDINGS = {"Move Paddle Left": "Left",
                        "Move Paddle Right": "Right",
                        "Move Menu Pointer Up": "Up",
                        "Move Menu Pointer Down": "Down",
                        "Confirm Option": "Return",
                        "Pause Game": "Escape",
                        "Reset Ball Speed": "F11",
                        "Set Lives to 10": "F12",
                        "Boss Key": "F1"
                       }
SHIFT_CHARACTERS_TO_NON_SHIFT = {"!": "1", '"': "2", "£": "3", "$": "4", "%": "5", "^": "6",
                                 "&": "7", "*": "8", "(": "9", ")": "0", "_": "-", "+": "=",
                                 "¬": "`", "¦": "`", "{": "[", "}": "]", ":": ";", "@": "'",
                                 "~": "#", "<": ",", ">": ".", "?": "/", "|": "\\"}
ACCEPTED_KEYBIND_SPECIAL_CHARACTERS = ["Escape", "Return", "Left", "Up", "Right", "Down", "Tab",
                                       "BackSpace", "Delete", "space", "F1", "F2", "F3", "F4",
                                       "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]

if __name__ == "__main__":
    print("Please run main.py")
