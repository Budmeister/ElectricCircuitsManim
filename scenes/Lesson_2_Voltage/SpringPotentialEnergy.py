from manim import *
from circuits.circuit_mobjects import *
from global_funcs import *

class SpringPotentialEnergy(Scene):
    def construct(self):
        inductor = InductorElement(DOWN * 4, ORIGIN, 1, 4, 1)
        spring = VGroup(
            inductor,
            Line().align_to(inductor, UP)
        )
        self.add(spring)

        equilibrium = DashedLine(LEFT * 3, RIGHT * 3, color=GRAY)

        scale_width = 0.3
        line1 = Line(ORIGIN, RIGHT * scale_width).align_to(equilibrium, LEFT)
        line2 = always_redraw(lambda: line1.copy().align_to(spring[1], DOWN))
        line3 = always_redraw(lambda: DashedLine(line1.get_center(), line2.get_center()))
        self.add(line1, line2, line3)
        
        scale = ValueTracker(1)
        scale.prev = scale.get_value()
        def spring_updater(m):
            spring.stretch(scale.get_value() / scale.prev, 1, about_edge=DOWN)
            scale.prev = scale.get_value()
        spring.add_updater(spring_updater)

        spring_size = 1
        k = 1000
        max_pe = 125
        def get_dx():
            return spring_size * (1 - scale.get_value())
        def get_pe():
            return 0.5 * k * get_dx() ** 2
        pe = always_redraw(lambda: MathTex("PE=" + str(round(get_pe(), 1)) + "J").next_to(equilibrium, RIGHT))
        ke = always_redraw(lambda: MathTex("KE=" + str(round(max_pe - get_pe(), 1)) + "J").next_to(pe, UP).align_to(pe, LEFT))
        spring.add_updater(lambda m: m.set_color(interpolate_color(WHITE, SPRING_PE_COLOR, get_pe() / max_pe)))
        
        self.add(pe, ke)

        self.play(Create(equilibrium), run_time=0.5)

        ball = Circle(radius=0.3, color=RED, fill_opacity=1).shift(UP * 5)
        self.play(ball.animate.shift(DOWN * 4.7), rate_func=linear, run_time=0.3)
        ball_updater = lambda m: m.move_to(spring[1].get_center() + UP * 0.3)
        ball.add_updater(ball_updater)
        
        rate_func = lambda a: (1 - np.exp(-a * 4)) / (1 - np.exp(-4))
        self.play(scale.animate.set_value(0.5), rate_func=rate_func, run_time=1)

        self.wait()

        self.play(scale.animate.set_value(1), rate_func=lambda a: 1 - rate_func(1 - a), run_time=1)
        ball.remove_updater(ball_updater)

        self.play(ball.animate.shift(UP * 4.7), rate_func=linear, run_time=0.3)


        self.wait()