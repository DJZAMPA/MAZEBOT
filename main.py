import sys
import os
import time
import traceback
from importlib import import_module
from highrise.__main__ import *

# BOT SETTINGS
bot_file_name = "run"
bot_class_name = "MazeBot"
room_id = "65a7cd002d4c283c61689cd5"
bot_token ="816fa979d29701fb2a4ee2c81c2ef4fba2715906586d58728fc70f1ecb42897f"

my_bot = BotDefinition(getattr(import_module(bot_file_name), bot_class_name)(), room_id, bot_token)

while True:
    try:
        definitions = [my_bot]
        arun(main(definitions))
    except Exception as e:
        print(f"An exception occurred: {e}")
        traceback.print_exc()
    time.sleep(5)
  
