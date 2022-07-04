from pde import CartesianGrid, DiffusionPDE, ScalarField, MemoryStorage, PDEBase
from manim import *
from matplotlib import pyplot as plt


class NewDiffusionPDE(PDEBase):
    def __init__(
        self,
        diffusivity: float = 1,
        noise: float = 0,
        bc = "auto_periodic_neumann",
    ):
        """
        Args:
            diffusivity (float):
                The diffusivity of the described species
            noise (float):
                Strength of the (additive) noise term
            bc:
                The boundary conditions applied to the field.
                {ARG_BOUNDARIES}
        """
        super().__init__(noise=noise)

        self.diffusivity = diffusivity
        self.bc = bc
        self.initial_mean = None
    

    def make_modify_after_step(self, state):
        initial_mean = self.initial_mean
        def modify_after_step(state_data: np.ndarray, t=None) -> float:
            if initial_mean is not None:
                change = initial_mean - state_data.mean()
                state_data += change
                return change
            return 0
        return modify_after_step
    
    def solve(self, state, *args, **kwargs):
        self.initial_mean = state.data.mean()
        super().solve(state, *args, **kwargs)

    

    def evolution_rate(  # type: ignore
        self,
        state: ScalarField,
        t: float = 0,
    ) -> ScalarField:
        assert isinstance(state, ScalarField), "`state` must be ScalarField"
        laplace = state.laplace(bc=self.bc, label="evolution rate", args={"t": t})
        return self.diffusivity * laplace - (state - state.data.mean())

class PoolTest1(Scene):
    def construct(self):
        grid = CartesianGrid([[0, 2]], [100])  # generate grid
        data = np.full(100, 0.5)
        data[40:60] = 1
        state = ScalarField(grid, data)  # generate initial condition
        # state.insert([1], 1)

        eq = NewDiffusionPDE(0.001, noise=0.05)  # define the pde
        memory_storage = MemoryStorage()
        t_range = 10
        result = eq.solve(state, t_range=t_range, dt=0.01, tracker=[memory_storage.tracker(0.01)])
        data = np.array(memory_storage.data)

        ax = Axes(
            x_range=(0, 2, 0.25),
            y_range=(0, 1, 0.25),
            x_length=7,
            y_length=5
        )
        xs = np.linspace(0, 2, 100)
        dt = 0.01
        t = ValueTracker(0)
        graph = ax.plot_line_graph(xs, data[0], add_vertex_dots=False).set_color(BLUE)
        def line_updater(m: Mobject):
            _t = int(t.get_value() / dt) % len(data)
            graph.become(ax.plot_line_graph(xs, data[_t], add_vertex_dots=False).set_color(BLUE))
        graph.add_updater(line_updater)

        self.add(graph)
        points = [ax.coords_to_point(*point) for point in 
            (
                (0, 1),
                (0, 0),
                (2, 0),
                (2, 1)
            )    
        ]
        self.add(
            *[
                Line(points[i-1], point)
                for i, point in enumerate(points) if i != 0
            ]
        )

        self.wait(2)
        self.play(t.animate.set_value(t_range), rate_func=linear, run_time=t_range / 3)



