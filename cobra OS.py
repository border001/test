import tkinter as tk
from tkinter import filedialog, messagebox
from tkhtmlview import HTMLLabel
import os, json, time, platform, glob

# -------------------------- CONFIG --------------------------
USER_FILE = "users.json"

# -------------------------- USER SYSTEM --------------------------
class UserManager:
    def __init__(self, user_file=USER_FILE):
        self.user_file = user_file
        self.users = self.load_users()
        self.current_user = None

    def load_users(self):
        if os.path.exists(self.user_file):
            with open(self.user_file, "r") as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(self.user_file, "w") as f:
            json.dump(self.users, f, indent=4)

    def add_user(self, username, password, email):
        self.users[username] = {"password": password, "email": email}
        self.save_users()

    def validate_login(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            self.current_user = username
            return True
        return False

# -------------------------- BOOTSCREEN --------------------------
def show_bootscreen(root):
    boot = tk.Toplevel(root)
    boot.attributes("-fullscreen", True)
    boot.configure(bg="black")

    tk.Label(boot,text="CobraBIOS v1.0",fg="lime",bg="black",font=("Consolas",30)).pack(pady=50,anchor="w")
    tk.Label(boot,text=f"CPU: {platform.processor()}",fg="lime",bg="black",font=("Consolas",16)).pack(pady=5,anchor="w")
    tk.Label(boot,text=f"RAM: 16GB",fg="lime",bg="black",font=("Consolas",16)).pack(pady=5,anchor="w")
    tk.Label(boot,text="Loading Cobra OS...",fg="lime",bg="black",font=("Consolas",20)).pack(pady=20,anchor="w")
    
    progress_bg = tk.Frame(boot,bg="#333",width=600,height=25)
    progress_bg.pack(pady=20)
    progress_fg = tk.Frame(progress_bg,bg="lime",width=0,height=25)
    progress_fg.place(x=0,y=0)

    boot.update()
    for i in range(601):
        progress_fg.config(width=i)
        boot.update()
        time.sleep(0.004)
    boot.destroy()

# -------------------------- WINDOW MANAGEMENT --------------------------
class WindowManager:
    def __init__(self, root):
        self.root = root
        self.windows = []
        self.task_buttons = []

    def create_window(self, title, width=500, height=400):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f"{width}x{height}")
        win_frame = tk.Frame(win)
        win_frame.pack(fill="both",expand=True)

        # Topbar
        topbar = tk.Frame(win_frame, bg="#222", height=25)
        topbar.pack(fill="x")
        tk.Label(topbar, text=title, bg="#222", fg="white").pack(side="left", padx=5)

        # Buttons
        tk.Button(topbar, text="_", command=win.iconify, width=2).pack(side="right")
        tk.Button(topbar, text="□", command=lambda: win.state('zoomed'), width=2).pack(side="right")
        tk.Button(topbar, text="X", command=lambda: self.close_window(win), width=2).pack(side="right")

        content_frame = tk.Frame(win_frame)
        content_frame.pack(fill="both", expand=True)
        self.windows.append(win)

        # Taskbar integration
        btn = tk.Button(taskbar_frame, text=title, command=lambda: win.deiconify())
        btn.pack(side="left", padx=2)
        self.task_buttons.append((win, btn))

        return win, content_frame

    def close_window(self, win):
        for w, btn in self.task_buttons:
            if w == win:
                btn.destroy()
        win.destroy()

# -------------------------- DESKTOP --------------------------
class Desktop:
    def __init__(self, root, wm):
        self.root = root
        self.wm = wm
        self.frame = tk.Frame(root, bg="#0f172a")
        self.frame.pack(fill="both", expand=True)
        self.icons = []
        self.wallpaper = None

        # Weißer Text in der Mitte
        self.center_label = tk.Label(
            self.frame,
            text="Cobra OS",
            fg="white",
            bg="#0f172a",
            font=("Segoe UI", 60)
        )
        self.center_label.place(relx=0.5, rely=0.5, anchor="center")

    def create_icon(self, name, command, x, y, image=None):
        btn = tk.Button(self.frame, text=name, width=20, height=2, command=command, wraplength=140, justify="center")
        if image:
            btn.config(image=image, compound="top")
        btn.place(x=x, y=y)
        self.icons.append(btn)
        self.make_draggable(btn)

    def make_draggable(self, widget):
        def start_drag(event):
            widget.startX = event.x
            widget.startY = event.y
        def drag(event):
            x = widget.winfo_x() - widget.startX + event.x
            y = widget.winfo_y() - widget.startY + event.y
            widget.place(x=x, y=y)
        widget.bind("<Button-1>", start_drag)
        widget.bind("<B1-Motion>", drag)

    def set_wallpaper(self, file):
        img = tk.PhotoImage(file=file)
        self.wallpaper = img
        bg_label = tk.Label(self.frame, image=img)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# -------------------------- CLOCK --------------------------
def update_clock():
    clock_label.config(text=time.strftime("%H:%M:%S"))
    root.after(1000, update_clock)

# -------------------------- APPS --------------------------
def open_explorer():
    win, frame = wm.create_window("Explorer", 600, 400)
    path_var = tk.StringVar()
    path_var.set(os.getcwd())
    tk.Entry(frame, textvariable=path_var, width=80).pack(pady=5)
    listbox = tk.Listbox(frame, width=80, height=20)
    listbox.pack()

    def update_list(path):
        listbox.delete(0, 'end')
        try:
            for f in os.listdir(path):
                listbox.insert('end', f)
        except: pass
    update_list(os.getcwd())

    def open_selected(event):
        selection = listbox.get(listbox.curselection())
        full_path = os.path.join(path_var.get(), selection)
        if os.path.isfile(full_path):
            os.startfile(full_path)
        else:
            path_var.set(full_path)
            update_list(full_path)
    listbox.bind("<Double-1>", open_selected)

    def go_back():
        path_var.set(os.path.dirname(path_var.get()))
        update_list(path_var.get())
    tk.Button(frame, text="Back", command=go_back).pack(pady=5)

def open_notepad():
    win, frame = wm.create_window("Notepad", 500, 400)
    text = tk.Text(frame)
    text.pack(expand=True, fill="both")
    def save_file():
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if file:
            with open(file,"w") as f:
                f.write(text.get("1.0","end"))
    def load_file():
        file = filedialog.askopenfilename(filetypes=[("Text Files","*.txt")])
        if file:
            with open(file,"r") as f:
                text.delete("1.0","end")
                text.insert("1.0",f.read())
    tk.Button(frame, text="Save", command=save_file).pack(side="left", padx=5)
    tk.Button(frame, text="Load", command=load_file).pack(side="left", padx=5)

def open_browser():
    win, frame = wm.create_window("Browser", 700, 500)
    url_var = tk.StringVar()
    url_var.set("https://www.google.com")
    tk.Entry(frame, textvariable=url_var, width=60).pack(side="top", pady=5)
    html_label = HTMLLabel(frame, html=f"<iframe src='{url_var.get()}' width='100%' height='400'></iframe>")
    html_label.pack(fill="both", expand=True)
    def load_url():
        html_label.set_html(f"<iframe src='{url_var.get()}' width='100%' height='400'></iframe>")
    tk.Button(frame, text="Search", command=load_url).pack(side="top")

def open_settings():
    win, frame = wm.create_window("Settings", 400, 300)
    tk.Label(frame, text="Wallpaper ändern:").pack(pady=5)
    def set_bg():
        file = filedialog.askopenfilename(filetypes=[("Image Files","*.png;*.jpg")])
        if file:
            desktop.set_wallpaper(file)
    tk.Button(frame, text="Hintergrund wählen", command=set_bg).pack()

def open_batch_app():
    win, frame = wm.create_window("Batch Console", 600, 400)
    tk.Label(frame, text="Batch-Befehle eingeben und Enter drücken:", anchor="w").pack(fill="x")
    entry = tk.Entry(frame, width=80)
    entry.pack(pady=5, padx=5)

    output = tk.Text(frame, height=20)
    output.pack(expand=True, fill="both", padx=5, pady=5)

    def execute_command(event=None):
        cmd = entry.get()
        entry.delete(0, 'end')
        if cmd.strip():
            try:
                result = os.popen(cmd).read()
                output.insert("end", f"> {cmd}\n{result}\n")
                output.see("end")
            except Exception as e:
                output.insert("end", f"Fehler: {e}\n")
                output.see("end")

    entry.bind("<Return>", execute_command)

# -------------------------- DESKTOP-APPS VOM WINDOWS-DESKTOP --------------------------
def get_desktop_apps():
    apps = []
    desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    for item in os.listdir(desktop_path):
        full_path = os.path.join(desktop_path, item)
        if os.path.isfile(full_path) and (full_path.lower().endswith('.lnk') or full_path.lower().endswith('.exe')):
            apps.append(full_path)
    return apps

def load_desktop_apps():
    apps = get_desktop_apps()
    x, y = 200, 40
    for app_path in apps:
        name = os.path.splitext(os.path.basename(app_path))[0]
        desktop.create_icon(
            name,
            command=lambda p=app_path: os.startfile(p),
            x=x,
            y=y
        )
        y += 80
        if y > root.winfo_screenheight() - 100:
            y = 40
            x += 180

# -------------------------- LOGIN & SETUP --------------------------
def setup_screen():
    for w in root.winfo_children():
        w.destroy()
    root.configure(bg="#0078D7")
    tk.Label(root,text="Cobra Setup",fg="white",bg="#0078D7",font=("Segoe UI",40)).pack(pady=60)
    username = tk.Entry(root,font=("Segoe UI",20))
    username.insert(0,"Benutzername")
    username.pack(pady=10)
    password = tk.Entry(root,font=("Segoe UI",20))
    password.insert(0,"Passwort")
    password.pack(pady=10)
    email = tk.Entry(root,font=("Segoe UI",20))
    email.insert(0,"Email")
    email.pack(pady=10)
    def finish():
        users.add_user(username.get(), password.get(), email.get())
        login_screen()
    tk.Button(root, text="Fertig", font=("Segoe UI",20), command=finish).pack(pady=20)

def login_screen():
    for w in root.winfo_children():
        w.destroy()
    root.configure(bg="#1e1e1e")
    tk.Label(root,text="Login",fg="white",bg="#1e1e1e",font=("Segoe UI",40)).pack(pady=80)
    username = tk.Entry(root,font=("Segoe UI",20))
    username.pack(pady=10)
    password = tk.Entry(root, show="*", font=("Segoe UI",20))
    password.pack(pady=10)
    def check():
        if users.validate_login(username.get(), password.get()):
            start_desktop()
        else:
            messagebox.showerror("Fehler","Benutzername oder Passwort falsch")
    tk.Button(root,text="Login",font=("Segoe UI",20),command=check).pack(pady=20)

# -------------------------- DESKTOP & TASKBAR --------------------------
def start_desktop():
    for w in root.winfo_children():
        w.destroy()
    root.configure(bg="#0f172a")
    global desktop
    desktop = Desktop(root, wm)

    # Desktop-Apps automatisch laden (nur Windows-Desktop)
    load_desktop_apps()

    # Taskbar
    global taskbar_frame
    taskbar_frame = tk.Frame(root, bg="#111", height=40)
    taskbar_frame.pack(side="bottom", fill="x")
    # Start Button
    start_btn = tk.Button(taskbar_frame, text="Start", command=toggle_start_menu)
    start_btn.pack(side="left", padx=5)
    # Clock
    global clock_label
    clock_label = tk.Label(taskbar_frame, fg="white", bg="#111")
    clock_label.pack(side="right", padx=10)
    update_clock()
    # Start Menu
    global start_menu
    start_menu = tk.Frame(root, bg="#222", width=250, height=400)
    tk.Label(start_menu,text="Cobra OS",bg="#222",fg="white",font=("Segoe UI",20)).pack(pady=10)
    tk.Button(start_menu,text="Explorer",width=20,command=open_explorer).pack(pady=5)
    tk.Button(start_menu,text="Notepad",width=20,command=open_notepad).pack(pady=5)
    tk.Button(start_menu,text="Browser",width=20,command=open_browser).pack(pady=5)
    tk.Button(start_menu,text="Settings",width=20,command=open_settings).pack(pady=5)
    tk.Button(start_menu,text="Batch",width=20,command=open_batch_app).pack(pady=5)
    tk.Button(start_menu,text="Shutdown",width=20,command=root.destroy).pack(pady=20)

def toggle_start_menu():
    if start_menu.winfo_ismapped():
        start_menu.place_forget()
    else:
        start_menu.place(x=0, y=root.winfo_height()-400)

# -------------------------- MAIN --------------------------
root = tk.Tk()
root.title("Cobra OS ")
root.attributes("-fullscreen", True)

users = UserManager()
wm = WindowManager(root)

root.withdraw()
show_bootscreen(root)
root.deiconify()

if users.users:
    login_screen()
else:
    setup_screen()

root.mainloop()
