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
        
        # Fixed Professional Dimensions
        self.width = 650
        self.height = 480
        self.collapsed_height = 70
        self.pill_width = 120
        self.pill_height = 4
        
        self.root.geometry(f'{self.width}x{self.collapsed_height}')
        self._center_window(self.collapsed_height)
        
        # Theme: Deep Obsidian & Electric Blue
        self.colors = {
            'bg': '#0D0D0E',
            'bg_secondary': '#161618',
            'border': '#232326',
            'accent': '#3B82F6',
            'glow': '#3B82F6', # Electric Blue glow
            'text_main': '#F3F4F6',
            'text_dim': '#9CA3AF',
            'success': '#10B981',
            'error': '#EF4444'
        }
        
        self.primary_font = "Segoe UI"
        
        self.root.configure(bg=self.colors['bg'])
        
        # Border Glow Container
        self.outer_border = tk.Frame(self.root, bg=self.colors['border'], padx=1, pady=1)
        self.outer_border.pack(fill='both', expand=True)
        
        self.container = tk.Frame(self.outer_border, bg=self.colors['bg'])
        self.container.pack(fill='both', expand=True)
        
        # Pill View (visible when collapsed)
        self.pill_view = tk.Frame(self.container, bg=self.colors['accent'], height=self.pill_height)
        # We don't pack it yet, we'll manage visibility in show/hide
        
        # --- Header / Input Area ---
        self.header = tk.Frame(self.container, bg=self.colors['bg'], padx=16, pady=10)
        self.header.pack(fill='x')
        
        # Mode Pill
        self.mode_btn = tk.Label(
            self.header, 
            textvariable=self.mode,
            font=(self.primary_font, 9, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg_secondary'],
            padx=12,
            pady=4,
            cursor="hand2"
        )
        self.mode_btn.pack(side='left')
        self.mode_btn.bind("<Button-1>", self._toggle_mode)
        
        # Main Entry
        self.entry = tk.Entry(
            self.header,
            font=(self.primary_font, 12),
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
            text="↑",
            font=(self.primary_font, 16, "bold"),
            fg=self.colors['text_dim'],
            bg=self.colors['bg'],
            cursor="hand2"
        )
        self.send_icon.pack(side='right')
        self.send_icon.bind("<Button-1>", lambda e: self.handle_submit())
        
        # --- Content Region ---
        self.content_scroll = tk.Frame(self.container, bg=self.colors['bg'], padx=20)
        self.divider = tk.Frame(self.content_scroll, bg=self.colors['border'], height=1)
        self.task_frame = tk.Frame(self.content_scroll, bg=self.colors['bg'], pady=15)
        self.task_widgets = {}
        self.results_area = tk.Frame(self.content_scroll, bg=self.colors['bg'])
        self.result_items = []
        self.selected_index = -1
        self.action_bar = tk.Frame(self.content_scroll, bg=self.colors['bg'], pady=15)
        self.execute_btn = tk.Label(
            self.action_bar,
            text="Run Action Chain",
            font=(self.primary_font, 10, "bold"),
            bg=self.colors['accent'],
            fg='white',
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.execute_btn.pack(side='right')
        self.execute_btn.bind("<Button-1>", lambda e: self.on_execute())

        self.root.bind("<Escape>", lambda e: self.hide())
        self.root.withdraw()

    def _center_window(self, h, target_y=None):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        if target_y is None:
            target_y = int((sh-h)/2)
        self.root.geometry(f'{self.width}x{int(h)}+{int((sw-self.width)/2)}+{int(target_y)}')

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
        # Animation parameters
        target_y = 40 # Position below camera
        steps = 15
        delay = 8
        
        sw = self.root.winfo_screenwidth()
        
        # Initial state (from Pill)
        curr_x = (sw - self.pill_width) // 2
        curr_y = 0
        
        self.root.geometry(f'{self.pill_width}x{self.pill_height}+{curr_x}+{curr_y}')
        self.pill_view.pack_forget()
        self.header.pack(fill='x')
        self.root.deiconify()
        self.root.lift()
        
        def animate(step):
            if step <= steps:
                t = step / steps
                ease_out = 1 - (1 - t) * (1 - t)
                
                # Interpolate Width, Height, X, Y
                w = int(self.pill_width + (self.width - self.pill_width) * ease_out)
                h = int(self.pill_height + (self.collapsed_height - self.pill_height) * ease_out)
                x = (sw - w) // 2
                y = int(curr_y + (target_y - curr_y) * ease_out)
                
                self.root.geometry(f'{w}x{h}+{x}+{y}')
                self.root.after(delay, lambda: animate(step + 1))
            else:
                self.entry.config(state='normal')
                self.entry.focus_set()

        # Reset
        self.content_scroll.pack_forget()
        self.action_bar.pack_forget()
        for w in self.task_frame.winfo_children(): w.destroy()
        for w in self.results_area.winfo_children(): w.destroy()
        self.task_widgets = {}
        self.result_items = []
        
        animate(0)

    def expand(self):
        # When expanding for results/tasks, we maintain the center-top position
        sw = self.root.winfo_screenwidth()
        curr_y = self.root.winfo_y()
        self.root.geometry(f'{self.width}x{self.height}+{int((sw-self.width)/2)}+{curr_y}')
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
            self.results_area, text=msg, fg=self.colors['text_main'], bg=self.colors['bg'], 
            font=("Inter", 11), wraplength=self.width - 60, justify='left'
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
            for child in f.winfo_children():
                child.bind("<Button-1>", lambda e, p=path: self.on_select(p))
                if isinstance(child, tk.Frame):
                    for g in child.winfo_children(): g.bind("<Button-1>", lambda e, p=path: self.on_select(p))

    def display_org_preview(self, proposal, on_confirm):
        self.expand()
        for w in self.results_area.winfo_children(): w.destroy()
        
        tk.Label(self.results_area, text="Confirm Organization Plan", font=(self.primary_font, 11, "bold"), 
                 fg=self.colors['accent'], bg=self.colors['bg']).pack(pady=(0, 15), anchor='w')
        
        # Scrollable container for many files
        canvas = tk.Canvas(self.results_area, bg=self.colors['bg'], highlightthickness=0, height=250)
        scrollbar = ttk.Scrollbar(self.results_area, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=self.width-60)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.org_vars = []
        for item in proposal:
            row = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'], pady=8, padx=12)
            row.pack(fill='x', pady=2)
            
            # File name (truncated if long)
            fname = item['file']
            if len(fname) > 30: fname = fname[:27] + "..."
            tk.Label(row, text=fname, fg=self.colors['text_main'], bg=self.colors['bg_secondary'], 
                     font=(self.primary_font, 9)).pack(side='left')
            
            tk.Label(row, text=" → ", fg=self.colors['text_dim'], bg=self.colors['bg_secondary']).pack(side='left')
            
            # Target folder entry
            target_var = tk.StringVar(value=item['target'])
            entry = tk.Entry(row, textvariable=target_var, bg=self.colors['bg'], fg=self.colors['text_main'],
                             insertbackground='white', bd=0, highlightthickness=1, 
                             highlightbackground=self.colors['border'], width=20)
            entry.pack(side='right', padx=5)
            
            self.org_vars.append({"file": item['file'], "var": target_var})

        # Confirm Button at the bottom
        btn_frame = tk.Frame(self.results_area, bg=self.colors['bg'], pady=10)
        btn_frame.pack(fill='x')
        
        def handle_confirm():
            final_proposal = [{"file": o["file"], "target": o["var"].get()} for o in self.org_vars]
            on_confirm(final_proposal)

        confirm_btn = tk.Label(
            btn_frame, text="Execute Organization", font=(self.primary_font, 10, "bold"),
            bg=self.colors['success'], fg='white', padx=20, pady=8, cursor="hand2"
        )
        confirm_btn.pack(side='right')
        confirm_btn.bind("<Button-1>", lambda e: handle_confirm())

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
        # Animation parameters
        curr_y = self.root.winfo_y()
        curr_w = self.root.winfo_width()
        curr_h = self.root.winfo_height()
        
        sw = self.root.winfo_screenwidth()
        target_y = 0
        steps = 12
        delay = 8
        
        # Hide interactive elements immediately
        self.header.pack_forget()
        self.content_scroll.pack_forget()
        
        def animate_exit(step):
            if step <= steps:
                t = step / steps
                ease_in = t * t
                
                # Interpolate back to Pill
                w = int(curr_w + (self.pill_width - curr_w) * ease_in)
                h = int(curr_h + (self.pill_height - curr_h) * ease_in)
                x = (sw - w) // 2
                y = int(curr_y + (target_y - curr_y) * ease_in)
                
                self.root.geometry(f'{w}x{h}+{x}+{y}')
                self.root.after(delay, lambda: animate_exit(step + 1))
            else:
                self.pill_view.pack(fill='both', expand=True)
                # Reset state after animation
                self.entry.config(state='normal')
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Search or command...")
                self.root.unbind("<Return>")
                self.root.bind("<Return>", lambda e: self.handle_submit())
                
                # Make pill interactive (click to show)
                self.pill_view.bind("<Button-1>", lambda e: self.show())

        animate_exit(0)

    def run(self):
        self.root.mainloop()
