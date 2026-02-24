import tkinter as tk
import threading
from pynput import keyboard

class MicIndicator:
    def __init__(self):
        self.muted = False
        self.pulse_growing = True
        self.pulse_size = 0

        self.root = tk.Tk()
        self.root.title("Mic Indicator")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")
        self.root.configure(bg="#010101")

        self.canvas_size = 100
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#010101",
            highlightthickness=0,
        )
        self.canvas.pack()

        # Draw the circle
        pad = 10
        self.circle = self.canvas.create_oval(
            pad, pad,
            self.canvas_size - pad, self.canvas_size - pad,
            fill="#22c55e",
            outline="",
        )
        # Glow ring behind the circle for pulse effect
        self.glow = self.canvas.create_oval(
            pad, pad,
            self.canvas_size - pad, self.canvas_size - pad,
            fill="",
            outline="#22c55e",
            width=0,
        )
        self.canvas.tag_lower(self.glow, self.circle)

        # Position top-right
        screen_w = self.root.winfo_screenwidth()
        x = screen_w - self.canvas_size - 20
        y = 20
        self.root.geometry(f"{self.canvas_size}x{self.canvas_size}+{x}+{y}")

        # Dragging
        self._drag_x = 0
        self._drag_y = 0
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)

        # Right-click to quit
        self.canvas.bind("<Button-3>", lambda e: self.quit())

        # Start hotkey listener
        self.listener = keyboard.Listener(on_press=self._on_key)
        self.listener.daemon = True
        self.listener.start()

        # Start pulse animation
        self._animate_pulse()

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")

    def _on_key(self, key):
        if key == keyboard.Key.f12:
            self.root.after(0, self._toggle)

    def _toggle(self):
        self.muted = not self.muted
        if self.muted:
            self.canvas.itemconfig(self.circle, fill="#ef4444")
            self.canvas.itemconfig(self.glow, outline="#ef4444", width=0)
            self.pulse_size = 0
        else:
            self.canvas.itemconfig(self.circle, fill="#22c55e")
            self.canvas.itemconfig(self.glow, outline="#22c55e")

    def _animate_pulse(self):
        if not self.muted:
            if self.pulse_growing:
                self.pulse_size += 1
                if self.pulse_size >= 6:
                    self.pulse_growing = False
            else:
                self.pulse_size -= 1
                if self.pulse_size <= 0:
                    self.pulse_growing = True

            pad = 10 - self.pulse_size
            self.canvas.coords(
                self.glow,
                pad, pad,
                self.canvas_size - pad, self.canvas_size - pad,
            )
            self.canvas.itemconfig(self.glow, width=2, outline="#4ade80")
        else:
            self.canvas.itemconfig(self.glow, width=0)

        self.root.after(50, self._animate_pulse)

    def quit(self):
        self.listener.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MicIndicator()
    app.run()
