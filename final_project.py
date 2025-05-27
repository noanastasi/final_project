import tkinter as tk
from tkinter import colorchooser, filedialog
import json
from PIL import Image, ImageDraw  # Для PNG

class Shape:
    def __init__(self, x1, y1, x2, y2, outline, width, fill=''):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.outline = outline
        self.width = width
        self.fill = fill
        self.id = None

    def draw(self, canvas):
        pass

    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'x1': self.x1, 'y1': self.y1,
            'x2': self.x2, 'y2': self.y2,
            'outline': self.outline,
            'width': self.width,
            'fill': self.fill
        }

    @classmethod
    def from_dict(cls, data):
        shape_type = data['type']
        if shape_type == 'Line':
            return Line(**data)
        elif shape_type == 'Rectangle':
            return Rectangle(**data)
        elif shape_type == 'Ellipse':
            return Ellipse(**data)

class Line(Shape):
    def draw(self, canvas):
        self.id = canvas.create_line(self.x1, self.y1, self.x2, self.y2,
                                     fill=self.outline, width=self.width)

class Rectangle(Shape):
    def draw(self, canvas):
        self.id = canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                                          outline=self.outline, width=self.width, fill=self.fill)

class Ellipse(Shape):
    def draw(self, canvas):
        self.id = canvas.create_oval(self.x1, self.y1, self.x2, self.y2,
                                     outline=self.outline, width=self.width, fill=self.fill)

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Графічний редактор")

        self.current_shape = 'Line'
        self.color = '#000000'
        self.fill_color = ''
        self.width = 2
        self.shapes = []
        self.tool = 'shape'
        self.temp_id = None

        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack(side=tk.LEFT)

        self.controls = tk.Frame(root)
        self.controls.pack(side=tk.RIGHT, fill=tk.Y)

        self.shape_var = tk.StringVar(value='Line')
        for shape in ['Line', 'Rectangle', 'Ellipse']:
            tk.Radiobutton(self.controls, text=shape, variable=self.shape_var,
                           value=shape, command=self.select_shape).pack(anchor=tk.W)

        tk.Button(self.controls, text='Колір контуру', command=self.choose_color).pack(fill=tk.X)
        tk.Button(self.controls, text='Колір заливки', command=self.choose_fill_color).pack(fill=tk.X)
        tk.Label(self.controls, text='Товщина:').pack()
        self.width_entry = tk.Entry(self.controls)
        self.width_entry.insert(0, '2')
        self.width_entry.pack()

        tk.Button(self.controls, text='Довільне малювання', command=self.use_freehand).pack(fill=tk.X)
        tk.Button(self.controls, text='Ластик', command=self.use_eraser).pack(fill=tk.X)
        tk.Button(self.controls, text='Ласо (переміщення)', command=self.use_lasso).pack(fill=tk.X)

        tk.Button(self.controls, text='Очистити все', command=self.clear_all).pack(fill=tk.X)
        tk.Button(self.controls, text='Зберегти як PNG', command=self.save_as_png).pack(fill=tk.X)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.start_x = self.start_y = 0
        self.selected_shape = None
        self.offset_x = 0
        self.offset_y = 0

    def select_shape(self):
        self.tool = 'shape'
        self.current_shape = self.shape_var.get()

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color

    def choose_fill_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.fill_color = color

    def use_eraser(self):
        self.tool = 'eraser'

    def use_freehand(self):
        self.tool = 'freehand'

    def use_lasso(self):
        self.tool = 'lasso'
        self.selected_shape = None

    def on_click(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.temp_id = None

        if self.tool == 'lasso':
            for shape in reversed(self.shapes):
                if (min(shape.x1, shape.x2) <= event.x <= max(shape.x1, shape.x2) and
                    min(shape.y1, shape.y2) <= event.y <= max(shape.y1, shape.y2)):
                    self.selected_shape = shape
                    self.offset_x = event.x - shape.x1
                    self.offset_y = event.y - shape.y1
                    break

    def on_drag(self, event):
        try:
            width = int(self.width_entry.get())
        except ValueError:
            width = 2

        if self.tool == 'eraser':
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill='white', width=width, capstyle=tk.ROUND)
            self.start_x, self.start_y = event.x, event.y
            return
        elif self.tool == 'freehand':
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill=self.color, width=width, capstyle=tk.ROUND)
            self.start_x, self.start_y = event.x, event.y
            return
        elif self.tool == 'lasso' and self.selected_shape:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.start_x, self.start_y = event.x, event.y
            self.canvas.delete(self.selected_shape.id)
            self.selected_shape.x1 += dx
            self.selected_shape.x2 += dx
            self.selected_shape.y1 += dy
            self.selected_shape.y2 += dy
            self.selected_shape.draw(self.canvas)
            return

        if self.temp_id:
            self.canvas.delete(self.temp_id)

        fill = self.fill_color if self.current_shape in ['Rectangle', 'Ellipse'] else ''
        if self.tool == 'shape':
            if self.current_shape == 'Line':
                self.temp_id = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                                       fill=self.color, width=width)
            elif self.current_shape == 'Rectangle':
                self.temp_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                            outline=self.color, width=width, fill=fill)
            elif self.current_shape == 'Ellipse':
                self.temp_id = self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y,
                                                       outline=self.color, width=width, fill=fill)

    def on_release(self, event):
        if self.tool == 'shape':
            try:
                width = int(self.width_entry.get())
            except ValueError:
                width = 2

            fill = self.fill_color if self.current_shape in ['Rectangle', 'Ellipse'] else ''
            shape_class = {'Line': Line, 'Rectangle': Rectangle, 'Ellipse': Ellipse}[self.current_shape]
            shape = shape_class(self.start_x, self.start_y, event.x, event.y, self.color, width, fill)
            shape.draw(self.canvas)
            self.shapes.append(shape)

            if self.temp_id:
                self.canvas.delete(self.temp_id)
                self.temp_id = None
        elif self.tool == 'lasso':
            self.selected_shape = None

    def clear_all(self):
        self.canvas.delete('all')
        self.shapes.clear()

    def save_as_png(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.canvas.update()
            ps_file = file_path + '.ps'
            self.canvas.postscript(file=ps_file, colormode='color')

            img = Image.open(ps_file)
            img.save(file_path, 'png')

if __name__ == '__main__':
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
