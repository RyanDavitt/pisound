import tkinter as tk


def run():
    root = tk.Tk(screenName="GUI Test")
    frm = tk.Frame(root, padx=10, pady=10, bg="grey")
    frm.grid()
    tk.Label(frm, text="Helloooo").grid(column=0, row=0)
    tk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
    root.mainloop()
