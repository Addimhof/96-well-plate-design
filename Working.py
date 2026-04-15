import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import *
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
# Go to Pylance Settings, then Python > Analysis: Extra Paths,
# Copy your working directory (where this file is) as text and paste it into the field. Pylance will complain otherwise.
import cluster_plate as cp
import os

DEV_MODE = True # Debug flag. Treat as constant. DO NOT change in any function.
CSV_FOLDER = "plate_test_rounds_native" # Points to file for csv to do stuff with. Treat as constant. DO NOT change in any function.
def load_all_rounds_from_folder(folder):
    """
    Desc: First function that should be called in main. Loads csv well data from a file path and documents everything in global well history

    Pre: Needs a string file path called folder.

    Post: well_data, well_history, and round_number are all global variables to be accessed later.
    """  
    global well_data, well_history, round_number
    # well_data: dictionary for associating wells with the data they store. Most recent data.
    # well_history: dictionary for associating wells with the data they store. Past data.
    # round_number: Tracks how many CSV files have been imported. Increments each time an import occurs following sorting.

    well_data = {}
    well_history = {}
    round_number = 0
    # A sorted list of all CSV filenames within the folder name string passed to this function.

    csv_files = sorted([f for f in os.listdir(folder) if f.endswith(".csv")]) #Declare file path to open for csv_file. Probably a String but technically Any.

    for csv_file in csv_files:
        
        round_number += 1
        path = os.path.join(folder, csv_file) # Declare file path to open for csv_file. Probably a String but technically Any.

        with open(path, newline="") as f:
            # Every instance of f is a file being opened here.
            reader = csv.reader(f) # Instance of a parsed csv file.
            header = next(reader) # Currently unused within scope. Please do something with this or delete it.
            for row in reader:
                row_label = row[0] # First element for every row. A string for diffrientiating rows.
                for i, cell in enumerate(row[1:]): # Loop to do things per cell.
                    well = f"{row_label}{i+1}" # Construct a well title. "A1", "A2", etc.
                    promoter, ahl, od, rfu = cell.split("|")
                    # promoter: Promoter type. Anderson mutants for where we are now. "J23###"
                    # ahl: AHL concentration.
                    # od: Optical Density. Estimated density of bacteria.
                    # rfu: Relative Fluorescence Units. DV.

                    od_val = float(od) if od else 0
                    rfu_val = float(rfu) if rfu else 0
                    # od_val, rfu_val: make these floats bc python sucks

                    # labelling for wells with non-existant data. Null values to not cause errors when we graph things.
                    if well not in well_history:
                        well_history[well] = {
                            "promoter": promoter,
                            "ahl": ahl,
                            "od": [],
                            "rfu": []
                        }
                    # Associate the float values that do exist for the well_history with their appropriate wells.
                    well_history[well]["od"].append(od_val)
                    well_history[well]["rfu"].append(rfu_val)

                    # Label EVERYTHING for wells that exist
                    well_data[well] = {
                        "promoter": promoter,
                        "ahl": ahl,
                        "od": od_val,
                        "rfu": rfu_val
                    }

    print(f"✅ Loaded {round_number} rounds from folder '{folder}'")

# Rows and columns going from A-H(row) 8x12 grid (Can change the size w/ this)
rows = 8 # Number of rows
columns = 12 # Number of columns
row_labels = [chr(i) for i in range(65, 65+rows)] # Chr referesneces ASCII index for uppercase A. Iterates from there for rows. > 26 rows means funny results.
well_data = {} # Dictionary for associating wells with the data they store. Most recent data.
buttons = {} # Dictionary of buttons. Each I believe corresponds with a well in the GUI.
button_states = {} # Holds all states associated with the buttons.
round_number = 1 # Initial round number. Associated with CSVs imported.
well_history = {} # Dictionary for associating wells with the data they store. Past data.

if DEV_MODE:
    load_all_rounds_from_folder(CSV_FOLDER)

# This is the window and its design
window = Tk() # Tkinter window template/object. It may be useful to roll all of the params into this constructor.

pressed = False
window.title("96 Well Plate") # Window display title. Reads at the top.
icon = PhotoImage(file='Ecoli.png') # Filepath for Window icon. Shows up in top-left and task bar.
window.iconphoto(True, icon) # Set the window icon to display.
window.config(background="white") # Background window color. Maybe tone this down from straight #ffffff.

timer_label = tk.Label(window, text="Timer: 0 seconds") # Places a label (Basically rendered text) in the top-middle of the window.
timer_label.grid(row=rows, column=0, columnspan=12, pady=10) # Positions the label at the top of each of the rows. Potential bug: columnspan should be = columns
seconds_passed = 0 # Label used for timer updates. Modified by update_timer().

# As a note, well_name is not actually any variable modified outside of a function. It's another way of referring to well_history[well].
# TODO: Pick well_name or well as the variable to reference individual wells.
def open_data_entry(well_name):
    """
    Desc: A popup window that handles editing of the well_data referenced in the passed param. Also includes definitions to save data.

    Pre: Called with a well/well_name to reference.

    Post: This function acts as a w included save_and_close(), see that function for more details.
    """  
    popup = tk.Toplevel(window) #Precisely what it sounds like. Creates a popup layered on top of the main window.
    popup.title(f"Enter data for {well_name}") #Pass the well title here. The popup also has a name.

    # Header text. User should put entries in widgets under this.
    tk.Label(popup, text=f"Data for {well_name}", font=("Times New Roman", 12)).pack(pady=5)

    # Change the promoter with the following widget. The label is anchored to the left.
    tk.Label(popup, text="Promoter:").pack(anchor="w", padx=10)
    entry_promoter = tk.Entry(popup, width=25) #entry_promoter: Creates a text entry box with a width of 25 characters.
    entry_promoter.insert(0, well_data.get(well_name, {}).get("promoter", "")) 
    # Anything that is typed in here gets stuck as the appropriate well_data promoter

    # Only the first csv imported should have its promoters edited? I might need more explanation here. -- Julian
    if round_number > 1:
        entry_promoter.config(state="disabled")

    # Layout the entry box.
    entry_promoter.pack(padx=10, pady=5)

    # Everything below follows a similar pattern to entry_promoter. TODO: Make a function to do this.
    # They correspond in this way: entry_ahl -> "ahl", entry_od -> "od", entry_rfu -> "rfu"
    # You can change OD and RFU between csv rounds.

    tk.Label(popup, text="AHL Concentration:").pack(anchor="w", padx=10)
    entry_ahl = tk.Entry(popup, width=25)
    entry_ahl.insert(0, well_data.get(well_name, {}).get("ahl", ""))

    if round_number > 1:
        entry_ahl.config(state="disabled")

    entry_ahl.pack(padx=10, pady=5)

    tk.Label(popup, text="OD:").pack(anchor="w", padx=5)
    entry_od = tk.Entry(popup, width=25)
    entry_od.insert(0, well_data.get(well_name,{}).get("od",""))
    entry_od.pack(padx=10,pady=10)

    tk.Label(popup, text="RFU:").pack(anchor="w", padx=5)
    entry_rfu = tk.Entry(popup, width=25)
    entry_rfu.insert(0, well_data.get(well_name,{}).get("rfu",""))
    entry_rfu.pack(padx=10,pady=10)

    # Data edits be here
    def save_and_close(open_next=True):
        """
        Desc: Assigns the changes made in the open_data_entry() popup to the wells and csv data.

        Pre: The open_next param, true by default, opens the next well entry recursively depending on user input.

        Post: save_plate_to_csv() will always eventually be called. This by extension has file I/O output.
        """  
        # Make some variables equal to the inputs gained from the tk Entries
        promoter = entry_promoter.get()
        ahl = entry_ahl.get()
        od = entry_od.get()
        rfu = entry_rfu.get()

        # Assign to well data. Clean empty entries.
        # This is also a repeat of a motif in load_all_rounds_from_folder(). TODO: Make this a function.
        well_data[well_name] = {
            "promoter": promoter,
            "ahl": ahl,
            "od": entry_od.get(),
            "rfu": entry_rfu.get()
        }
        if well_name not in well_history:
            well_history[well_name] = {
                "promoter": promoter,
                "ahl": ahl, 
                "od": [], 
                "rfu": []
            }   

        # Kill the window.
        popup.destroy()
        # Below is recursive calling that if the open_next param is true, will allow for consecutive data entry.
        if open_next:
            next_well = get_next_well(well_name)
            if next_well:
                open_data_entry(next_well)
            else:
                # If there's no more data to enter, save everything.
                save_plate_to_csv()
        else:
            save_plate_to_csv()
    #The Enter (Return) key should save the data and close the window
    popup.bind("<Return>", lambda e: save_and_close(True))
    # Two more buttons for saving. Done is recursive. Finish is not.
    # MAYBE TODO: "Done" should be "Done (Open Next)" for user-friendliness.
    tk.Button(popup, text="Done", command=lambda: save_and_close(True)).pack(pady=5)
    tk.Button(popup, text="Finish", command= lambda: save_and_close(False)).pack(pady=5)

def get_next_well(current_well):
    """
    Desc: Fetches the next well accounting for rows of columns.

    Pre: Called with a current_well to index.

    Post: Gets the index of the next well if it exists, otherwise returns None.
    """  
    all_wells = [f"{r}{c+1}" for r in row_labels for c in range(columns)] #A 2D list of ALL the wells.
    # Error handling? In my GUI?
    try:
        # An index is grabbed from the the current_well passed, from its position in all_wells.
        index = all_wells.index(current_well)
        # If there's a well following, return the index of the next well. Or else return None.
        if index + 1 < len(all_wells):
            return all_wells[index+1]
        else:
            return None
    except ValueError:
        # If there's not an applicable value return none.
        return None

def on_hover(well_name):
    """
    Desc: Very simple function. Changes the window title when called to reference a specific well button label.

    Pre: Called with a well/well_name to reference.

    Post: Changes the tkinter window title to reference the well/well_name.
    """  
    window.title(f"Hovering over {well_name}")

def button_pressed(row, col):
    """
    Desc: Also simple GUI handling. Assigns a True button_state and changes its appearance if clicked.

    Pre: Called with a row and column for the button, assuming they are in a 2D matrix.

    Post: Changes the button_state and its appearance to reflect clicking on it.
    """  
    if not button_states[(row, col)]:
            button_states[(row, col)] = True
            button = buttons[(row, col)]
            button.config(relief="sunken", bg="dark grey")

for r in range(rows):
    for c in range(columns):
        button_states [(r, c)] = False
        well_name = f"{row_labels[r]}{c+1}"

        button = tk.Button(window,
                           text=well_name,
                           width=6, height=2,
                           bg="lightgrey",
                           command=lambda r=r, c=c: button_pressed(r, c,)
        )
        button.grid(row=r, column=c, padx=2, pady=2)
        buttons[(r, c)] = button

        button.bind("<Enter>", lambda e, w=well_name: on_hover(w))
        button.bind("<Button-1>", lambda e, r=r, c=c, w=well_name: (
            button_pressed(r, c),
            open_data_entry(w)
        ))

def save_plate_to_csv():
    global round_number, well_history
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"plate_data_round_{round_number}_{timestamp}.csv"
    for well, data in well_data.items():
        if well not in well_history:
            well_history[well] = {
                "promoter": data.get("promoter", ""),
                "ahl": data.get("ahl", ""),
                "od": [],
                "rfu": []
            }
        try:
            od_value = float(data["od"]) if data ["od"] else 0
        except ValueError:
            od_value = 0
        well_history[well]["od"].append(od_value)
        try:
            rfu_value = float(data["rfu"]) if data ["rfu"] else 0
        except ValueError:
            rfu_value = 0
        well_history[well]["rfu"].append(rfu_value)
   
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        header = [str(i+1) for i in range(columns)]
        writer.writerow([""]+header)
        for r in range(rows):
            row_label=row_labels[r]
            row_values = []
            for c in range(columns):
                well_name = f"{row_label}{c+1}"
                data = well_data.get(well_name, {})
                value = f"{data.get('promoter','')}|{data.get('ahl','')}|{data.get('od','')}|{data.get('rfu','')}"
                row_values.append(value)
            writer.writerow([row_label] + row_values)
save_button = tk.Button(window, text= "Save Curretn Data", command=save_plate_to_csv)
save_button.grid(row=rows+2, column=0, columnspan=12, pady=5)

def start_round():
    global round_number, well_data
    save_plate_to_csv()
    
    for w in well_data:
        well_data[w]["od"] = ""
        well_data[w]["rfu"] = ""
   
    round_number += 1
    messagebox.showinfo("New Round", f"Round {round_number} started. Enter new values.")

round_button = tk.Button(window, text="Start New Round", command=start_round)
round_button.grid(row=rows+2, column=0, columnspan=12, pady=5)

def update_timer():
    global seconds_passed
    if not window.winfo_exists():  # window is destroyed
        return
    seconds_passed += 1
    timer_label.config(text=f"Timer: {seconds_passed} seconds")
    window.after(1000, update_timer)

def plot_well_history():
    for well, history in well_history.items():
        if not(any(v != 0 for v in history["od"]) or any(v !=0 for v in history["rfu"])):
            continue
        rounds= list(range(1, len(history["od"]) + 1))

        plt.figure(figsize=(6,4))
        plt.plot(rounds, history["od"], marker= 'o', label="od")
        plt.plot(rounds, history["rfu"], marker='x', label='rfu')
        plt.title(f"Well {well} ({history['promoter']} | {history['ahl']})")
        plt.xlabel("Round")
        plt.ylabel("Value")
        plt.legend()
        plt.show()

def trim_empties(values):
    while values and (values[-1] == "" or values[-1] is None):
        values.pop()
    return values

def group_wells_by(field):
    groups = {}
    for well, data in well_history.items():
        key = data.get(field)
        if key:
            if key not in groups:
                groups[key] = []
            groups[key].append(well)
    return groups


def select_and_plot_wells():
    """
    Desc: This function is a main for all graphing operations, separated into four broad steps with a final matplotlib graph within a popup window.

    Pre: Presumably uses globals since there are no arguments. Outside of this function a button is needed to call from GUI, done with plot_selected_button below.

    Post: Produces matplotlib figures in windows created and handled within the function.
    """  
    import cluster_plate as cp  # Ensure cluster_plate.py is in the same folder

    # --- Step 1: Well selection popup ---
    well_popup = tk.Toplevel(window) # Top-level window prompting user on which wells to plot. Includes more setup below.
    well_popup.title("Select Wells to Plot")

    canvas = tk.Canvas(well_popup, height=300) # Canvas is utilized here to arrange elements within the window accessible have a scrollbar.
    # ^Could be renamed for descriptiveness
    v_scrollbar = tk.Scrollbar(well_popup, orient="vertical", command=canvas.yview) # Create a vertical scroll bar for viewing elements listed vertically in the popup
    frame = tk.Frame(canvas) # Tie the canvas to a frame, which actually allows for easier widget handling.

    # In order: <Configure> is triggered when window size changes, the lambda is a short function triggered by this event that calls for elements in the bounding 
    # box to be shifted
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    # Create the frame as a window with a topleft anchor
    canvas.create_window((0,0), window=frame, anchor="nw")
    # Display the scrollbar
    canvas.configure(yscrollcommand=v_scrollbar.set)
    
    # This expands the canvas to expand to the bounds of the created window
    canvas.grid(row=0, column=0, sticky="nsew")
    # Expands the scrollbar to the top and bottom, and assigns it to the eastmost column
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    # Blow up the canvas so it takes up most of the window.
    well_popup.grid_rowconfigure(0, weight=1)
    well_popup.grid_columnconfigure(0, weight=1)

    # Displays "Select wells to plot" as a header
    tk.Label(frame, text="Select wells to plot").grid(row=0, column=0, columnspan=columns, pady=5)

    well_vars = {} # Based on usage in functions well_vars acts as a boolean selection/filtering tool for picking elements promoter_groups and ahl_groups
    # Both promoter_groups and ahl_groups are lists of well data added to a group if their promoter or ahl data exists. Ethan should annotate the function called.
    promoter_groups = group_wells_by("promoter")  
    ahl_groups = group_wells_by("ahl")

    # Inner function set here (And any definitions henceforth) are utilized to access variables within select_and_plot_wells()
    def select_group(well_list):
        """
        Desc: When called with a list, will compare keys present in both the list provided and well_vars, setting the associated well_vars value to true if both keys 
        exist.

        Pre: Pass well_list in. In calls within select_and_plot_wells, this is for promoter_groups and ahl_groups. Mayber rename well_list to well_group.

        Post: Edits well_vars with boolean definitions in present items. Used with a global this could be somewhat destructive.
        When we refactor I recommend passing well_vars in and using a temporary dictionary that is returned, with well_vars set to it.
        """  
        for w in well_list:
            if w in well_vars:
                well_vars[w].set(True)

    # select_all_var is for selecting all the buttons in the window.
    select_all_var = tk.BooleanVar(value=False)
    def toggle_select_all():
        """
        Desc: Selects all of the wells present within the window.

        Pre: Accesses the key value pairs in well_vars.

        Post: Indiscriminantly sets all values in well_vars to true via set function.
        """  
        for var in well_vars.values():
            var.set(select_all_var.get())
    
    # Button for checking all wells, acted upon by the above toggle_select_all() function.
    tk.Checkbutton(frame, text="Select All Wells", variable=select_all_var, command=toggle_select_all).grid(row=1, column=0, columnspan=columns, pady=5)
    tk.Label(frame, text="Select by Promoter").grid(row=2, column=0, columnspan=columns, pady=5)

    # row_offset starts buttons a ways from the left edge so that they're roughly centered.
    row_offset = 3

    # Below two enumerated loops create lines of buttons for each element within the promoter or ahl group.
    # They allow for promoter and ahl group selection.
    for i, promoter in enumerate(promoter_groups):
        tk.Button(frame, text=f"Select Promoter: {promoter}",
                  command=lambda p=promoter: select_group(promoter_groups[p])
        ).grid(row=row_offset+i, column=0, columnspan=columns//2, sticky="w")

    for i, ahl in enumerate(ahl_groups):
        tk.Button(frame, text=f"Select AHL: {ahl}",
                  command=lambda a=ahl: select_group(ahl_groups[a])
        ).grid(row=row_offset+i, column=columns//2, columnspan=columns//2, sticky="w")

    # --- Individual wells ---
    # As the above header would imply for the handling, we create buttons for each and every well present with meaningful data in well_history.
    # row_index firmly places these east of the grouping buttons handled above.
    row_index = 6 + len(promoter_groups)
    # 2D button array.
    for r_i, r in enumerate(row_labels):
        for c in range(1, columns+1):
            # Well labels based on row and column
            well = f"{r}{c}"
            # If current well history exists, obtain the data. Otherwise return NoneType.
            history = well_history.get(well, None)
            # Check specificall if od and rfu are non-zero.
            if history and (any(v != 0 for v in history["od"]) or any(v != 0 for v in history["rfu"])):
                # If the current well does have that data, then add it as a button to the grid, labelled with
                # "A1,B2,etc. (Promoter | rfu)"
                var = tk.BooleanVar()
                well_vars[well] = var
                cb = tk.Checkbutton(frame, text=f"{well} ({history['promoter']} | {history['ahl']})", variable=var)
                cb.grid(row=row_index+r_i, column=c-1, padx=3, pady=3)

    def go_to_graph_type():
        """
        Desc: Final function of Step 1. Creates an actionable list of wells to be graphed when appropriate wells have been selected.

        Pre: No parameters. Needs access to well_popup as well as well_vars. This is also something that could be handled through passing variables.

        Post: Destroys the well_popup window. Moves to graph_type_popup.
        """  
        well_popup.destroy() #When this function is called we no longer need to pick out wells.
        selected_wells = [w for w, var in well_vars.items() if var.get()] #Make a list of all of the wells selected.
        if not selected_wells:
            # Error handling. Make sure user actually picks wells.
            messagebox.showwarning("No wells selected", "Please select at least one well.")
            return
        graph_type_popup(selected_wells) #Start doing graphs.

    # "Next" button calls the above go_to_graph_type function.
    tk.Button(frame, text="Next", command=go_to_graph_type).grid(row=rows+3, column=0, columnspan=columns, pady=10)

    # --- Step 2: Graph type selection popup ---
    def graph_type_popup(selected_wells):
        """
        Desc: Entirely handles a window which prompts the user for graphing options. Standard and Clustered are the options, these could be explained
        more technically (i.e. what kind of graph are they?) Perhaps some descriptive "What is this" popups.

        Pre: All selected wells are passed here for graph handling.

        Post: Graph handling is done by plot_standard and cluster_options_popup calls, which do different types of graphing.
        """ 
        #Top-level window prompting user to select a graphing procedure.
        popup = tk.Toplevel(window)
        popup.title("Select Graph Type")
        
        # Same within window as a header
        tk.Label(popup, text="Select graph type:").pack(pady=5)
        # A variable set by the buttons below. Defaults to all so that go_next will display standard graphing by default.
        graph_type_var = tk.StringVar(value="all")
        # Buttons assign different values to the StringVar to encode a graph selection. Handled by if-else in go_next
        tk.Radiobutton(popup, text="Standard Graph", variable=graph_type_var, value="all").pack(anchor="w", padx=10)
        tk.Radiobutton(popup, text="Clustered Graph", variable=graph_type_var, value="clustered").pack(anchor="w", padx=10)

        def go_next():
            """
            Desc: Function within graph_type_popup to handle "stalled looping" allowing for graphs to be displayed, iterated with the "Next" button being hit.

            Pre: Accesses the StringVar graph_type_var for checking which graph to display.

            Post: Actually calls plot_standard and cluster_options_popup.
            """ 
            popup.destroy()
            if graph_type_var.get() == "all":
                plot_standard(selected_wells)
            else:
                cluster_options_popup(selected_wells)

        # Next button to flip through graphs.
        tk.Button(popup, text="Next", command=go_next).pack(pady=10)

    # --- Step 3: Cluster options popup ---
    def cluster_options_popup(selected_wells):
        """
        Desc: Handles the entirety of a window which allows the user to select groups of wells to cluster on graphs, based on their individual variables.
        The user may also select groups based on graphical features of interest. When the window is terminated everything is passed to plot_clusters_gui().

        Pre: selected_wells is passed to this function. It is not modified or used for mapping, but it is utilized when plot_clusters_gui() is called.

        Post: Graphical features of interest are stored as variables, usually tk Bools and dictionaries that are all inevitably passed to plot_clusters_gui() as
        parameters when this popup is closed.
        """
        # Top level window for selecting data clusters.
        popup = tk.Toplevel(window)
        popup.title("Cluster Options")

        # Window header label
        tk.Label(popup, text="Select measurement(s) to cluster:").pack(pady=5)

        # Buttons tied to boolean values od_var and rfu_var enable clustering based on said conditions. These are by default true.
        od_var = tk.BooleanVar(value=True)
        rfu_var = tk.BooleanVar(value=True)
        tk.Checkbutton(popup, text="OD", variable=od_var).pack(anchor="w", padx=10)
        tk.Checkbutton(popup, text="RFU", variable=rfu_var).pack(anchor="w", padx=10)

        # Next section allows for selection of signal features.
        tk.Label(popup, text="Select signal features:").pack(pady=5)
        # Dictionary stores variables tied to features as keys, with true/false mapping for values. Allows for specific graphical features to be selected.
        feature_vars = {}
        for feat in ["total","peak","ending"]:
            #Each feature gets its own button. These as vars are capitalized.
            var = tk.BooleanVar(value=True)
            feature_vars[feat] = var
            tk.Checkbutton(popup, text=feat.capitalize(), variable=var).pack(anchor="w", padx=10)

        # Create boolean buttons to include the categorical variables Promoter and AHL Concentration in clustering.
        tk.Label(popup, text="Include categorical features:").pack(pady=5)
        include_promoter_var = tk.BooleanVar(value=False)
        include_ahl_var = tk.BooleanVar(value=False)

        tk.Checkbutton(popup, text="Promoter", variable=include_promoter_var).pack(anchor="w", padx=10)
        tk.Checkbutton(popup, text="AHL Concentration", variable=include_ahl_var).pack(anchor="w", padx=10)

        # Allows user to either specify a number of clusters or automatically assign a number. This decision is handled through StringVar cluster_mode_var as an enum.
        tk.Label(popup, text="Select clustering mode:").pack(pady=5)
        cluster_mode_var = tk.StringVar(value="auto")
        tk.Radiobutton(popup, text="Automatic Clustering", variable=cluster_mode_var, value="auto").pack(anchor="w", padx=10)
        tk.Radiobutton(popup, text="Specify Number of Clusters", variable=cluster_mode_var, value="manual").pack(anchor="w", padx=10)

        # For manual cluster, include an entry box for the number of clusters. Stored in num_clusters_entry
        num_clusters_entry = tk.Entry(popup, width=5)
        num_clusters_entry.pack(anchor="w", padx=20)

        def plot_clusters():
            """
            Desc: This function does three things: Input validation to make sure the user has selected appropriate clusters, 
            preparation of plot_clusters_gui params, then execution of plot_clusters_gui.

            Pre: Relies pretty heavily on tkinter variables defined in cluster_options_popup for use with buttons. Able to use them within its scope.

            Post: Calls plot_clusters_gui based on the params defined in this function.
            """
            # Validate that signals have been selected. If there are, pass the values as a dictionary called signals_selected.
            signals_selected = {"OD": od_var.get(), "RFU": rfu_var.get()}
            if not any(signals_selected.values()):
                messagebox.showwarning("No measurement selected","Select at least OD or RFU.")
                return
            # Validate that features have been selected. If there are, pass the values as a dictionary called features_selected.
            features_selected = [f for f,var in feature_vars.items() if var.get()]
            if not features_selected:
                messagebox.showwarning("No features selected","Select at least one feature for clustering.")
                return
            # When initialized the number of clusters (stored in n_clusters) is NoneType. Every value stored afterwards should be an integer.
            n_clusters = None
            # If the user selected manual for their number of clusters, we need to do some exception handling.
            if cluster_mode_var.get()=="manual":
                try:
                    # If the number of clusters is 0, negative, or None, the user must re-enter a value.
                    n_clusters = int(num_clusters_entry.get())
                    if n_clusters<1: raise ValueError
                except ValueError:
                    messagebox.showwarning("Invalid input","Enter a valid number of clusters.")
                    return

            # Kill the window
            popup.destroy()
            # Graph everything.
            plot_clusters_gui(
                selected_wells=selected_wells,
                features_selected=features_selected,
                signals_selected=signals_selected,
                include_promoter=include_promoter_var.get(),
                include_ahl=include_ahl_var.get(),
                clustering_mode="kmeans" if n_clusters else "auto",
                n_clusters=n_clusters if n_clusters else 4
            )

        # Plot button to begin plotting via plot_clusters
        tk.Button(popup, text="Plot", command=plot_clusters).pack(pady=10)

    # --- Step 4: Standard plotting function (NEW) ---
    def plot_standard(selected_wells):
        """
        Desc: This function is called by graph_type_popup when the user calls for a standard graph, represented by tk StringVar value "all" when a graphing
        method is chosen by the program. selected_wells is iterated through for to construct lines for each included well via matplotlib's functions 
        and the resulting graph, alongside a legend for each of the lines, is displayed in a GUI to the user. 

        Pre: A dictionary called selected_wells must be passed to this function. It is the dataset we do plt operations on.

        Post: show() calls are made to display the data with a GUI.
        """
        # fig is the figure/plot we inevitably show to the user.
        # ax1 is the Y-axis for OD
        # ax2 is the Y-axis for RFU, cloned initially from ax1.
        fig, ax1 = plt.subplots(figsize=(8,5))
        ax2 = ax1.twinx()
        # Our color table is borrowed from matplotlib's built-in color maps, allowing for automatic assignment.
        colors = plt.cm.tab10.colors
        # color_index simply acts as a way to access the colormap to make datasets look distinct.
        color_index = 0

        for well in selected_wells:
            # history acts as the access variable for values in the current well.
            history = well_history[well]
            # rounds for all intents and purposes is the x-axis variable. We simply construct it by repeatedly assigning a ranged list of values based on the length
            # of entries in the well_history with key "od", followed by an increment. Two assumptions are made:
            #   - "od" and "rfu" are of the same length, which is hopefully checked by other functions.
            #   - Whatever the last "od" key-value pair is will represent the greatest value on the x-axis. This is error-prone.
            rounds = list(range(1, len(history["od"])+1))
            # OD lines are constructed with solid lines '-' and circular points 'o'. Labels are in the format "(Anderson Promoter) (AHL Conc.) OD".
            ax1.plot(rounds, history["od"], marker='o', linestyle='-', label=f"{history['promoter']} ({history['ahl']}) OD", color=colors[color_index % len(colors)])
            # RFU lines are constructed with dashed lines '--' and cross points 'x'. Labels are in the format "(Anderson Promoter) (AHL Conc.) RFU".
            ax2.plot(rounds, history["rfu"], marker='x', linestyle='--', label=f"{history['promoter']} ({history['ahl']}) RFU", color=colors[color_index % len(colors)])
            # Update the color index. Color is kept the same for both well OD and RFU for the user to associate the two.
            color_index += 1

        # These commands simply set labels for ax1 and ax2 that are viewable by the user.
        ax1.set_xlabel("Round")
        ax1.set_ylabel("OD")
        ax2.set_ylabel("RFU")
        ax1.set_title("Selected Wells OD & RFU")

        # --- Show main graph ---
        # lines is a list of the ax1 and ax2 lines drawn for later legend handling.
        lines = ax1.get_lines() + ax2.get_lines()
        # labels is a list of labels accessed from the list of lines created, also for legend handling.
        labels = [l.get_label() for l in lines]
        fig.show()

        # --- Separate legend window ---
        # legend_fig is the constructed window for figures.
        legend_fig = plt.figure("Legend Window", figsize=(6, max(4,len(labels)*0.35)))
        # legend_ax is created to allow us to render things.
        legend_ax = legend_fig.add_subplot(111)
        legend_ax.axis("off")
        # ncols is scaled to the number of lines present. 
        ncols = max(1,len(labels)//15)
        # legend_ax is actually made into a proper legend here. It pulls the lines list, the labels list, centers everything based on ncols, and adds a border.
        legend_ax.legend(lines, labels, loc="center", ncol=ncols, frameon=True)
        legend_ax.set_title("Legend")
        legend_fig.show()



# This is now part of the main window rather than a defined function. If we could somehow reorganize this to not be as out of the way, that would be useful.
# plot_selected_button acts as a way for a user to call select_and_plot_wells from gui.
plot_selected_button = tk.Button(
    window,
    text="Plot Selected Wells",
    command=select_and_plot_wells)
plot_selected_button.grid(row=rows+3, column=0, columnspan=12, pady=10)

def plot_clusters_gui(selected_wells, features_selected, signals_selected,
                      include_promoter=False, include_ahl=False,
                      clustering_mode="kmeans", n_clusters=4, dbscan_eps=0.5):
    """
    Desc:  

    Pre: For a list of all of the parameters passed to the function, look below in its own section for a description of each.

    Post: Creates a configurable tkinter window that houses a matplotlib canvas_plot displaying the cluster map built by this function.

    Parameters (Included since there's quite a few):
        -selected_wells: Iterable of well identifiers. Specified during go_to_graph_type().
        
        -features_selected: User chooses these during plot_clusters().

        -signals_selected: An iterable of every OD and RFU data point.

        -include_promoter: tk Boolval to include promoter mutants as a clustering factor

        -include_ahl: tk Boolval to include AHL levels as a clustering factor

        -clustering_mode: Clustering algorithm selector ("kmeans", "auto", etc.). kmeans partions observations into a set number of clusters
        specified by n_clusters.

        -n_clusters: Number of clusters for k-means (if applicable). Specified by user in plot_clusters().

        -dbscan_eps: Maximum distance during DBSCAN algorithim that points can be from each other while still being neighbors.
    """
    #cluster plate functions are used specifically for this function.
    import cluster_plate as cp
    from matplotlib.lines import Line2D

    # Ensure all OD/RFU are lists of floating point or string values.
    for w in selected_wells:
        if isinstance(well_history[w]["od"], (float, str)):
            well_history[w]["od"] = [float(well_history[w]["od"])]
        if isinstance(well_history[w]["rfu"], (float, str)):
            well_history[w]["rfu"] = [float(well_history[w]["rfu"])]

    # --- Create plot window ---
    # It should be noted, that compared to plot_standard() this function embeds the matplotlib graphs into tkinter windows, as opposed to using matplotlib's built-in
    # GUI handling.
    plot_window = tk.Toplevel()
    plot_window.title("Clustered Wells Plot")
    # fig is the figure/plot we inevitably show to the user.
    # ax_od is the Y-axis for OD.
    # ax_rfu is the Y-axis for RFU, cloned initially from ax1.
    fig, ax_od = plt.subplots(figsize=(9,6))
    # Our color table is borrowed from matplotlib's built-in color maps, allowing for automatic assignment.
    ax_rfu = ax_od.twinx()
    # color_index simply acts as a way to access the colormap to make datasets look distinct.
    colors = plt.cm.tab10.colors

    max_rounds = max(len(well_history[w]["od"]) for w in selected_wells)
    rounds = list(range(1, max_rounds + 1))

    legend_items = []  # List to collect info for legend.

    # OD clustering
    # It should also be noted that nearly all of the functions from cluster_plate are utilized in these sections.
    if signals_selected.get("OD", False):
        # X_od, labels_od are enumerated returns for the vector features and well labels built by build_feature_matrix.
        X_od, labels_od = cp.build_feature_matrix(well_history,"od",features_selected,selected_wells,include_promoter,include_ahl)
        # od_cluster_ids using the clustering_mode specified, builds a list of cluster features and returns a numpy array reference to each
        od_cluster_ids = cp.cluster_signal(X_od, clustering_mode, n_clusters, dbscan_eps)
        # od_clusters is a dict allowing for labels_od references to return cluster ids. We iterate through this for the next steps.
        od_clusters = cp.build_cluster_map(labels_od, od_cluster_ids)
        for cid, wells in od_clusters.items():
            # First collect time series from the numpy array, stored in mean_od
            mean_od = np.array([well_history[w]["od"] for w in wells], dtype=object)
            # Then get the mean od value, now stored in mean_od
            mean_od = np.mean([np.pad(v, (0, max_rounds - len(v)), 'constant', constant_values=np.nan) for v in mean_od], axis=0)
            # line is used to store the plotting data drawn from the clustering data collected.
            line = ax_od.plot(rounds, mean_od, color=colors[cid % len(colors)],
                              linestyle="-", linewidth=2, label=f"Cluster {cid} OD (n={len(wells)})")
            # Make a legend for each signal. Formatted in the style "Cluster {cluster Id} OD (n={number of clusters})
            legend_items.append((line[0], f"Cluster {cid} OD (n={len(wells)})"))

    # RFU clustering. Copied in structure from OD clustering. We could make this an embedded function called with OD or RFU as a parameter.
    if signals_selected.get("RFU", False):
        X_rfu, labels_rfu = cp.build_feature_matrix(well_history,"rfu",features_selected,selected_wells,include_promoter,include_ahl)
        rfu_cluster_ids = cp.cluster_signal(X_rfu, clustering_mode, n_clusters, dbscan_eps)
        rfu_clusters = cp.build_cluster_map(labels_rfu, rfu_cluster_ids)
        for cid, wells in rfu_clusters.items():
            mean_rfu = np.array([well_history[w]["rfu"] for w in wells], dtype=object)
            mean_rfu = np.mean([np.pad(v, (0, max_rounds - len(v)), 'constant', constant_values=np.nan) for v in mean_rfu], axis=0)
            line = ax_rfu.plot(rounds, mean_rfu, color=colors[cid % len(colors)],
                               linestyle="--", linewidth=2, label=f"Cluster {cid} RFU (n={len(wells)})")
            legend_items.append((line[0], f"Cluster {cid} RFU (n={len(wells)})"))

    # These commands simply set labels for ax_od and ax_rfu that are viewable by the user.
    ax_od.set_xlabel("Round")
    ax_od.set_ylabel("OD")
    ax_rfu.set_ylabel("RFU")
    ax_od.set_title("Clustered Mean OD and RFU Curves")

    # Embed the resultant plot in GUI with FigureCanvasTkAgg, draw it and return it to the window
    canvas_plot = FigureCanvasTkAgg(fig, master=plot_window)
    canvas_plot.draw()
    canvas_plot.get_tk_widget().pack(fill="both", expand=True)

    # --- Create separate legend window ---
    # legend_window: popup window with name "Legend"
    legend_window = tk.Toplevel()
    legend_window.title("Legend")
    fig_legend, ax_legend = plt.subplots(figsize=(6, max(4, len(legend_items)*0.35)))
    ax_legend.axis("off")

    # Create dummy lines for legend
    lines = [Line2D([0], [0], color=l.get_color(), linestyle=l.get_linestyle(), linewidth=l.get_linewidth())
             for l, _ in legend_items]
    labels = [label for _, label in legend_items]

    # ncols and next lines center everything based on how many labels are needed
    ncols = max(1, len(labels)//15)
    ax_legend.legend(lines, labels, loc="center", ncol=ncols, frameon=True)
    ax_legend.set_title("Legend")

    # Embed the legend in GUI with FigureCanvasTkAgg, draw it and return it to the window
    canvas_legend = FigureCanvasTkAgg(fig_legend, master=legend_window)
    canvas_legend.draw()
    canvas_legend.get_tk_widget().pack(fill="both", expand=True)

#Update the program timer for each program execution/tick.
#Potentially may be useful to include delta-time implementation for update_timer()
update_timer()
#Update tkinter's window handling for each program excution/tick.
window.mainloop()