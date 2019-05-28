import tkinter as tk
from tkinter import StringVar
    
def run_search():


    top = tk.Tk()
    top.geometry('800x800') # controls the intitial size of gui
    query = StringVar()
    L1 = tk.Label(top, text="SEARCH BAR") # Search Bar Header Label
    L1.pack( side = tk.TOP)
    E1 = tk.Entry(top, textvariable = query, bd = 1, width=100) # text-input bar
    E1.pack(side = tk.TOP, fill=tk.X, padx=10)
    B1 = tk.Button(top, text="Search", command = querySubmitCallback ) # Button
    B1.pack(side = tk.TOP,padx=10)
    text = tk.Text(top)
    Result_Label = tk.Label(top, text="RESULTS")
    Result_Label.pack(side=tk.TOP, padx=10, pady=10)
    T = tk.Text(top, height=40, width=100)
    T.pack(side = tk.TOP)
    
    top.mainloop()


if __name__ == "__main__":
    run_search()
