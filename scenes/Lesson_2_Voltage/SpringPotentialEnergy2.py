from manim import *
from circuits.circuit_mobjects import *
from global_funcs import *

class SpringPotentialEnergy2(Scene):
    def construct(self):
        max_pe = 350

        line1_pos = ValueTracker(-4)
        line2_pos = ValueTracker(0)
        line3_pos = ValueTracker(4)
        def get_updater(tracker):
            return lambda m, dt: m.move_to(tracker.get_value() * RIGHT)
        line1 = Line(DOWN * 2, UP * 2)
        line1.add_updater(get_updater(line1_pos), call_updater=True)
        line2 = Line(DOWN, UP)
        line2.add_updater(get_updater(line2_pos), call_updater=True)
        line3 = Line(DOWN * 2, UP * 2)
        line3.add_updater(get_updater(line3_pos), call_updater=True)

        spring1 = always_redraw(lambda: InductorElement(
            line1.get_center(),
            line2.get_center(),
            1, 4, 1
        ))
        spring2 = always_redraw(lambda: InductorElement(
            line2.get_center(),
            line3.get_center(),
            1, 4, 1
        ))

        arrow1 = always_redraw(lambda: Arrow(LEFT, RIGHT).next_to(spring1, LEFT))
        arrow2 = always_redraw(lambda: Arrow(RIGHT, LEFT).next_to(spring2, RIGHT))

        spring_size = 1
        equ_length = 4
        k = 1000
        def get_pe():
            dx1 = line2_pos.get_value() - line1_pos.get_value() - equ_length
            dx2 = line3_pos.get_value() - line2_pos.get_value() - equ_length
            dx1 *= spring_size / equ_length
            dx2 *= spring_size / equ_length
            pe1 = 0.5 * k * dx1 ** 2
            pe2 = 0.5 * k * dx2 ** 2
            return pe1 + pe2
        pe = always_redraw(lambda: MathTex("PE=" + str(round(get_pe(), 1)) + "J").shift(UP * 3).align_to(LEFT * 2, LEFT))

        self.add(line1, line2, line3, spring1, spring2, arrow1, arrow2, pe)
        [
            mob.add_updater(lambda m: m.set_color(interpolate_color(WHITE, SPRING_PE_COLOR, get_pe() / max_pe)))
            for mob in (line1, line2, line3, spring1, spring2)
        ]

        max_min = lambda a, l, u: max(min(a, u), l)
        self.wait()
        self.play(
            line1_pos.animate.set_value(-3),
            line3_pos.animate.set_value(3)
        )
        self.wait()
        self.play(
            line1_pos.animate.set_value(-2),
            line3_pos.animate.set_value(2)
        )

        self.wait()