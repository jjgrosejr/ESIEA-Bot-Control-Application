import time
import tkinter as tk
from tkinter import messagebox
import paramiko
import pyautogui

TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080


class App:
    def __init__(self, root):

        # gui window init
        self.root = root
        self.root.title("Raspberry Pi Remote GUI")
        self.ssh_client = None

        # gui input var
        self.username = tk.StringVar()
        self.ip = tk.StringVar()
        self.password = tk.StringVar()

        self.mouse_update_job = None # tikinter timer loop
        self.pressed_keys = set() # tracks current pressed keys
        self.shell = None # ssh shell session

        # load login screen
        self.build_login_frame()

    def build_login_frame(self):
        # create login frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=10, pady=10)

        # username input
        tk.Label(self.login_frame, text="Username").grid(row=0, column=0)
        tk.Entry(self.login_frame, textvariable=self.username).grid(row=0, column=1)

        # ip input
        tk.Label(self.login_frame, text="IP Address").grid(row=1, column=0)
        tk.Entry(self.login_frame, textvariable=self.ip).grid(row=1, column=1)

        # password input
        tk.Label(self.login_frame, text="Password").grid(row=2, column=0)
        tk.Entry(self.login_frame, textvariable=self.password, show='*').grid(row=2, column=1)

        # login button
        tk.Button(self.login_frame, text="Login", command=self.ssh_login).grid(row=3, columnspan=2, pady=10)

    def ssh_login(self):
        ip = self.ip.get()
        username = self.username.get()
        password = self.password.get()

        try:
            # sets up/connects to client
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(ip, username=username, password=password)

            # opens shell
            self.shell = self.ssh_client.invoke_shell()

            # runs control program on esieabot
            self.shell.send("python3 robot.py\n")

            messagebox.showinfo("Success", "SSH Connection Established")

            # trannsition to control interface
            self.login_frame.destroy()
            self.build_main_frame()

        except Exception as e:
            messagebox.showerror("SSH Error", str(e))

    def on_key_press(self, event):
        if event.keysym.upper() in {"W", "A", "S", "D"}:
            self.pressed_keys.add(event.keysym.upper())

    def on_key_release(self, event):
        if event.keysym.upper() in self.pressed_keys:
            self.pressed_keys.remove(event.keysym.upper())

    def build_main_frame(self):
        # create control interface after login
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # not super used rn, webview is a pain in the ass but wtv
        self.browser_frame = tk.Frame(self.main_frame, width=800, height=600)
        self.browser_frame.pack(padx=10, pady=10)

        # display mouse coords
        self.coord_label = tk.Label(self.main_frame, text="Mouse Position:")
        self.coord_label.pack(pady=5)

        # terminal out
        self.output_box = tk.Text(self.main_frame, height=10, state="disabled", bg="#111", fg="#0f0")
        self.output_box.pack(fill=tk.BOTH, padx=10, pady=10)

        # bind wasd key handling
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        # disocnnect button
        self.disconnect_button = tk.Button(self.main_frame, text="Disconnect", command=self.disconnect)
        self.disconnect_button.pack(pady=10)

        self.update_mouse_position()
        self.check_ssh_output()

    def check_ssh_output(self):
        # read ssh output and display
        if self.shell and self.shell.recv_ready():
            try:
                output = self.shell.recv(1024).decode("utf-8")
                self.output_box.config(state="normal")
                self.output_box.insert(tk.END, output)
                self.output_box.see(tk.END)  # Auto-scroll
                self.output_box.config(state="disabled")
            except Exception as e:
                print("Error reading SSH output:", e)

        # run every 100ms
        self.root.after(100, self.check_ssh_output)  # Check again in 100ms

    def disconnect(self):
        # close ssh
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        self.reset_to_login()

    def reset_to_login(self):
        # go bacl to login page
        if self.mouse_update_job is not None:
            self.root.after_cancel(self.mouse_update_job)
            self.mouse_update_job = None
        self.main_frame.destroy()
        self.build_login_frame()

    def update_mouse_position(self):
        if not hasattr(self, "coord_label") or not self.coord_label.winfo_exists():
            return

        # get current mouse pos
        x, y = pyautogui.position()
        screen_width, screen_height = pyautogui.size()

        # calculate as percent
        x_perc = round((x / screen_width) * 100, 2)
        y_perc = round((y / screen_height) * 100, 2)

        # translate to target rez
        translated_x = int((x_perc / 100) * TARGET_WIDTH)
        translated_y = int((y_perc / 100) * TARGET_HEIGHT)

        # update pos label
        self.coord_label.config(
            text=f"Mouse: {x}, {y} | %: {x_perc}%, {y_perc}% | Translated: {translated_x}, {translated_y}"
        )

        # send actual key presses (W, A, S, D)
        if self.shell and self.pressed_keys:
            for key in self.pressed_keys:
                try:
                    message = f"{key} {x_perc} {y_perc}\n"
                    self.shell.send(message)
                except Exception as e:
                    print("Error sending keypress:", e)

        # alwasy send a Q command as placeholder
        if self.shell:
            try:
                placeholder = f"Q {x_perc} {y_perc}\n"
                self.shell.send(placeholder)
            except Exception as e:
                print("Error sending placeholder:", e)

        # repeat every 100ms
        self.mouse_update_job = self.root.after(500, self.update_mouse_position)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
