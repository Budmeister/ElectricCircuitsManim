from manim import *
from circuits.circuit_mobjects import *
from circuits import theoretical as tl

class Intro(Scene):
    def construct(self):
        # Build Circuit
        circuit = tl.ACCircuit(nodes=4, w=0)
        circuit.add(
            tl.Wire(0, 1),
            tl.IndependantVoltage(4, 2, 0),
            tl.Wire(2, 3),
            tl.Resistor(4, 1, 3)
        )

        circuit.nodal_analysis()
        circuit.calculate_currents()

        cmob_circuit = circuit.get_mobjects(
            np.array([
                DL * 2,
                DR * 2,
                UL * 2,
                UR * 2
            ]),
            {
                (0, 2): {"label": "4V"},
                (1, 3): {"label": "4Ω"}
            },
            do_colored_voltage=True
        )

        timer = cmob_circuit.get_timer()
        cmobjects = cmob_circuit.get_circuit_mobjects()
        currents = cmob_circuit.get_current_mobjects()
        # Circuit Built

        # Circuit Offset
        pcircuit_offset = ComplexValueTracker(0)
        circuit_offset = ComplexValueTracker(0)
        def circuit_offset_updater(m):
            z = circuit_offset.get_value() - pcircuit_offset.get_value()
            z = np.array([np.real(z), np.imag(z), 0])
            cmob_circuit.coords += z
            cmobjects.shift(z)
            pcircuit_offset.set_value(circuit_offset.get_value())
        circuit_offset.add_updater(circuit_offset_updater)
        
        # Begin Animation
        time = 1
        self.add(cmobjects, currents)
        self.play(timer.animate.set_value(time), run_time=time, rate_func=linear)
        
        surr_rect = SurroundingRectangle(
            VGroup(
                cmobjects[2, 0][1],
                cmobjects[2, 0].get_label()
            )
        )
        time = 2
        self.play(
            timer.animate(rate_func=linear).increment_value(time),
            Succession(Create(surr_rect), FadeOut(surr_rect)),
            run_time=time
        )

        title = Text("Voltage").scale(2).to_edge(DOWN)
        time = 1
        self.play(
            timer.animate(rate_func=linear).increment_value(time),
            circuit_offset.animate.set_value(0.5j),
            Write(title),
            run_time=time
        )
        
        time = 1
        self.play(
            timer.animate(rate_func=linear).increment_value(time),
        )