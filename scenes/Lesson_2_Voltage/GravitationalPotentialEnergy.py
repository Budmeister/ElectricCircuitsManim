from manim import *
from stickman import *

class GravitationalPotentialEnergy(Scene):
    def construct(self):
        skyscraper = SVGMobject("./svgs/skyscraper.svg").scale(3)
        self.add(skyscraper)

        self.wait()
        height_count = ValueTracker(0)
        height_count_width = 0.3
        line1 = Line(height_count_width / 2 * LEFT, height_count_width / 2 * RIGHT)
        line2 = always_redraw(lambda: line1.copy().shift(height_count.get_value() * UP))
        line3 = always_redraw(lambda: DashedLine(line1.get_midpoint(), line2.get_midpoint()))
        text  = always_redraw(lambda: Text(str(round(height_count.get_value() / 6 * 300)) + "m").next_to(line3, LEFT))
        line1.next_to(skyscraper, LEFT).align_to(skyscraper, DOWN)
        height_count_group = VGroup(line1, line2, line3, text)
        self.add(height_count_group)
        self.play(height_count.animate.set_value(6), run_time=3)

        self.wait()
        self.play(FadeOut(height_count_group, run_time=0.3), skyscraper.animate.scale(20).align_to(ORIGIN, UR))
        self.wait()

        stickman = StickMan(LEFT + UP * 1.5 + RIGHT * 0.5, leg_angle=np.pi / 6)
        ball = Circle(radius=0.3, color=RED, fill_opacity=1).move_to(stickman.get_right_arm_end() + RIGHT * 0.3)
        stickman.get_right
        self.play(Succession(Create(stickman), Create(ball, run_time=0.2)))

        # PE Equation
        starts = [6, 27]
        pe = MathTex(r"PE &= mgh\\ &= (1kg)(9.8\frac{m}{s^2})(300m)\\ &= 2940J").shift(RIGHT * 4)
        pe = pe[0]
        self.play(Write(pe[:starts[0]]))
        self.wait()
        self.play(ReplacementTransform(pe[2:starts[0]].copy(), pe[starts[0]:starts[1]]))
        self.wait()
        self.play(ReplacementTransform(pe[starts[0]:starts[1]].copy(), pe[starts[1]:]))
        
        # Ball drop
        self.play(
            stickman.right_arm.animate(run_time=0.2).rotate(PI / 10, about_point=stickman.get_left_arm_start()),
            ball.animate(rate_func=lambda a: a**2, run_time=1).shift(DOWN * 8)
        )

        
        self.wait()