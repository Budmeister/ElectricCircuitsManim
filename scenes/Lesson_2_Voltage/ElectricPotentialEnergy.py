from manim import *
from circuits.circuit_mobjects import *
from global_funcs import *
from manim_extensions import *

class ElectricPotentialEnergy(Scene):
    def construct(self):
        max_pe = 1000
        line1_pos = ValueTracker(-6)
        line2_pos = ValueTracker(-4)
        line3_pos = ValueTracker(-2)
        def get_updater(tracker):
            return lambda m, dt: m.move_to(tracker.get_value() * RIGHT)
        line1 = Line(DOWN, UP)
        line1.add_updater(get_updater(line1_pos), call_updater=True)
        line2 = Line(DOWN / 2, UP / 2)
        line2.add_updater(get_updater(line2_pos), call_updater=True)
        line3 = Line(DOWN, UP)
        line3.add_updater(get_updater(line3_pos), call_updater=True)

        
        spring1 = always_redraw(lambda: InductorElement(
            line1.get_midpoint(),
            line2.get_midpoint(),
            0.5, 4, 0.5
        ))
        spring2 = always_redraw(lambda: InductorElement(
            line2.get_midpoint(),
            line3.get_midpoint(),
            0.5, 4, 0.5
        ))

        arrow1 = Arrow(LEFT, RIGHT).scale(0.5).next_to(spring1, LEFT).set_color(BLUE)
        arrow2 = Arrow(RIGHT, LEFT).scale(0.5).next_to(spring2, RIGHT).set_color(BLUE)

        spring_size = 1
        equ_length = 2
        k = 1000
        def get_dx1():
            dx1 = line2_pos.get_value() - line1_pos.get_value() - equ_length
            dx1 *= spring_size / equ_length
            return dx1
        def get_dx2():
            dx2 = line3_pos.get_value() - line2_pos.get_value() - equ_length
            dx2 *= spring_size / equ_length
            return dx2

        def get_pe(dx=None):
            if dx is None:
                dx1 = get_dx1()
                dx2 = get_dx2()
            else:
                dx1 = dx2 = dx / 2 - spring_size
            pe1 = 0.5 * k * dx1 ** 2
            pe2 = 0.5 * k * dx2 ** 2
            return pe1 + pe2
        pe = always_redraw(lambda: MathTex("PE=" + str(round(get_pe(), 1)) + "J").shift(UP * 1.5).align_to(LEFT * 5, LEFT))

        tracker_size = 0.3
        line4 = always_redraw(lambda: Line(ORIGIN, DOWN * tracker_size).next_to(line1, DOWN))
        line5 = always_redraw(lambda: Line(ORIGIN, DOWN * tracker_size).next_to(line3, DOWN))
        line6 = always_redraw(lambda: DashedLine(line4.get_midpoint(), line5.get_midpoint()))
        dx_tracker = always_redraw(
            lambda: MathTex(f"r={round((line3_pos.get_value() - line2_pos.get_value()) * 2 * spring_size / equ_length, 1)}").next_to(line6, DOWN)
        )
        
        self.add(spring1, spring2, line1, line2, line3, arrow1, arrow2, pe, line4, line5, line6, dx_tracker)

        # Graph
        ax = Axes(
            (0, 2.4, 0.4),
            (0, 1200, 100),
            x_length=6,
            y_length=6,
            x_axis_config={
                "include_numbers": True
            },
            y_axis_config={
                "include_numbers": True,
                "numbers_to_exclude": [1100]
            }
        ).align_to(ORIGIN, LEFT)
        x_label = Text("r").scale(0.7).next_to(ax.get_x_axis().get_tip(), DOWN)
        y_label = Text("PE(J)").scale(0.7).next_to(ax.get_y_axis().get_tip(), LEFT)
        # ax.plot(lambda dx: get_pe(dx), (line3_pos.get_value() - line2_pos.get_value(), 1))
        def graph_generator():
            graph = ParametricFunction(
                lambda t: ax.coords_to_point(t, get_pe(t)),
                t_range=np.array([(line3_pos.get_value() - line1_pos.get_value()) * spring_size / equ_length, 2]),
                scaling=ax.x_axis.scaling
            )
            graph.underlying_function = get_pe
            return graph.set_color(SPRING_PE_COLOR)
        graph = always_redraw(graph_generator)
        dot = always_redraw(lambda: Dot(ax.coords_to_point(
            (line3_pos.get_value() - line1_pos.get_value()) * spring_size / equ_length,
            get_pe((line3_pos.get_value() - line1_pos.get_value()) * spring_size / equ_length)
        ), color=YELLOW_A))
        
        self.add(ax, x_label, y_label, graph, dot)
        [
            mob.add_updater(lambda m: m.set_color(interpolate_color(WHITE, SPRING_PE_COLOR, get_pe() / max_pe)))
            for mob in (line1, line2, line3, spring1, spring2)
        ]

        self.wait()

        arrow1.new = always_redraw(
            lambda: Arrow(ORIGIN, LEFT * -get_dx1(), buff=0)
            .align_to(line1, RIGHT)
            .set_color(SPRING_PE_COLOR)
        )
        arrow2.new = always_redraw(
            lambda: Arrow(ORIGIN, RIGHT * -get_dx2(), buff=0)
            .align_to(line3, LEFT)
            .set_color(SPRING_PE_COLOR)
        )
        self.play(
            ReplacementTransform(arrow1, arrow1.new),
            ReplacementTransform(arrow2, arrow2.new)
        )
        arrow1 = arrow1.new
        arrow2 = arrow2.new

        self.wait()

        self.play(
            line1_pos.animate.set_value(-5),
            line3_pos.animate.set_value(-3)
        )
        self.wait()

        self.play(
            line1_pos.animate.set_value(-4.5),
            line3_pos.animate.set_value(-3.5)
        )
        self.wait()

        spring_graph = ax.plot(get_pe, (0, 2)).set_color(SPRING_PE_COLOR)
        self.play(
            *[FadeOut(mob) for mob in 
            (line1, line2, line3, line4, line5, line6, dx_tracker, spring1, spring2, arrow1, arrow2, pe)],
            FadeIn(spring_graph)
        )
        self.remove(graph, dot)

        self.wait()

        # Electric PE ----------------------------------------------------------------------------
        max_pe = 1000
        k = 250
        q1 = 1
        q2 = 1
        right_charge_pos = ValueTracker(-2)
        left_charge_pos = ValueTracker(-6)
        scale = 4/1.2
        def get_r():
            return (right_charge_pos.get_value() - left_charge_pos.get_value()) / scale
        def get_pe(r=None):
            if r is None:
                r = get_r()
            return k * q1 * q2 / r
        def get_f(r=None):
            if r is None:
                r = get_r()
            return q1 * q2 / r ** 2
        # To be used later on -- needs to be added now

        left_charge = VGroup(
            Circle(radius=0.3, fill_opacity=1),
            Text("+").move_to(ORIGIN)
        )
        left_charge.add_updater(lambda m, dt=0:
            m.move_to(left_charge_pos.get_value() * RIGHT)[0].set_color(interpolate_color(BLUE_C, ELECTRIC_PE_COLOR, get_pe() / max_pe))
            ,
            call_updater=True
        )
        right_charge = VGroup(
            Circle(radius=0.3, fill_opacity=1),
            Text("+").move_to(ORIGIN)
        )
        right_charge.add_updater(lambda m, dt=0:
            m.move_to(right_charge_pos.get_value() * RIGHT)[0].set_color(interpolate_color(BLUE_C, ELECTRIC_PE_COLOR, get_pe() / max_pe))
            ,
            call_updater=True
        )
        arrow1 = always_redraw(
            lambda: Arrow(ORIGIN, LEFT * get_f(), buff=0)
            .align_to(left_charge.get_left(), RIGHT)
            .set_color(ELECTRIC_PE_COLOR)
        )
        arrow2 = always_redraw(
            lambda: Arrow(ORIGIN, RIGHT * get_f(), buff=0)
            .align_to(right_charge.get_right(), LEFT)
            .set_color(ELECTRIC_PE_COLOR)
        )

        pe = always_redraw(lambda: MathTex("PE=" + str(round(get_pe(), 1)) + "J").shift(UP * 1.5).align_to(LEFT * 5, LEFT))

        tracker_size = 0.3
        line4 = always_redraw(lambda: Line(ORIGIN, DOWN * tracker_size).next_to(left_charge, DOWN))
        line5 = always_redraw(lambda: Line(ORIGIN, DOWN * tracker_size).next_to(right_charge, DOWN))
        line6 = always_redraw(lambda: DashedLine(line4.get_midpoint(), line5.get_midpoint()))
        dx_tracker = always_redraw(
            lambda: MathTex(f"r={round(get_r(), 1)}").next_to(line6, DOWN)
        )
        
        # Graph
        dx_range = [get_r(), get_r()]
        def graph_generator():
            r = get_r()
            if r < dx_range[0]:
                dx_range[0] = r
            if r > dx_range[1]:
                dx_range[1] = r
            graph = ParametricFunction(
                lambda t: ax.coords_to_point(t, get_pe(t)),
                t_range=np.array(dx_range),
                scaling=ax.x_axis.scaling
            )
            graph.underlying_function = get_pe
            return graph.set_color(ELECTRIC_PE_COLOR)
        graph = always_redraw(graph_generator)
        dot = always_redraw(lambda: Dot(
            ax.coords_to_point(get_r(), get_pe())
        ).set_color(BLUE_B))
        self.add(dot)


        self.play(
            *[FadeIn(mob) for mob in 
            (left_charge, right_charge, line4, line5, line6, dx_tracker, pe, dot, graph, arrow1, arrow2)]
        )

        self.wait()

        self.play(right_charge_pos.animate.set_value(2))
        self.wait()
        self.play(right_charge_pos.animate.set_value(0))
        self.wait()
        self.play(right_charge_pos.animate.set_value(-4))
        self.wait()
        self.play(right_charge_pos.animate.set_value(-5))
        self.wait()

        charge_graph = ax.plot(get_pe, (0.15, 2.5)).set_color(ELECTRIC_PE_COLOR)
        self.play(FadeIn(charge_graph), FadeOut(dot))
        self.remove(graph)
        self.wait()

