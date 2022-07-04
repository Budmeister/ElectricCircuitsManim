from manim import *

class VoltageDefinition(Scene):
    def construct(self):
        electric = Text("Electric")
        potential = Text("Potential")
        difference = Text("Difference")

        group = VGroup(electric, potential, difference)
        group.arrange(DOWN).scale(2.5)
        time = 2.5
        self.play(Succession(*[FadeIn(word) for word in group]), lag_ratio=1.5, run_time=time)
        self.wait()
        self.play(Indicate(electric, color=BLUE, rate_func=smooth))
        self.wait()

        self.play(electric.animate.scale(1/1.2))
        self.wait()

        self.play(Indicate(potential, color=BLUE, rate_func=smooth))
        self.wait()
        
        self.play(potential.animate.scale(1/1.2))
        self.wait()

        self.play(Indicate(difference, color=BLUE, rate_func=smooth))
        self.wait()