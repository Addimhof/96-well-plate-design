Goals for this branch:
  - This branch should implement the module configparser in a new .py file which is opened by Working.py prior to the main window loop executing
  - The new .py file should specifically open a file path referencing a file called config.ini
  - config.ini specifically should contain aliases for different cell names within .csv files the program seeks to import, the idea being that plate readers will export with different variable names
  - Aliases in config.ini should correspond to in-program variables, with default names that are the same as those in the program.
  - The new .py file should house the loops that assign variables to lists instead of Working.py
  - All variables, via import in Working.py should be referenced from the new file.
