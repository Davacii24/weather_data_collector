from manim import *

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()  # Create a circle
        circle.set_fill(PINK, opacity=0.5)  # Set color and opacity
        square = Square()  # Create a square

        self.play(Create(square))  # Animate square creation
        self.play(Transform(square, circle))  # Transform square into circle
        self.play(FadeOut(square))  # Fade out


        # hwllo