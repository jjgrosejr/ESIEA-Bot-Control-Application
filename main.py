import tkinter as tk
from tkinter import ttk
import paramiko
import pyautogui
import webview

class Login(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text = "welcome the start page")
        label.pack(pady = 10, padx = 10)
        button = tk.Button(self, text = "go to page one", command = lambda: controller.show_frame(Control))
        button.pack()

class Control(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text = "this is page one")
        label.pack(pady = 10, padx = 10)
        button = tk.Button(self, text = "go to start page", command = lambda: controller.show_frame(Login))
        button.pack()

class main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.columnconfigure(0, weight = 1)

        self.frames = {}

        for F in (Login, Control):
            page_name = F.__name__
            frame = F(parent = container, controller = self)
            self.frames[page_name] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(Login)

    def show_frame(self, page_name):
        frame = self.frames[page_name.__name__]
        frame.tkraise()

if __name__ == "__main__":
    app = main()
    app.mainloop()