import tkinter as tk
from tkinter import ttk
import os

class OverlayWindow:
    def __init__(self, on_submit, on_select, on_execute):
        self.on_submit = on_submit
        self.on_select = on_select
        self.on_execute = on_execute
        self.root = tk.Tk()
        self.root.title("CursorOS")
        
        # Mode State
        self.mode = tk.StringVar(value="Auto")
        
        # Always on top and borderless
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        
        # Fixed Professional Dimensions (prevents jerky resizing)
        self.width = 650
        self.height = 480
        self.collapsed_height = 70
        
        self.root.geometry(f'{self.width}x{self.collapsed_height}')
        self._center_window(self.collapsed_height)
        
        # Theme: Deep Obsidian & Electric Blue
        self.colors = {
            'bg': '#0D0D0E',
            'bg_secondary': '#161618',
            'border': '#232326',
            'accent': '#3B82F6',
            'text_main': '#F3F4F6',
            'text_dim': '#9CA3AF',
            'success': '#10B981',
            'error': '#EF4444'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Border Glow Container
        self.outer_border = tk.Frame(self.root, bg=self.colors['border'], padx=1, pady=1)
        self.outer_border.pack(fill='both', expand=True)
        
        self.container = tk.Frame(self.outer_border, bg=self.colors['bg'])
        self.container.pack(fill='both', expand=True)
        
        # --- Header / Input Area ---
        self.header = tk.Frame(self.container, bg=self.colors['bg'], padx=16, pady=12)
        self.header.pack(fill='x')
        
        # Mode Pill
        self.mode_btn = tk.Label(
            self.header, 
            textvariable=self.mode,
            font=("Inter", 8, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg_secondary'],
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.mode_btn.pack(side='left')
        self.mode_btn.bind("<Button-1>", self._toggle_mode)
        
        # Main Entry
        self.entry = tk.Entry(
            self.header,
            font=("Inter", 13),
            bg=self.colors['bg'],
            fg=self.colors['text_main'],
            insertbackground='white',
            bd=0,
            highlightthickness=0
        )
        self.entry.pack(side='left', expand=True, fill='x', padx=16)
        self.entry.insert(0, "Search or command...")
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Return>", lambda e: self.handle_submit())
        self.entry.bind("<Down>", self._focus_results)
        
        # Send Icon
        self.send_icon = tk.Label(
            self.header,
            text="󰁝", # Using a symbol char
            font=("Inter", 14),
            fg=self.colors['text_dim'],
            bg=self.colors['bg'],
            cursor="hand2"
        )
        self.send_icon.pack(side='right')
        self.send_icon.bind("<Button-1>", lambda e: self.handle_submit())
        
        # --- Content Region (Hidden by default) ---
        self.content_scroll = tk.Frame(self.container, bg=self.colors['bg'], padx=16)
        
        # Horizontal Separator
        self.divider = tk.Frame(self.content_scroll, bg=self.colors['border'], height=1)
        
        # Task Stack
        self.task_frame = tk.Frame(self.content_scroll, bg=self.colors['bg'], pady=12)
        self.task_widgets = {}
        
        # Dynamic results / message area
        self.results_area = tk.Frame(self.content_scroll, bg=self.colors['bg'])
        self.result_items = []
        self.selected_index = -1
        
        # Action Bar (Execute Plan)
        self.action_bar = tk.Frame(self.content_scroll, bg=self.colors['bg'], pady=10)
        self.execute_btn = tk.Label(
            self.action_bar,
            text="Run Action Chain",
            font=("Inter", 9, "bold"),
            bg=self.colors['accent'],
            fg='white',
            padx=16,
            pady=6,
            cursor="hand2"
        )
        self.execute_btn.pack(side='right')
        self.execute_btn.bind("<Button-1>", lambda e: self.on_execute())

        self.root.bind("<Escape>", lambda e: self.hide())
        self.root.withdraw()

    def _center_window(self, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f'{self.width}x{int(h)}+{int((sw-self.width)/2)}+{int((sh-h)/2)}')

    def _on_focus_in(self, e):
        if self.entry.get() == "Search or command...":
            self.entry.delete(0, tk.END)
        self.header.config(bg=self.colors['bg_secondary'])
        self.entry.config(bg=self.colors['bg_secondary'])
        self.send_icon.config(bg=self.colors['bg_secondary'], fg=self.colors['accent'])

    def _on_focus_out(self, e):
        if not self.entry.get():
            self.entry.insert(0, "Search or command...")
        self.header.config(bg=self.colors['bg'])
        self.entry.config(bg=self.colors['bg'])
        self.send_icon.config(bg=self.colors['bg'], fg=self.colors['text_dim'])

    def show(self, event=None):
        self.root.deiconify()
        self.root.lift()
        self.root._center_window(self.collapsed_height) # Reset to small
        self.entry.config(state='normal')
        self.entry.focus_set()
        
        # Clear content
        self.content_scroll.pack_forget()
        self.action_bar.pack_forget()
        for w in self.task_frame.winfo_children(): w.destroy()
        for w in self.results_area.winfo_children(): w.destroy()
        self.task_widgets = {}
        self.result_items = []

    def expand(self):
        """Smoothly reveal content area."""
        self.root.geometry(f'{self.width}x{self.height}')
        self._center_window(self.height)
        self.content_scroll.pack(fill='both', expand=True)
        self.divider.pack(fill='x')
        self.task_frame.pack(fill='x')
        self.results_area.pack(fill='both', expand=True)

    def add_task_step(self, task_id, description):
        if not self.content_scroll.winfo_viewable():
            self.expand()
        
        row = tk.Frame(self.task_frame, bg=self.colors['bg'], pady=4)
        row.pack(fill='x')
        
        indicator = tk.Label(row, text="●", font=("Inter", 8), fg='#272729', bg=self.colors['bg'])
        indicator.pack(side='left', padx=(4, 12))
        
        desc = tk.Label(row, text=description, font=("Inter", 10), fg=self.colors['text_dim'], bg=self.colors['bg'])
        desc.pack(side='left')
        
        self.task_widgets[task_id] = {"dot": indicator, "text": desc}
        self.root.update_idletasks()

    def update_task_status(self, task_id, status):
        if task_id not in self.task_widgets: return
        w = self.task_widgets[task_id]
        if status == "in-progress":
            w["dot"].config(fg=self.colors['accent'])
            w["text"].config(fg=self.colors['text_main'])
        elif status == "completed":
            w["dot"].config(fg=self.colors['success'])
        elif status == "failed":
            w["dot"].config(fg=self.colors['error'])
        self.root.update_idletasks()

    def display_message(self, msg):
        self.expand()
        for w in self.results_area.winfo_children(): w.destroy()
        m = tk.Label(
            self.results_area, 
            text=msg, 
            fg=self.colors['text_main'], 
            bg=self.colors['bg'], 
            font=("Inter", 11),
            wraplength=self.width - 60,
            justify='left'
        )
        m.pack(pady=20, anchor='w')
        self.root.update_idletasks()

    def display_results(self, results):
        self.expand()
        for w in self.results_area.winfo_children(): w.destroy()
        self.result_items = []
        
        if not results:
            tk.Label(self.results_area, text="No results found", fg=self.colors['text_dim'], bg=self.colors['bg'], pady=20).pack()
            return

        for i, path in enumerate(results[:3]):
            f = tk.Frame(self.results_area, bg=self.colors['bg'], pady=10, padx=12, cursor="hand2")
            f.pack(fill='x', pady=2)
            
            icon = "󰈞" if os.path.splitext(path)[1] else "󰉋"
            tk.Label(f, text=icon, font=("Inter", 14), bg=self.colors['bg'], fg=self.colors['text_dim']).pack(side='left', padx=(0, 12))
            
            txt = tk.Frame(f, bg=self.colors['bg'])
            txt.pack(side='left', fill='both')
            tk.Label(txt, text=os.path.basename(path), font=("Inter", 11, "bold"), bg=self.colors['bg'], fg=self.colors['text_main']).pack(anchor='w')
            tk.Label(txt, text=path, font=("Inter", 8), bg=self.colors['bg'], fg=self.colors['text_dim']).pack(anchor='w')

            item = {"frame": f, "path": path}
            self.result_items.append(item)
            f.bind("<Button-1>", lambda e, p=path: self.on_select(p))
            # Nested bindings for smoother click
            for child in f.winfo_children():
                child.bind("<Button-1>", lambda e, p=path: self.on_select(p))
                if isinstance(child, tk.Frame):
                    for g in child.winfo_children(): g.bind("<Button-1>", lambda e, p=path: self.on_select(p))

    def _focus_results(self, e):
        if self.result_items:
            self._move_selection(1)

    def _move_selection(self, d):
        if not self.result_items: return
        if self.selected_index != -1:
            self._style_item(self.selected_index, self.colors['bg'])
        self.selected_index = (self.selected_index + d) % len(self.result_items)
        self._style_item(self.selected_index, self.colors['bg_secondary'])
        self.root.bind("<Return>", lambda e: self.on_select(self.result_items[self.selected_index]["path"]))

    def _style_item(self, idx, color):
        item = self.result_items[idx]
        item["frame"].config(bg=color)
        for c in item["frame"].winfo_children():
            c.config(bg=color)
            if isinstance(c, tk.Frame):
                for g in c.winfo_children(): g.config(bg=color)

    def show_plan_ready(self):
        self.expand()
        self.action_bar.pack(fill='x', side='bottom', pady=10)

    def _toggle_mode(self, e):
        m = "Plan" if self.mode.get() == "Auto" else "Auto"
        self.mode.set(m)

    def handle_submit(self):
        val = self.entry.get()
        if val.strip() and val != "Search or command...":
            self.on_submit(val)
            self.entry.config(state='disabled')
        else:
            self.hide()

    def hide(self, event=None):
        self.root.withdraw()
        self.entry.config(state='normal')
        self.entry.delete(0, tk.END)
        self.root.unbind("<Return>")
        self.root.bind("<Return>", lambda e: self.handle_submit())

    def run(self):
        self.root.mainloop()
