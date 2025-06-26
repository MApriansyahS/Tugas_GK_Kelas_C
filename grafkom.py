import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from collections import deque
import math

class Shape:
    def __init__(self, shape_type, points, color, width, line_type="solid"):
        self.type = shape_type
        self.points = points
        self.color = color
        self.width = width
        self.line_type = line_type

    def draw(self, canvas):
        if self.type == "line":
            if self.line_type == "solid":
                canvas.create_line(*self.points, fill=self.color, width=self.width)
            elif self.line_type == "dashed":
                canvas.create_line(*self.points, fill=self.color, width=self.width, dash=(8, 4))
            elif self.line_type == "arrow":
                canvas.create_line(*self.points, fill=self.color, width=self.width, arrow=tk.LAST)
        elif self.type == "rect":
            canvas.create_rectangle(*self.points, outline=self.color, width=self.width)
        elif self.type == "oval":
            canvas.create_oval(*self.points, outline=self.color, width=self.width)
        elif self.type == "ellipse":
            canvas.create_oval(*self.points, outline=self.color, width=self.width)  # Perlakuan sama dengan oval
        elif self.type == "triangle":
            canvas.create_polygon(self.points, outline=self.color, fill="", width=self.width)
        elif self.type == "star":
            canvas.create_polygon(self.points, outline=self.color, fill="", width=self.width)
        elif self.type == "hexagon":
            canvas.create_polygon(self.points, outline=self.color, fill="", width=self.width)
        elif self.type == "pentagon":
            canvas.create_polygon(self.points, outline=self.color, fill="", width=self.width)
        elif self.type == "parallelogram":
            canvas.create_polygon(self.points, outline=self.color, fill="", width=self.width)
        elif self.type == "trapezoid":
            canvas.create_polygon(self.points, outline=self.color, fill="", width=self.width)
        elif self.type == "rhombus":
            canvas.create_polygon(self.points, outline=self.color, fill="", width=self.width)
        elif self.type == "text" and hasattr(self, "text"):
            x, y = self.points[0]
            canvas.create_text(x, y, text=self.text, fill=self.color, font=("Arial", max(10, self.width*3)))

    def is_clicked(self, x, y):
        margin = 5
        xs, ys = zip(*self.points)
        return min(xs)-margin <= x <= max(xs)+margin and min(ys)-margin <= y <= max(ys)+margin

    def translate(self, dx, dy):
        self.points = [(x+dx, y+dy) for x, y in self.points]

    def rotate(self, angle_deg):
        angle = math.radians(angle_deg)
        cx = sum(x for x, _ in self.points) / len(self.points)
        cy = sum(y for _, y in self.points) / len(self.points)
        new_points = []
        for x, y in self.points:
            dx, dy = x - cx, y - cy
            new_x = dx * math.cos(angle) - dy * math.sin(angle) + cx
            new_y = dx * math.sin(angle) + dy * math.cos(angle) + cy
            new_points.append((new_x, new_y))
        self.points = new_points

class MiniPaint:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Paint Lengkap")

        self.width, self.height = 800, 600
        self.image = Image.new("RGB", (self.width, self.height), "white")
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.draw_image = ImageDraw.Draw(self.image)

        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.pen_color = "black"
        self.pen_width = 3
        self.mode = "free"
        self.start_x = None
        self.start_y = None
        self.shapes = []
        self.selected_shape = None
        self.undo_stack = []
        self.redo_stack = []
        self.line_type = "solid"  # Default line type

        self.status_var = tk.StringVar()
        self.status_var.set("Mode: Free | Warna: Black")

        self.setup_menu()
        self.setup_ui()
        self.bind_canvas()
        self.setup_statusbar()
        self.root.bind("<Configure>", self.on_resize)  # Tambahkan ini
        self.root.minsize(600, 400)  # Atur minimal window, sesuaikan sesuai kebutuhan



    def on_resize(self, event):
        # Hanya resize jika ukuran canvas berubah dan cukup besar
        if event.widget == self.root:
            min_width, min_height = 600, 400  # Samakan dengan minsize
            new_width = max(self.root.winfo_width(), min_width)
            new_height = max(self.root.winfo_height() - 80, min_height)
            # Jangan resize jika window terlalu kecil
            if new_width <= min_width or new_height <= min_height:
                return
            if (new_width, new_height) != (self.width, self.height):
                self.width, self.height = new_width, new_height
                self.image = self.image.resize((self.width, self.height), Image.BICUBIC)
                self.tk_image = ImageTk.PhotoImage(self.image)
                self.draw_image = ImageDraw.Draw(self.image)
                self.canvas.config(width=self.width, height=self.height)
                self.refresh_canvas()
                self.redraw_all()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command=self.save_image)
        filemenu.add_command(label="Load", command=self.load_image)
        filemenu.add_separator()
        filemenu.add_command(label="Clear", command=self.clear_canvas)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_command(label="Redo", command=self.redo)
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Mini Paint by Weeaboo"))
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X)

        tk.Button(frame, text="Shape", command=self.choose_shape_type).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Line", command=self.choose_line_type).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Fill", command=self.choose_fill_color).pack(side=tk.LEFT, padx=2)  # Tambahkan ini
        
        self.rotate_ccw_btn = tk.Button(frame, text="⟲", command=lambda: self.rotate_selected(-15), state=tk.DISABLED)
        self.rotate_ccw_btn.pack(side=tk.LEFT, padx=2)
        self.rotate_cw_btn = tk.Button(frame, text="⟳", command=lambda: self.rotate_selected(15), state=tk.DISABLED)
        self.rotate_cw_btn.pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Eraser", command=lambda: self.set_mode("eraser")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Warna", command=self.choose_color).pack(side=tk.LEFT, padx=2)

        tk.Label(frame, text="Tebal:").pack(side=tk.LEFT, padx=2)
        self.width_var = tk.IntVar(value=self.pen_width)
        tk.Spinbox(frame, from_=1, to=10, width=3, textvariable=self.width_var, command=self.change_width).pack(side=tk.LEFT)

        self.color_label = tk.Label(frame, text=" ", bg=self.pen_color, width=2)
        self.color_label.pack(side=tk.LEFT, padx=2)

    def setup_statusbar(self):
        status = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.bind("<Motion>", self.update_statusbar)

    def update_statusbar(self, event):
        self.status_var.set(f"Mode: {self.mode.capitalize()} | Warna: {self.pen_color} | Posisi: ({event.x},{event.y})")

    def set_mode(self, mode):
        self.mode = mode
        self.selected_shape = None
        self.status_var.set(f"Mode: {self.mode.capitalize()} | Warna: {self.pen_color}")

    def choose_color(self):
        try:
            color = colorchooser.askcolor()[1]
            if color:
                self.pen_color = color
                self.color_label.config(bg=color)
                self.status_var.set(f"Mode: {self.mode.capitalize()} | Warna: {self.pen_color}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memilih warna: {e}")

    def change_width(self):
        self.pen_width = self.width_var.get()

    def bind_canvas(self):
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("r", self.rotate_selected_key)  # Tambah binding keyboard untuk rotasi

    def on_click(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.mode == "fill":
            # Cek apakah klik di dalam shape
            for shape in reversed(self.shapes):
                if shape.is_clicked(event.x, event.y):
                    # Lakukan flood fill pada titik klik
                    self.flood_fill(event.x, event.y, self.fill_color)
                    self.refresh_canvas()
                    self.save_undo()
                    return
            # Jika tidak ada shape yang diklik, tidak melakukan apa-apa
            messagebox.showinfo("Info", "Klik di dalam shape untuk mengisi warna.")
        elif self.mode == "select":
            self.select_shape(event.x, event.y)
            self.last_drag_x, self.last_drag_y = event.x, event.y
        else:
            self.save_undo()

    def on_drag(self, event):
        if self.mode == "free":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill=self.pen_color, width=self.pen_width)
            self.draw_image.line((self.start_x, self.start_y, event.x, event.y), fill=self.pen_color, width=self.pen_width)
            self.start_x, self.start_y = event.x, event.y
        elif self.mode == "eraser":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="white", width=15)
            self.draw_image.line((self.start_x, self.start_y, event.x, event.y), fill="white", width=15)
            self.start_x, self.start_y = event.x, event.y
        elif self.mode == "select" and self.selected_shape:
            # Translasi shape dengan drag
            dx = event.x - self.last_drag_x
            dy = event.y - self.last_drag_y
            self.selected_shape.translate(dx, dy)
            self.last_drag_x, self.last_drag_y = event.x, event.y
            self.redraw_all(highlight=True)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        if self.mode == "line":
            pts = [(self.start_x, self.start_y), (end_x, end_y)]
            shape = Shape("line", pts, self.pen_color, self.pen_width, self.line_type)
            self.shapes.append(shape)
            self.redraw_all()
            self.save_undo()
            return
        elif self.mode == "rect":
            pts = [(self.start_x, self.start_y), (end_x, end_y)]
        elif self.mode == "oval":
            pts = [(self.start_x, self.start_y), (end_x, end_y)]
        elif self.mode == "ellipse":
            pts = [(self.start_x, self.start_y), (end_x, end_y)]
        elif self.mode == "triangle":
            mx = (self.start_x + end_x) / 2
            pts = [(mx, self.start_y), (self.start_x, end_y), (end_x, end_y)]
        elif self.mode == "star":
            pts = self.make_star(self.start_x, self.start_y, end_x, end_y)
        elif self.mode == "hexagon":
            pts = self.make_polygon(self.start_x, self.start_y, end_x, end_y, 6)
        elif self.mode == "pentagon":
            pts = self.make_polygon(self.start_x, self.start_y, end_x, end_y, 5)
        elif self.mode == "parallelogram":
            pts = self.make_parallelogram(self.start_x, self.start_y, end_x, end_y)
        elif self.mode == "trapezoid":
            pts = self.make_trapezoid(self.start_x, self.start_y, end_x, end_y)
        elif self.mode == "rhombus":
            pts = self.make_rhombus(self.start_x, self.start_y, end_x, end_y)
        elif self.mode == "text":
            text = self.ask_text()
            if not text:
                return
            pts = [(end_x, end_y)]
            shape = Shape("text", pts, self.pen_color, self.pen_width, text=text)
            self.shapes.append(shape)
            self.redraw_all()
            self.save_undo()
            return
        else:
            if self.mode == "select" and self.selected_shape:
                self.save_undo()
            return

        shape = Shape(self.mode, pts, self.pen_color, self.pen_width)
        self.shapes.append(shape)
        self.redraw_all()
        self.save_undo()

    def rotate_selected_key(self, event):
        # Rotasi shape terpilih dengan tombol R
        if self.selected_shape:
            self.save_undo()
            self.selected_shape.rotate(30)
            self.redraw_all(highlight=True)
        else:
            messagebox.showwarning("Peringatan", "Pilih shape terlebih dahulu.")

    def rotate_selected(self, angle):
        if self.selected_shape:
            self.save_undo()
            self.selected_shape.rotate(angle)
            self.redraw_all(highlight=True)
        else:
            messagebox.showwarning("Peringatan", "Pilih shape terlebih dahulu.")

    def select_shape(self, x, y):
        found = False
        for shape in reversed(self.shapes):
            if shape.is_clicked(x, y):
                self.selected_shape = shape
                found = True
                break
        if not found:
            self.selected_shape = None
            messagebox.showinfo("Info", "Tidak ada shape yang dipilih.")
        self.redraw_all(highlight=True)
        # Enable/disable tombol rotasi
        if self.selected_shape:
            self.rotate_cw_btn.config(state=tk.NORMAL)
            self.rotate_ccw_btn.config(state=tk.NORMAL)
        else:
            self.rotate_cw_btn.config(state=tk.DISABLED)
            self.rotate_ccw_btn.config(state=tk.DISABLED)

    def translate_selected(self):
        if self.selected_shape:
            self.save_undo()
            self.selected_shape.translate(30, 30)
            self.redraw_all()
        else:
            messagebox.showwarning("Peringatan", "Pilih shape terlebih dahulu.")

    def delete_selected(self):
        if self.selected_shape:
            self.save_undo()
            self.shapes.remove(self.selected_shape)
            self.selected_shape = None
            self.redraw_all()
            # Disable tombol rotasi
            self.rotate_cw_btn.config(state=tk.DISABLED)
            self.rotate_ccw_btn.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("Peringatan", "Pilih shape terlebih dahulu.")

    def redraw_all(self, highlight=False):
        self.canvas.delete("all")
        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        for shape in self.shapes:
            shape.draw(self.canvas)
        if highlight and self.selected_shape:
            xs, ys = zip(*self.selected_shape.points)
            self.canvas.create_rectangle(min(xs)-5, min(ys)-5, max(xs)+5, max(ys)+5, outline="red", dash=(4,2))
            # Rotation handle
            cx = (min(xs) + max(xs)) / 2
            cy = min(ys) - 25
            self.rotation_handle = self.canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill="orange", outline="black", tags="rotate_handle")
            self.canvas.tag_bind("rotate_handle", "<Button-1>", self.start_rotate)
            self.canvas.tag_bind("rotate_handle", "<B1-Motion>", self.do_rotate)
            self.canvas.tag_bind("rotate_handle", "<ButtonRelease-1>", self.end_rotate)
        else:
            self.rotation_handle = None

    def choose_fill_color(self):
        color = colorchooser.askcolor(title="Pilih warna fill")[1]
        if color:
            self.fill_color = color
            self.set_mode("fill")
            self.status_var.set(f"Mode: Fill | Warna: {self.fill_color}")

    def start_rotate(self, event):
        self.rotating = True
        self.rotate_origin = (event.x, event.y)
        # Simpan posisi pusat objek
        xs, ys = zip(*self.selected_shape.points)
        self.rotate_cx = sum(xs) / len(xs)
        self.rotate_cy = sum(ys) / len(ys)

    def do_rotate(self, event):
        if not hasattr(self, 'rotating') or not self.rotating:
            return
        x0, y0 = self.rotate_origin
        x1, y1 = event.x, event.y
        angle0 = math.atan2(y0 - self.rotate_cy, x0 - self.rotate_cx)
        angle1 = math.atan2(y1 - self.rotate_cy, x1 - self.rotate_cx)
        angle_deg = math.degrees(angle1 - angle0)
        self.selected_shape.rotate(angle_deg)
        self.rotate_origin = (x1, y1)
        self.redraw_all(highlight=True)

    def end_rotate(self, event):
        self.rotating = False
        self.save_undo()

    def flood_fill(self, x, y, hex_color):
        try:
            rgb = self.image.getpixel((x, y))
            fill = self.hex_to_rgb(hex_color)
            if rgb == fill:
                return
            q = deque()
            q.append((x, y))
            px = self.image.load()
            while q:
                cx, cy = q.popleft()
                if (0 <= cx < self.width and 0 <= cy < self.height and px[cx, cy] == rgb):
                    px[cx, cy] = fill
                    q.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
        except Exception as e:
            messagebox.showerror("Error", f"Flood fill gagal: {e}")

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def refresh_canvas(self):
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.canvas_image, image=self.tk_image)

    def save_undo(self):
        # Simpan state shapes untuk undo
        import copy
        self.undo_stack.append(copy.deepcopy(self.shapes))
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.shapes)
            self.shapes = self.undo_stack.pop()
            self.redraw_all()
        else:
            messagebox.showinfo("Info", "Tidak ada aksi untuk di-undo.")

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.shapes)
            self.shapes = self.redo_stack.pop()
            self.redraw_all()
        else:
            messagebox.showinfo("Info", "Tidak ada aksi untuk di-redo.")

    def clear_canvas(self):
        self.save_undo()
        self.shapes.clear()
        self.image = Image.new("RGB", (self.width, self.height), "white")
        self.draw_image = ImageDraw.Draw(self.image)
        self.refresh_canvas()
        self.redraw_all()

    def save_image(self):
        file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file:
            self.image.save(file)
            messagebox.showinfo("Info", f"Gambar disimpan di {file}")

    def load_image(self):
        file = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file:
            try:
                self.image = Image.open(file).convert("RGB")
                self.tk_image = ImageTk.PhotoImage(self.image)
                self.draw_image = ImageDraw.Draw(self.image)
                self.refresh_canvas()
                self.redraw_all()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal load gambar: {e}")

    def choose_line_type(self):
        win = tk.Toplevel(self.root)
        win.title("Pilih Jenis Garis")
        win.grab_set()
        tk.Label(win, text="Pilih jenis garis:").pack(padx=10, pady=10)

        def pilih(jenis):
            self.line_type = jenis
            self.set_mode("line")
            win.destroy()

        tk.Button(win, text="Lurus", width=15, command=lambda: pilih("solid")).pack(pady=2)
        tk.Button(win, text="Putus-putus", width=15, command=lambda: pilih("dashed")).pack(pady=2)
        tk.Button(win, text="Panah", width=15, command=lambda: pilih("arrow")).pack(pady=2)

    def choose_shape_type(self):
        win = tk.Toplevel(self.root)
        win.title("Pilih Shape")
        win.grab_set()
        tk.Label(win, text="Pilih shape:").pack(padx=10, pady=10)

        shapes = [
            ("Rectangle", "rect"),
            ("Oval", "oval"),
            ("Ellipse", "ellipse"),
            ("Triangle", "triangle"),
            ("Star", "star"),
            ("Hexagon", "hexagon"),
            ("Pentagon", "pentagon"),
            ("Parallelogram", "parallelogram"),
            ("Trapezoid", "trapezoid"),
            ("Rhombus", "rhombus"),
        ]

        for label, mode in shapes:
            tk.Button(win, text=label, width=18, command=lambda m=mode: self.set_shape_mode(m, win)).pack(pady=2)

    def set_shape_mode(self, mode, win):
        self.mode = mode
        self.selected_shape = None
        self.status_var.set(f"Mode: {self.mode.capitalize()} | Warna: {self.pen_color}")
        win.destroy()

    def make_star(self, x0, y0, x1, y1):
        from math import sin, cos, pi
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        r = min(abs(x1 - x0), abs(y1 - y0)) / 2
        points = []
        for i in range(10):
            angle = pi/2 + i * pi/5
            radius = r if i % 2 == 0 else r/2
            x = cx + cos(angle) * radius
            y = cy - sin(angle) * radius
            points.append((x, y))
        return points

    def make_polygon(self, x0, y0, x1, y1, sides):
        from math import sin, cos, pi
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        r = min(abs(x1 - x0), abs(y1 - y0)) / 2
        points = []
        for i in range(sides):
            angle = pi/2 + i * 2 * pi / sides
            x = cx + cos(angle) * r
            y = cy - sin(angle) * r
            points.append((x, y))
        return points

    def make_parallelogram(self, x0, y0, x1, y1):
        # Parallelogram dengan offset 1/4 lebar
        dx = (x1 - x0) / 4
        return [
            (x0 + dx, y0),
            (x1, y0),
            (x1 - dx, y1),
            (x0, y1)
        ]

    def make_trapezoid(self, x0, y0, x1, y1):
        # Trapezoid dengan sisi atas lebih pendek
        dx = abs(x1 - x0) / 4
        return [
            (x0 + dx, y0),
            (x1 - dx, y0),
            (x1, y1),
            (x0, y1)
        ]

    def make_rhombus(self, x0, y0, x1, y1):
        # Rhombus (belah ketupat)
        mx = (x0 + x1) / 2
        my = (y0 + y1) / 2
        return [
            (mx, y0),
            (x1, my),
            (mx, y1),
            (x0, my)
        ]

    def ask_text(self):
        import tkinter.simpledialog
        return tkinter.simpledialog.askstring("Input Text", "Masukkan teks:")

    def flood_fill(self, x, y, hex_color):
        try:
            rgb = self.image.getpixel((x, y))
            fill = self.hex_to_rgb(hex_color)
            if rgb == fill:
                return
            q = deque()
            q.append((x, y))
            px = self.image.load()
            while q:
                cx, cy = q.popleft()
                if (0 <= cx < self.width and 0 <= cy < self.height and px[cx, cy] == rgb):
                    px[cx, cy] = fill
                    q.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
        except Exception as e:
            messagebox.showerror("Error", f"Flood fill gagal: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')  # Tambahkan baris ini untuk Windows fullscreen
    app = MiniPaint(root)
    root.mainloop()
