from manim import *

from . import theoretical as tl

def perp(coord : np.ndarray) -> np.ndarray:
    retval = coord.copy()
    retval[0] = -coord[1]
    retval[1] = coord[0]
    return retval

def interpolate_color_with_midpoint(color1, color2, midpoint, midpoint_val, alpha):
    if alpha < midpoint_val:
        return interpolate_color(color1, midpoint, alpha / midpoint_val)
    else:
        return interpolate_color(midpoint, color2, (alpha - midpoint_val) / (1 - midpoint_val))

HIGH_VOLTAGE_COLOR = "#00FF00"
GROUND_COLOR = GREY
LOW_VOLTAGE_COLOR = "#FF0000"

def get_voltage_color(v, strength=1):
    v = np.arctan(strength * v) / (np.pi / 2)
    if v > 0:
        return interpolate_color(GROUND_COLOR, HIGH_VOLTAGE_COLOR, v)
    else:
        return interpolate_color(GROUND_COLOR, LOW_VOLTAGE_COLOR, -v)

def get_voltage_color_gradient(high, low, strength=1):
    return [get_voltage_color(v) for v in np.linspace(high, low, 10)]


def phasor2real(p, w, time):
    return np.real(p * np.exp(w * time * 1j))

class CircuitMobject(VGroup):
    def __init__(self, start, end, *args, **kwargs):
        super().__init__()
        self.start = start
        self.end = end

class CircuitElementMobject(CircuitMobject):
    def __init__(self, start, end, component_width=0.5, component_length=0.7, 
                do_colored_voltage=False, base_v=0, diff_v=0, w=0,
                reverse_label=False, *args, **kwargs):
        super().__init__(start, end)
        self._reverse_label = reverse_label
        self._component_width = component_width
        self._component_length = component_length

        self._r = end - start
        self._length = np.sqrt(np.dot(self._r, self._r))
        self._rhat = self._r / self._length
        self._midpoint = start + self._r / 2

        self.do_colored_voltage = do_colored_voltage
        self.base_v = base_v
        self.diff_v = diff_v
        self.w = w

    def _add_label(self, label):
        self._label = Text(label).scale(0.6).next_to(self._midpoint, perp(self._rhat) * (-1 if self._reverse_label else 1), 
            buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER + self._component_width / 2)
        self.add(self._label)

    def get_label(self):
        return self._label

    def set_reverse_label(self, reverse_label):
        self._reverse_label = reverse_label
        self._label.next_to(self._midpoint, perp(self._rhat) * (-1 if self._reverse_label else 1), 
            buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER + self._component_width / 2)
    
    def set_time(self, time):
        raise NotImplementedError()
    
    def get_start_color(self, time):
        return get_voltage_color(phasor2real(self.base_v + self.diff_v, self.w, time))

    def get_end_color(self, time):
        return get_voltage_color(phasor2real(self.base_v, self.w, time))

class ResistorElement(TipableVMobject):
    def __init__(self, start, end, width, points, *args, **kwargs):
        self._start = start
        self._end = end
        self._width = width
        self._points = points
        self._r = end - start
        self._length = np.sqrt(np.dot(self._r, self._r))
        self._rhat = self._r / self._length
        super().__init__(**kwargs)

    def init_points(self):
        self.generate_points()

    def generate_points(self):
        anchors = []
        handles1 = []
        handles2 = []

        pcoord = self._start
        for point in range(self._points):
            if point % 2 == 1:
                coord = self._start + (point + 0.5) / self._points * self._length * self._rhat + self._width / 2 * perp(self._rhat)
            else:
                coord = self._start + (point + 0.5) / self._points * self._length * self._rhat - self._width / 2 * perp(self._rhat)
            anchor1 = pcoord
            anchor2 = coord
            handle1 = coord
            handle2 = pcoord
            pcoord = coord
            
            anchors.append(anchor1)
            handles1.append(handle1)
            handles2.append(handle2)

        anchors.append(anchor2)
        handles1.append(self._end)
        anchors.append(self._end)
        handles2.append(anchors[-2])

        anchors = np.array(anchors)
        handles1 = np.array(handles1)
        handles2 = np.array(handles2)
        self.set_anchors_and_handles(anchors[:-1], handles1, handles2, anchors[1:])

class Resistor(CircuitElementMobject):
    def __init__(self, start=LEFT, end=RIGHT, component_length=0.8, component_width=0.4, points=6, label=None, *args, **kwargs):
        super().__init__(start, end, component_length=component_length, component_width=component_width, *args, **kwargs)
        rstart = self._midpoint - self._rhat * component_length / 2
        rend = self._midpoint + self._rhat * component_length / 2
    
        self.add(Line(start, rstart))

        self.add(ResistorElement(rstart, rend, component_width, points, sheen_direction=self._rhat))

        self.add(Line(rend, end))

        self.set_time(0)

        if label is not None:
            self._add_label(label)

    def set_time(self, time):
        if not self.do_colored_voltage:
            return
        self[0].set_color(self.get_start_color(time))

        low = phasor2real(self.base_v, self.w, time)
        high = phasor2real(self.base_v + self.diff_v, self.w, time)
        self[1].set_color(get_voltage_color_gradient(high, low))

        self[2].set_color(self.get_end_color(time))

class Capacitor(CircuitElementMobject):
    def __init__(self, start=LEFT, end=RIGHT, component_length=0.2, component_width=0.4, label=None, *args, **kwargs):
        super().__init__(start, end, component_length=component_length, component_width=component_width, *args, **kwargs)
        cstart = self._midpoint - self._rhat * component_length / 2
        cend = self._midpoint + self._rhat * component_length / 2
        self.add(Line(start, cstart))

        self.add(Line(cstart + component_width / 2 * perp(self._rhat), cstart - component_width / 2 * perp(self._rhat)))
        self.add(Line(cend + component_width / 2 * perp(self._rhat), cend - component_width / 2 * perp(self._rhat)))

        self.add(Line(cend, end))
        self.set_time(0)

        if label is not None:
            self._add_label(label)

    def set_time(self, time):
        if not self.do_colored_voltage:
            return
        start_color = self.get_start_color(time)
        self[0].set_color(start_color)
        self[1].set_color(start_color)

        end_color = self.get_end_color(time)
        self[2].set_color(end_color)
        self[3].set_color(end_color)

class InductorElement(TipableVMobject):
    def __init__(self, start, end, width, loops, loop_width, *args, **kwargs):
        self._start = start
        self._end = end
        self._width = width
        self._loops = loops
        self._loop_width = loop_width
        self._r = end - start
        self._length = np.sqrt(np.dot(self._r, self._r))
        self._rhat = self._r / self._length
        super().__init__(**kwargs)

    def init_points(self):
        self.generate_points()

    def generate_points(self):
        anchors = []
        handles1 = []
        handles2 = []


        num_divisions = 2 * self._loops + 3
        for loop in range(self._loops):
            anchor1 = self._start + 2 * loop / num_divisions * self._r
            anchor2 = self._start + (2 * loop + 3) / num_divisions * self._r
            handle1 = anchor1 + perp(self._rhat) * self._loop_width
            handle2 = anchor2 + perp(self._rhat) * self._loop_width
            anchors.append(anchor1)
            handles1.append(handle1)
            handles2.append(handle2)

            anchor3 = self._start + (2 * loop + 2) / num_divisions * self._r
            handle3 = anchor3 - perp(self._rhat) * self._loop_width
            handle2 = anchor2 - perp(self._rhat) * self._loop_width
            anchors.append(anchor2)
            handles1.append(handle2)
            handles2.append(handle3)

        anchors.append(self._start + 2 * self._loops / num_divisions * self._r)
        handles1.append(anchors[-1] + perp(self._rhat) * self._loop_width)
        anchors.append(self._end)
        handles2.append(anchors[-1] + perp(self._rhat) * self._loop_width)
        

        anchors = np.array(anchors)
        handles1 = np.array(handles1)
        handles2 = np.array(handles2)
        self.set_anchors_and_handles(anchors[:-1], handles1, handles2, anchors[1:])

class Inductor(CircuitElementMobject):
    def __init__(self, start=LEFT, end=RIGHT, inductor_length=1, inductor_width=0.4, loops=5, loop_width=0.2, label=None, *args, **kwargs):
        super().__init__(start, end, *args, **kwargs)
        lstart = self._midpoint - self._rhat * inductor_length / 2
        lend = self._midpoint + self._rhat * inductor_length / 2

        self.add(Line(start, lstart))

        self.add(InductorElement(lstart, lend, width=inductor_width, loops=loops, loop_width=loop_width, sheen_direction=self._rhat))

        self.add(Line(lend, end))
        self.set_time(0)
        
        if label is not None:
            self._add_label(label)

    def set_time(self, time):
        if not self.do_colored_voltage:
            return
        self[0].set_color(self.get_start_color(time))

        low = phasor2real(self.base_v, self.w, time)
        high = phasor2real(self.base_v + self.diff_v, self.w, time)
        self[1].set_color(get_voltage_color_gradient(high, low))

        self[2].set_color(self.get_end_color(time))

class IndependantVoltage(CircuitElementMobject):
    def __init__(self, start=LEFT, end=RIGHT, voltage_size=0.5, label=None, *args, **kwargs):
        super().__init__(start, end, component_length=voltage_size, component_width=voltage_size, *args, **kwargs)
        vstart = self._midpoint - self._rhat * voltage_size / 2
        vend = self._midpoint + self._rhat * voltage_size / 2

        self.add(Line(start, vstart))

        self.add(Circle(color=WHITE, radius=voltage_size/2, fill_opacity=0).shift(self._midpoint))

        plus = self._midpoint - self._rhat * voltage_size / 5
        minus = self._midpoint + self._rhat * voltage_size / 5
        minus_size = voltage_size / 4

        self.add(Line(minus + perp(self._rhat) * minus_size / 2, minus - perp(self._rhat) * minus_size / 2))
        self.add(Line(plus + perp(self._rhat) * minus_size / 2, plus - perp(self._rhat) * minus_size / 2))
        self.add(Line(plus + self._rhat * minus_size / 2, plus - self._rhat * minus_size / 2))

        self.add(Line(vend, end))
        self.set_time(0)
        
        if label is not None:
            self._add_label(label)
            

    def set_time(self, time):
        if not self.do_colored_voltage:
            return
        self[0].set_color(self.get_start_color(time))

        self[5].set_color(self.get_end_color(time))

class Wire(CircuitElementMobject):
    def __init__(self, start=LEFT, end=RIGHT, *args, **kwargs):
        super().__init__(start, end, *args, **kwargs)
        self.add(Line(start, end))
        self.set_time(0)

    def set_time(self, time):
        if not self.do_colored_voltage:
            return
        self[0].set_color(self.get_start_color(time))



class Current(CircuitMobject):
    def __init__(self, start, end, i, w, time, current_speed, current_density, *args, **kwargs):
        super().__init__(start, end, *args, **kwargs)
        self.i = i
        self.w = w
        self.current_speed = current_speed
        self.current_density = current_density
        self.set_time(time)

    def set_time(self, time):
        self.time = time
        r = self.start - self.end
        length = np.sqrt(np.dot(r, r))
        rhat = r / length
        dist = -self.current_speed * (np.imag(self.i * np.exp(self.w * time * 1j) / self.w) if self.w != 0 else np.real(self.i)*time)
        start = dist % (1 / self.current_density)

        group = VGroup()

        pos = start
        while pos <= length:
            coord = self.end + pos * rhat
            group.add(Dot(coord, color=YELLOW, radius=DEFAULT_DOT_RADIUS * 0.75))
            pos += 1 / self.current_density

        self.become(group)


class SymmetricVDict(VDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        return self.submob_dict.get(key, self.submob_dict[(key[1], key[0])])


class ACCircuit:
    def __init__(self, circuit: tl.ACCircuit, mob_kwargs, do_colored_voltage=False, *args, **kwargs):
        if mob_kwargs is None:
            mob_kwargs = {}

        self.coords = circuit.coords
        self.current_speed = circuit.current_speed
        self.current_density = circuit.current_density
        
        self._timer = ValueTracker(0)
        
        self._elems = SymmetricVDict()
        self._currents = SymmetricVDict()

        for i in range(circuit.nodes - 1):
            for j in range(i+1, circuit.nodes):
                celem = circuit[i, j]
                if celem is None:
                    continue
                mobject = celem.get_mobject(
                    base_v=circuit.get_voltage(celem.tail),
                    diff_v=celem.get_voltage(head=celem.head),
                    w=celem.w,
                    do_colored_voltage=do_colored_voltage,
                    **mob_kwargs.get(
                    (i, j), mob_kwargs.get((j, i), {})
                ))
                mobject.add_updater(lambda m: m.set_time(self._timer.get_value()))
                current = celem.get_current_mobject(0, self.current_speed, self.current_density)
                current.add_updater(lambda c: c.set_time(self._timer.get_value()))
                self._elems.add({(i, j): mobject})
                self._currents.add({(i, j): current})
        
    def get_timer(self):
        return self._timer
    
    def get_circuit_mobjects(self):
        return self._elems
    
    def get_current_mobjects(self):
        return self._currents
