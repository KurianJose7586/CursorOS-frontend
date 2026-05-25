import tkinter as tk
from tkinter import ttk
import os

class OverlayWindow:
    def __init__(self, on_submit, on_select):
        self.on_submit = on_submit
        self.on_select = on_select
        self.root = tk.Tk()
        self.root.title("CursorOS Overlay")
        
        # Always on top and borderless
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        
        # Dimensions
        self.base_width = 650
        self.base_height = 80
        self.expanded_height = 450
        
        self.root.geometry(f'{self.base_width}x{self.base_height}')
        self._center_window(self.base_height)
        
        self.root.configure(bg='#1a1a1b')
        
        # --- Input Area ---
        self.main_frame = tk.Frame(self.root, bg='#1a1a1b', padx=15, pady=15)
        self.main_frame.pack(fill='x')
        
        self.entry = tk.Entry(
            self.main_frame, 
            font=("Segoe UI", 14), 
            bg='#272729', 
            fg='#d7dadc', 
            insertbackground='white', 
            bd=0,
            highlightthickness=1,
            highlightbackground='#343437',
            highlightcolor='#3498db'
        )
        self.entry.pack(side='left', expand=True, fill='x', ipady=8)
        self.entry.bind("<Return>", lambda e: self.handle_submit())
        self.entry.bind("<Down>", self._focus_results)
        
        # --- Content Area (Progress + Results) ---
        self.content_frame = tk.Frame(self.root, bg='#1a1a1b', padx=20)
        
        # Progress Area
        self.progress_frame = tk.Frame(self.content_frame, bg='#1a1a1b')
        self.task_widgets = {}
        
        # Results Area
        self.results_frame = tk.Frame(self.content_frame, bg='#1a1a1b', pady=10)
        self.result_items = [] # list of {frame, path, index}
        self.selected_index = -1
        
        self.root.bind("<Escape>", lambda e: self.hide())
        self.root.withdraw()

    def _center_window(self, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.base_width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{self.base_width}x{height}+{x}+{y}')

    def show(self, event=None):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.entry.config(state='normal')
        self.entry.focus_set()
        self.root.geometry(f'{self.base_width}x{self.base_height}')
        self._center_window(self.base_height)
        
        # Clear previous state
        self.content_frame.pack_forget()
        self.progress_frame.pack_forget()
        self.results_frame.pack_forget()
        for widget in self.progress_frame.winfo_children(): widget.destroy()
        for widget in self.results_frame.winfo_children(): widget.destroy()
        self.task_widgets = {}
        self.result_items = []
        self.selected_index = -1

    def add_task_step(self, task_id, description):
        if not self.content_frame.winfo_viewable():
            self.content_frame.pack(fill='both', expand=True)
            self.progress_frame.pack(fill='x', pady=(0, 10))
            self.root.geometry(f'{self.base_width}x{self.expanded_height}')
            self._center_window(self.expanded_height)
        
        row = tk.Frame(self.progress_frame, bg='#1a1a1b', pady=4)
        row.pack(fill='x')
        
        icon = tk.Label(row, text="○", font=("Segoe UI", 12), fg='#4f4f52', bg='#1a1a1b')
        icon.pack(side='left', padx=(0, 10))
        
        desc = tk.Label(row, text=description, font=("Segoe UI", 10), fg='#818384', bg='#1a1a1b')
        desc.pack(side='left')
        
        self.task_widgets[task_id] = {"icon": icon, "desc": desc}
        self.root.update_idletasks()

    def update_task_status(self, task_id, status):
        if task_id not in self.task_widgets: return
        w = self.task_widgets[task_id]
        if status == "in-progress":
            w["icon"].config(text="◑", fg='#3498db')
            w["desc"].config(fg='#d7dadc')
        elif status == "completed":
            w["icon"].config(text="●", fg='#2ecc71')
        elif status == "failed":
            w["icon"].config(text="×", fg='#e74c3c')
        self.root.update_idletasks()

    def display_results(self, results):
        """Displays the top 3 search results."""
        self.results_frame.pack(fill='both', expand=True)
        for widget in self.results_frame.winfo_children(): widget.destroy()
        self.result_items = []
        
        if not results:
            lbl = tk.Label(self.results_frame, text="No matches found.", fg='#818384', bg='#1a1a1b', font=("Segoe UI", 10))
            lbl.pack(pady=10)
            return

        tk.Label(self.results_frame, text="RESULTS (Use ↓ to select)", fg='#3498db', bg='#1a1a1b', font=("Segoe UI", 8, "bold")).pack(anchor='w', pady=(0, 5))

        for i, path in enumerate(results[:3]):
            name = os.path.basename(path)
            item_frame = tk.Frame(self.results_frame, bg='#1a1a1b', pady=8, padx=10, cursor="hand2")
            item_frame.pack(fill='x', pady=2)
            
            # File Icon Placeholder
            ext = os.path.splitext(path)[1].lower()
            icon_text = "📄" if ext else "📁"
            tk.Label(item_frame, text=icon_text, bg='#1a1a1b', fg='#d7dadc', font=("Segoe UI", 12)).pack(side='left', padx=(0, 10))
            
            # Name and Path
            txt_frame = tk.Frame(item_frame, bg='#1a1a1b')
            txt_frame.pack(side='left', fill='both')
            tk.Label(txt_frame, text=name, bg='#1a1a1b', fg='#d7dadc', font=("Segoe UI", 11, "bold")).pack(anchor='w')
            tk.Label(txt_frame, text=path, bg='#1a1a1b', fg='#818384', font=("Segoe UI", 8)).pack(anchor='w')

            item_data = {"frame": item_frame, "path": path, "index": i}
            self.result_items.append(item_data)
            
            # Bindings
            item_frame.bind("<Button-1>", lambda e, p=path: self.on_select(p))
            for child in item_frame.winfo_children():
                child.bind("<Button-1>", lambda e, p=path: self.on_select(p))
                for gchild in child.winfo_children() if isinstance(child, tk.Frame) else []:
                    gchild.bind("<Button-1>", lambda e, p=path: self.on_select(p))

        self.selected_index = -1
        self.root.update_idletasks()

    def _focus_results(self, event):
        if self.result_items:
            self._move_selection(1)

    def _move_selection(self, delta):
        if not self.result_items: return
        
        # Unhighlight previous
        if self.selected_index != -1:
            self.result_items[self.selected_index]["frame"].config(bg='#1a1a1b')
            for child in self.result_items[self.selected_index]["frame"].winfo_children():
                child.config(bg='#1a1a1b')
                if isinstance(child, tk.Frame):
                    for gchild in child.winfo_children(): gchild.config(bg='#1a1a1b')

        self.selected_index = (self.selected_index + delta) % len(self.result_items)
        
        # Highlight new
        item = self.result_items[self.selected_index]
        item["frame"].config(bg='#272729')
        for child in item["frame"].winfo_children():
            child.config(bg='#272729')
            if isinstance(child, tk.Frame):
                for gchild in child.winfo_children(): gchild.config(bg='#272729')
        
        # Bind Return to select when highlighted
        self.root.bind("<Return>", lambda e: self.on_select(item["path"]))

    def handle_submit(self):
        text = self.entry.get()
        if text.strip():
            if self.on_submit:
                self.on_submit(text)
            self.entry.config(state='disabled')
        else:
            self.hide()

    def hide(self, event=None):
        self.root.withdraw()
        self.entry.config(state='normal')
        self.entry.delete(0, tk.END)
        self.root.unbind("<Return>")
        self.root.bind("<Return>", lambda e: self.handle_submit()) # Reset binding

    def run(self):
        self.root.mainloop()
