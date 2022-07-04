from manim import *
from global_funcs import *
from manim_extensions import *

def map(val, min1, max1, min2, max2):
    val = (val - min1) / (max1 - min1)
    val = val * (max2 - min2) + min2
    return val

class ElectricPotentialEnergy2(Scene):
    def construct(self):
        left_charge = VGroup(
            Circle(radius=0.3, fill_opacity=1).set_color(ELECTRIC_PE_COLOR),
            Text("+").move_to(ORIGIN)
        ).shift(LEFT * 2)
        right_charge = VGroup(
            Circle(radius=0.3, fill_opacity=1).set_color(ELECTRIC_PE_COLOR),
            Text("+").move_to(ORIGIN)
        ).shift(RIGHT * 2)
        field_rate_func = lambda a: map(1 / (10 * a + 1), 1 / 11, 1, 0, 1)
        grad_colors = [interpolate_color(BLACK, GREEN, field_rate_func(a)) for a in np.arange(0, 1, 0.01)]
        field = Circle(radius=10, fill_opacity=1).move_to(left_charge.get_center()).set_color(grad_colors)
        field.radial_gradient = True
        self.add(field)

        self.add(left_charge, right_charge)
        self.wait()
        self.play(left_charge.animate.scale(2))
        self.wait()
        self.play(right_charge.animate.scale(0.2))
        self.wait()

        left_label = MathTex("1C").next_to(left_charge, UP)
        right_label = MathTex("1C").next_to(right_charge, UP)

        tracker_size = 0.3
        line1 = Line(ORIGIN, DOWN * tracker_size).next_to(left_charge, DOWN)
        line2 = line1.copy().align_to(right_charge.get_center(), RIGHT)
        line3 = DashedLine(line1.get_midpoint(), line2.get_midpoint())
        dx_label = MathTex("r=1m").next_to(line3, DOWN)
        dx_group = VGroup(line1, line2, line3, dx_label)

        voltage = MathTex(
            "\\frac{PE}{q} &=",                     # 0
            "{",                                    # 1
            "{k", "{Q", "q", "\\over", "r} }",      # 2, 3, 4, 5, 6
            "\\over",                               # 7
            "q}",                                   # 8
            "=",                                    # 9
            "\\left(5\\frac{Nm^2}{C^2} \\right)",   # 10
            "{",                                    # 11
            "\\frac{(1C)(1C)}{(1m)}",               # 12
            "\\over",                               # 13
            "(1C)",                                 # 14
            "}",                                    # 15
            "={ ",                                  # 16
            "{5", "J", "}\\over", "{1", "C", "} }",  # 17, 18, 19, 20, 21, (22), 23
            "\\\\",                                 # 24
            "&=",                                   # 25
            "{ {k", "{Q", "q", "\\over", "r} }",      # 26, 27, 28, 29, 30
            "\\over",                               # 31
            "q}",                                   # 32
            "=",                                    # 33
            "{",                                    # 34
            "\\left(5\\frac{Nm^2}{C^2} \\right)",   # (34)
            "\\frac{(1C)}{(1m)}",                   # 35
            " }",                                   # 36
            "=5VV"                                   # 37
        ).align_on_border(DL)

        self.play(FadeIn(voltage[0]))
        self.wait()
        self.play(FadeIn(voltage[1:9]))
        self.wait()
        self.play(FadeIn(dx_group))
        self.wait()
        self.play(FadeOut(dx_group))
        self.wait()
        self.play(ReplacementTransform(voltage[1:9].copy(), voltage[9:16]))
        self.play(FadeIn(voltage[16:25]))
        five = MathTex("=", "5{", "J", "\\over", "C", "}").next_to(voltage[17:25], RIGHT)
        self.play(TransformMatchingShapes(voltage[17:25].copy(), five))
        self.wait()
        five_new = MathTex("=", "5", "V").next_to(voltage[17:25], RIGHT)
        self.play(TransformMatchingTex(five, five_new))
        self.wait()

        self.play(TransformMatchingShapes(voltage[1:9].copy(), voltage[25:34]))
        self.wait()
        uncancelled_qs = MathTex(*voltage.tex_strings[25:32]).move_to(voltage[26:33])
        cancel_qs = MathTex("{ {k", "{Q", "\\over", "r} } }").move_to(uncancelled_qs, LEFT)
        self.remove(*voltage[26:33])
        self.add(uncancelled_qs)
        self.play(TransformMatchingTex(uncancelled_qs, cancel_qs))
        self.wait()
        self.play(ReplacementTransform(cancel_qs.copy(), voltage[33:]))
        self.wait()

        right_charge.save_state()
        arrow = Arrow(right_charge.get_center() + UR, right_charge)
        floating_charge_label = MathTex("q=", "1", "C").next_to(right_charge, UL)
        self.play(ShrinkToCenter(right_charge))
        self.play(FadeIn(arrow, shift=DL * 0.5))
        self.wait()

        self.play(Restore(right_charge), FadeIn(floating_charge_label))
        self.wait()

        replacement_frac = MathTex(
            "{ {(1C)({{1}}C)}\\over{(1m)} }",               # 12
            "\\over",                               # 13
            "(1C)",                                 # 14
        ).move_to(voltage[12:15])

        replacement_frac2 = MathTex(
            "{ {(1C)({{2}}C)}\\over{(1m)} }",               # 12
            "\\over",                               # 13
            "(2C)",                                 # 14
        ).move_to(voltage[12:15])
        self.remove(*voltage[12:15])
        self.add(replacement_frac)
        
        replacement_five = MathTex(
            "{5", "J", "}\\over", "{1", "C", "}",  # 17, 18, 19, 20, 21, (22), 23
        ).move_to(voltage[17:24])

        replacement_five2 = MathTex(
            "{10", "J", "}\\over", "{2", "C", "}",  # 17, 18, 19, 20, 21, (22), 23
        ).move_to(voltage[17:24])
        self.remove(*voltage[17:24])
        self.add(replacement_five)

        self.play(
            TransformMatchingTex(replacement_frac, replacement_frac2),
            TransformMatchingTex(replacement_five, replacement_five2),
            TransformMatchingTex(floating_charge_label, MathTex("q=", "2", "C").move_to(floating_charge_label))
        )

        # self.play(FadeIn(voltage), FadeIn(index_labels(voltage)))
        # self.wait()


        #========================================

        # voltage = MathTex(
        #     "\\frac{PE}{q}=",
        #     "{",
        #     "{k", "{Q", "q", "\\over", "r} }",
        #     "\\over",
        #     "q}"
        # ).align_on_border(DL)
        # new_voltage = MathTex(
        #     "\\frac{PE}{q}=",
        #     "{k", "{Q", "\\over", "r} }"
        # ).align_on_border(DL)
        # self.play(FadeIn(voltage[0]))
        # self.wait()
        # self.play(FadeIn(left_label), FadeIn(right_label))
        # self.play(FadeIn(dx_group))
        # self.wait()
        # self.play(FadeOut(dx_group))
        # self.wait()
        # self.play(FadeIn(voltage[1:]))
        # self.play(TransformMatchingTex(voltage, new_voltage))

        # voltage_with_values = MathTex(
        #     "=",
        #     "(5 \\frac{N m^2}{C^2})", "{ {(1C)}", "\\over", "{(1m)} }"
        #     "=",
        #     "5", "J/C"
        # ).next_to(voltage, RIGHT)
        # self.play(FadeIn(voltage_with_values[:5]))
        # self.play(FadeIn(voltage_with_values[5:]))
        # self.wait()
        # self.play(Transform(voltage_with_values[-1], MathTex("V").next_to(voltage_with_values[-2], RIGHT)))

        self.wait()

