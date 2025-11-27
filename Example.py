import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import *
import csv
from datetime import datetime

window = Tk()
food = {}


def say_cat(pet_name):
    Copup = tk.Toplevel(window)
    tk.Label(Copup, text= "Food").pack()
    entry_food = tk.Entry(Copup,width=25)
    entry_food.pack()
    tk.Label(Copup, text="Amount").pack(padx= 10, pady= 10)
    entry_amount = tk.Entry(Copup, width=25)
    entry_amount.pack(padx= 10, pady = 10)


    def save_and_close():
        food_name = entry_food.get()
        amount_value = entry_amount.get()
        food[pet_name] = {"food": food_name, "amount": amount_value}
        with open("Food.csv", "w", newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["Pet", "Food", "Amount"])
            for pet, details in food.items():
                writer.writerow([pet, details ["food"], details ["amount"]])
        
            Copup.destroy()
            print(food)
        
    Done_button = tk.Button(Copup, text= "Done", command=save_and_close)
    Done_button.pack()

Cutton = tk.Button(window, text="Cat", command=lambda: say_cat("Cat"))
Dotton = tk.Button(window, text="Dog", command=lambda: say_cat("Dog"))
Bitton = tk.Button(window, text="Bird", command=lambda: say_cat("Bird"))

Cutton.place(x=10, y=10)
Dotton.place(x=50, y=10)
Bitton.place(x=90, y=10)



window.mainloop()