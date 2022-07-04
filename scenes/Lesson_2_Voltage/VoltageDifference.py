from manim import *
from manim_extensions import *
from stickman import *
import itertools as it

class ElectronBox(VGroup):
    def __init__(
        self,
        width,
        height,
        electron_generator=None,
        electron_position_initializer=None,
        post_electron_modifier=None,
        chunk_density=(10, 10),
        num_rows=10,
        num_cols=10,
        draw_force_lines=False,
        draw_chunk_lines=False,
        *args,
        **kwargs
    ):
        # self.chunk_density = (rows, cols)
        super().__init__()
        self._box = Rectangle(width=width, height=height, *args, **kwargs)
        if electron_generator is None:
            electron_generator = self.default_electron_generator
        if electron_position_initializer is None:
            electron_position_initializer = self.initialize_electron_position
        if post_electron_modifier is None:
            post_electron_modifier = lambda electrons: electrons
        self.draw_force_lines = draw_force_lines
        self.chunk_density = chunk_density
        self._electrons = [electron_position_initializer(self, electron_generator(), r, c, num_rows, num_cols) for c in range(num_cols) for r in range(num_rows)]
        new_electrons = post_electron_modifier(self._electrons)
        self.add(*new_electrons)
        self.add(self._box)
        self.add_updater(self.update_electron_positions)

        if draw_chunk_lines:
            ul = self._box.get_critical_point(UL)
            dl = self._box.get_critical_point(DL)
            ur = self._box.get_critical_point(UR)
            dr = self._box.get_critical_point(DR)
            gridx = VGroup(*[Line(ul, dl).shift(RIGHT * self._box.width  * i / chunk_density[0]) for i in range(chunk_density[0])]).set_color(GRAY)
            gridy = VGroup(*[Line(ul, ur).shift(DOWN  * self._box.height * i / chunk_density[1]) for i in range(chunk_density[1])]).set_color(GRAY)
            self.add(gridx, gridy)

    def update_electron_positions(self, m, dt):
        # Assign each electron to a chunk
        chunks = [[[] for _ in range(self.chunk_density[0])] for _ in range(self.chunk_density[1])]
        chunk_width = self._box.width / self.chunk_density[1]
        chunk_height = self._box.height / self.chunk_density[0]
        zero = self._box.get_critical_point(UL)
        end = self._box.get_critical_point(DR)
        for electron in self._electrons:
            electron: Mobject
            center = electron[0].get_center() - zero
            c = int(center[0] / chunk_width)
            r = int(-center[1] / chunk_height)
            if c < 0:
                c = 0
            elif c >= self.chunk_density[1]:
                c = self.chunk_density[1] - 1
            if r < 0:
                r = 0
            elif r >= self.chunk_density[0]:
                r = self.chunk_density[0] - 1
            chunks[r][c].append(electron)
        k = 0.1
        wall_k = 2
        speed_damping = -0.04
        speed_multiplier = np.exp(speed_damping * dt)
        get_f = lambda e1, e2: k / np.dot(e1.get_center() - e2.get_center(), e1.get_center() - e2.get_center())
        get_f_lw = lambda e: wall_k / (e.get_center()[0] - zero[0]) ** 2
        get_f_uw = lambda e: wall_k / (e.get_center()[1] - zero[1]) ** 2
        get_f_rw = lambda e: wall_k / (e.get_center()[0] - end[0]) ** 2
        get_f_bw = lambda e: wall_k / (e.get_center()[1] - end[1]) ** 2
        for r in range(self.chunk_density[0]):
            for c in range(self.chunk_density[1]):
                for e1 in chunks[r][c]:
                    f = np.zeros(3)
                    for e2 in it.chain(*(
                        electron
                        for row in 
                        chunks[max(r - 1, 0):min(r + 2, self.chunk_density[0])]
                        for electron in
                        row[max(c - 1, 0):min(c + 2, self.chunk_density[1])] 
                    )):
                        if e1 is e2:
                            continue
                        f += get_f(e1, e2) * norm(e1.get_center() - e2.get_center())
                    if r == 0:
                        f += get_f_uw(e1) * DOWN
                    elif r == self.chunk_density[0] - 1:
                        f += get_f_bw(e1) * UP
                    if c == 0:
                        f += get_f_lw(e1) * RIGHT
                    elif c == self.chunk_density[1] - 1:
                        f += get_f_rw(e1) * LEFT
                    f_mag = np.sqrt(np.dot(f, f))
                    if f_mag >= 1:
                        f *= 1 / f_mag
                    if np.any(np.isnan(f)):
                        f = np.zeros(3)
                    e1.f = f
        for electron in self._electrons:
            electron.shift(electron.v * dt)
            electron.v += electron.f * dt
            electron.v *= speed_multiplier
            center = electron[0].get_center()
            proper_pos = np.array([
                max(zero[0], min(center[0], end[0])),
                max(end[1], min(center[1], zero[1])),
                0
            ])
            if proper_pos[0] != center[0]:
                electron.v[0] *= -0.1
            if proper_pos[1] != center[1]:
                electron.v[1] *= -0.1
            electron.shift(proper_pos - center)
                    



    def default_electron_generator(self):
        group = VGroup(
            Circle(radius=0.1, fill_opacity=1, color=YELLOW),
        )
        if self.draw_force_lines:
            group += Line()
            group.add_updater(lambda m: m[1].become(Line(ORIGIN, m.f).shift(m[0].get_center())))
        return group

    def initialize_electron_position(self, box, electron: Mobject, r, c, num_rows, num_cols):
        # Move the electron to the right place and
        # give it a velocity of zero
        w, h = self._box.width, self._box.height
        x0, y0, _ = self._box.get_critical_point(UL)
        x, y = w / (num_cols + 1) * (c + 1) + x0, -h / (num_rows + 1) * (r + 1) + y0
        electron.move_to(np.array([x, y, 0]))
        electron.v = np.zeros(3)
        return electron

class ElectronBoxTest2(Scene):
    def construct(self):
        def initialize_electron_position(box, electron: Mobject, r, c, num_rows, num_cols):
            # Move the electron to the right place and
            # give it a velocity of zero
            c /= 2
            w, h = box._box.width, box._box.height
            x0, y0, _ = box._box.get_critical_point(UL)
            x, y = w / (num_cols + 1) * (c + 1) + x0, -h / (num_rows + 1) * (r + 1) + y0
            electron.move_to(np.array([x, y, 0]))
            electron.v = np.zeros(3)
            return electron
        def electron_generator():
            electron = VGroup()
            circle = Circle(radius=0.1, color=YELLOW, fill_opacity=1)
            voltage = Circle(radius=2).set_fill((RED, RED, RED), opacity=(1, 0, 0)).set_stroke(BLACK, opacity=0)
            voltage.radial_gradient = True
            electron += voltage
            electron += circle
            return electron
        def post_electron_modifier(electrons: VGroup):
            new_electrons = list(it.chain(*electrons))
            new_electrons.sort(key=lambda x: x.radius, reverse=True)
            return new_electrons
        box = ElectronBox(
            4, 4, chunk_density=(10, 10), num_rows=10, num_cols=10,
            electron_position_initializer=initialize_electron_position, electron_generator=electron_generator,
            post_electron_modifier=post_electron_modifier
        )
        self.add(box)
        self.wait(10)
