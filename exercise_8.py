from turtle import *
from time import *
from math import *

class Watch:
    def __init__(self):
        self.screen = Screen()
        self.screen.setup(width=500, height=500)
        self.screen.title("Watch")
        self.screen.bgcolor("lightblue")
        self.screen.tracer(0, 0)

    def run(self):
        pass

class Number:
    def __init__(self, number, radius=150):
        self.number = number
        self.radius = radius
        self.t = Turtle()
        self.t.hideturtle()
        self.t.penup()

    def draw(self):
        angle = 90 - self.number * 30
        x = self.radius * cos(radians(angle))
        y = self.radius * sin(radians(angle))
        self.t.goto(x, y - 10)
        self.t.write(str(self.number), align="center", font=("Courier", 14, "normal"))

class Dial:
    def __init__(self):
        self.numbers = [Number(i) for i in range(1, 13)]
        self.circle_turtle = Turtle()
        self.circle_turtle.hideturtle()
        self.circle_turtle.speed(0)

    def draw(self):
        self.circle_turtle.penup()
        self.circle_turtle.goto(0, -170)
        self.circle_turtle.pendown()
        self.circle_turtle.color("white")
        self.circle_turtle.begin_fill()
        self.circle_turtle.circle(170)
        self.circle_turtle.end_fill()

        self.circle_turtle.penup()
        self.circle_turtle.goto(0, -175)
        self.circle_turtle.pendown()
        self.circle_turtle.color("sienna")
        self.circle_turtle.pensize(10)
        self.circle_turtle.circle(175)
        self.circle_turtle.pensize(1)

        for number in self.numbers:
            number.draw()

class Hand:
    def __init__(self, length, width, color):
        self.t = Turtle()
        self.t.shape("arrow")
        self.t.shapesize(stretch_wid=width, stretch_len=length)
        self.t.color(color)
        self.t.speed(0)
        self.t.penup()
        self.t.goto(0, 0)
        self.t.pendown()
        self.t.setheading(90)

    def update(self, angle):
        self.t.setheading(90 - angle)

class AnalogWatch(Watch):
    def __init__(self):
        super().__init__()
        self.dial = Dial()
        self.dial.draw()

        self.hour_hand = Hand(6, 0.5, "dodgerblue")
        self.minute_hand = Hand(10, 0.4, "limegreen")
        self.second_hand = Hand(12, 0.2, "tomato")

    def run(self):
        while True:
            now = localtime()
            sec = now.tm_sec
            minute = now.tm_min
            hour = now.tm_hour % 12

            self.second_hand.update(sec * 6)
            self.minute_hand.update(minute * 6 + sec * 0.1)
            self.hour_hand.update(hour * 30 + minute * 0.5)

            self.screen.update()
            sleep(1)

class DigitalWatch(Watch):
    def __init__(self, format_24h=True):
        super().__init__()
        self.format_24h = format_24h
        self.t = Turtle()
        self.t.hideturtle()
        self.t.penup()
        self.t.goto(0, 0)
        self.t.color("black")
        self.t.write("Loading...", align="center", font=("Courier", 40, "bold"))

    def run(self):
        while True:
            now = localtime()
            hour = now.tm_hour
            minute = now.tm_min
            sec = now.tm_sec

            if not self.format_24h:
                suffix = "AM"
                display_hour = hour
                if hour == 0:
                    display_hour = 12
                elif hour > 12:
                    display_hour = hour - 12
                    suffix = "PM"
                time_str = f"{display_hour:02d}:{minute:02d}:{sec:02d} {suffix}"
            else:
                time_str = f"{hour:02d}:{minute:02d}:{sec:02d}"

            self.t.clear()
            self.t.write(time_str, align="center", font=("Courier", 40, "bold"))
            self.screen.update()
            sleep(1)

def draw_button(t, x, y, width, height, text):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.fillcolor("white")
    t.pencolor("black")
    t.begin_fill()
    for _ in range(2):
        t.forward(width)
        t.right(90)
        t.forward(height)
        t.right(90)
    t.end_fill()
    t.penup()
    t.goto(x + width/2, y - height + 15)
    t.write(text, align="center", font=("Arial", 16, "bold"))

def is_inside(x, y, bx, by, bw, bh):
    # bx,by - лівий верхній кут кнопки
    # y знижується вниз у turtle, тому верхній кут має більший y, нижній — менший
    return bx <= x <= bx + bw and by - bh <= y <= by

def main_menu():
    screen = Screen()
    screen.setup(width=500, height=500)
    screen.title("Watch selector")
    screen.bgcolor("lightblue")
    tracer(0, 0)

    drawer = Turtle()
    drawer.hideturtle()
    drawer.speed(0)

    btn_width = 220
    btn_height = 50

    # Координати лівого верхнього кута кнопок
    analog_x, analog_y = -btn_width/2, 80
    digital_12_x, digital_12_y = -btn_width/2, 10
    digital_24_x, digital_24_y = -btn_width/2, -60

    draw_button(drawer, analog_x, analog_y, btn_width, btn_height, "Analog Watch")
    draw_button(drawer, digital_12_x, digital_12_y, btn_width, btn_height, "Digital Watch 12h")
    draw_button(drawer, digital_24_x, digital_24_y, btn_width, btn_height, "Digital Watch 24h")

    screen.update()

    def click_handler(x, y):
        if is_inside(x, y, analog_x, analog_y, btn_width, btn_height):
            screen.clearscreen()
            analog_watch = AnalogWatch()
            analog_watch.run()
        elif is_inside(x, y, digital_12_x, digital_12_y, btn_width, btn_height):
            screen.clearscreen()
            digital_watch_12 = DigitalWatch(format_24h=False)
            digital_watch_12.run()
        elif is_inside(x, y, digital_24_x, digital_24_y, btn_width, btn_height):
            screen.clearscreen()
            digital_watch_24 = DigitalWatch(format_24h=True)
            digital_watch_24.run()

    screen.onclick(click_handler)
    screen.mainloop()

if __name__ == "__main__":
    main_menu()
