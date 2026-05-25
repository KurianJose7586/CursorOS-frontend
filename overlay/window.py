import tkinter as tk

class OverlayWindow:
    def __init__(self, on_submit):
        self.on_submit = on_submit
        self.root = tk.Tk()
        self.root.title("CursorOS Overlay")
        
        # Always on top and borderless
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        
        # Center the window
        self.width, self.height = 500, 100
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f'{self.width}x{self.height}+{x}+{y}')
        
        # Styling
        self.root.configure(bg='#2b2b2b')
        
        frame = tk.Frame(self.root, bg='#2b2b2b', bd=2)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.entry = tk.Entry(frame, font=("Arial", 14), bg='#3c3f41', fg='white', insertbackground='white', bd=0)
        self.entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.handle_submit())
        
        submit_btn = tk.Button(frame, text="Submit", command=self.handle_submit, bg='#4e4e4e', fg='white', bd=0, padx=10)
        submit_btn.pack(side='right')
        
        self.root.bind("<Escape>", lambda e: self.hide())
        
        # Start hidden
        self.root.withdraw()

    def show(self, event=None):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.entry.focus_set()

    def handle_submit(self):
        text = self.entry.get()
        if text.strip():
            print(f"Captured input: {text}")
            self.hide() # Hide immediately
            if self.on_submit:
                self.on_submit(text)
        else:
            self.hide()

    def hide(self, event=None):
        self.root.withdraw()
        self.entry.delete(0, tk.END)

    def run(self):
        self.root.mainloop()
