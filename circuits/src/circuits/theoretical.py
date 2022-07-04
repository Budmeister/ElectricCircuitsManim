import numpy as np
from scipy import linalg

from manim import *
from . import circuit_mobjects as cmob

NUMBERS = (int, float, complex, np.number)

class CircuitError(RuntimeError):
    pass

'''
    Superclass for all circuit elements.
'''
class CircuitElement:
    def __init__(self, head, tail, smart_update=True, circuit=None, w=0, *args, **kwargs):
        self.smart_update = smart_update
        self.head = head
        self.tail = tail
        self.w = w if circuit is None else circuit.w
        self.set_circuit(circuit)

    def set_circuit(self, circuit):
        if circuit is not None:
            self.circuit = circuit
            self.w = circuit.w
        else:
            circuit = None

        self._v = None
        self._i = None
        self._z = None
        self.set_voltage(None, head=self.head)
        self.set_current(None, head=self.head)
        self.set_impedance(None)
        if self.smart_update:
            self.do_smart_update()

    '''
        Returns the voltage variable held by this object if it is known. Otherwise, 
        returns None. If the voltage is unknown, this method does not check if the
        voltage is known by the circuit. To accomplish that, call update_voltage().

        Either head or tail must be specified so that a direction can be applied to 
        the voltage.

    '''
    def get_voltage(self, head=None, tail=None):
        if self._v is None:
            return None
        if head == self.head or tail == self.tail:
            return self._v
        elif head == self.tail or tail == self.head:
            return -self._v
        raise ValueError(f"Incorrect target node: Head: {head}, Tail: {tail}")

    '''
        Updates the voltage variable held by this object to match that known by the 
        circuit. 
        
        Returns True if the value changed.
    '''
    def update_voltage(self):
        if self.circuit is not None:
            voltage = self.circuit.voltage_between(self.head, self.tail)
            if isinstance(voltage, NUMBERS):
                self.set_voltage(voltage, head=self.head)
                return True
        return False

    '''
        Sets the voltage variable held by this object. If smart_update is True, then
        this method also checks if the current or impedance can be calculated using
        Ohm's law.

        Either head or tail must be specified so that a direction can be applied to 
        the voltage.

    '''
    def set_voltage(self, v, head=None, tail=None):
        if v is None:
            self._v = None
            return
        if head == self.head or tail == self.tail:
            self._v = v
        elif head == self.tail or tail == self.head:
            self._v = -v
        else:
            raise ValueError(f"Incorrect target node: Head: {head}, Tail: {tail}")
        if self.smart_update and v is not None:
            i = self.get_current(head=self.head)
            z = self.get_impedance()
            if isinstance(i, NUMBERS) and not isinstance(z, NUMBERS) and i != 0:
                self.set_impedance(v / i)
            elif isinstance(z, NUMBERS) and not isinstance(i, NUMBERS) and z != 0:
                self.set_current(v / z, head=self.head)

    '''
        Returns the current variable held by this object if it is known. Otherwise, 
        returns None. 

        Either head or tail must be specified so that a direction can be applied to 
        the current.

    '''
    def get_current(self, head=None, tail=None):
        if self._i is None:
            return None
        if head == self.head or tail == self.tail:
            return self._i
        elif head == self.tail or tail == self.head:
            return -self._i
        raise ValueError(f"Incorrect target node: Head: {head}, Tail: {tail}")

    '''
        Sets the current variable held by this object. If smart_update is True, then
        this method also checks if the voltage or impedance can be calculated using
        Ohm's law.

        Either head or tail must be specified so that a direction can be applied to 
        the current.

    '''
    def set_current(self, i, head=None, tail=None):
        if i is None:
            self._i = None
            return
        if head == self.head or tail == self.tail:
            self._i = i
        elif head == self.tail or tail == self.head:
            self._i = -i
        else:
            raise ValueError(f"Incorrect target node: Head: {head}, Tail: {tail}")
        if self.smart_update and i is not None:
            v = self.get_voltage(head=self.head)
            z = self.get_impedance()
            if isinstance(v, NUMBERS) and not isinstance(z, NUMBERS) and i != 0:
                self.set_impedance(v / i)
            elif isinstance(z, NUMBERS) and not isinstance(v, NUMBERS):
                self.set_voltage(i * z, head=self.head)

    '''
        Returns the impedance variable held by this object if it is known. Otherwise, 
        returns None. 

    '''
    def get_impedance(self):
        return self._z

    '''
        Sets the impedance variable held by this object. If smart_update is True, then
        this method also checks if the voltage or current can be calculated using
        Ohm's law.

    '''
    def set_impedance(self, z):
        self._z = z
        if self.smart_update and z is not None:
            v = self.get_voltage(head=self.head)
            i = self.get_current(head=self.head)
            if isinstance(v, NUMBERS) and not isinstance(i, NUMBERS) and z != 0:
                self.set_current(v / z, head=self.head)
            elif isinstance(i, NUMBERS) and not isinstance(v, NUMBERS):
                self.set_voltage(i * z, head=self.head)
    
    '''
        If one of voltage, current, or impedance is unknown while the other two are known,
        then it is calculated using Ohm's law. This method is not used by the other setters,
        (set_voltage, set_current, set_impedance) which do smart_update, and it does not
        check self.smart_update. It is for manual smart_update.
    '''
    def do_smart_update(self):
        z = self.get_impedance()
        if z == 0:
            self._v = 0
        v = self.get_voltage(head=self.head)
        i = self.get_current(head=self.head)
        unknowns = [
            x for x in 
            [("v", v), ("i", i), ("z", z)]
            if not isinstance(x[1], NUMBERS)
        ]
        if len(unknowns) != 1:
            return
        if unknowns[0][0] == "v":
            self._v = i * z
        elif unknowns[0][0] == "i" and z != 0:
            self._i = v / z
        elif unknowns[0][0] == "z" and i != 0:
            self._z = v / i
    
    def get_mobject(self, *args, **kwargs):
        raise NotImplementedError()

    def get_current_mobject(self, time, current_speed, current_density, *args, **kwargs):
        current_mobject = cmob.Current(
            start=self.circuit.coords[self.head],
            end=self.circuit.coords[self.tail],
            i=self.get_current(self.head),
            w=self.w,
            time=time,
            current_speed=current_speed,
            current_density=current_density,
            *args, **kwargs
        )
        return current_mobject
        


class Resistor(CircuitElement):
    def __init__(self, r, *args, **kwargs):
        self._resistance = r
        super().__init__(*args, **kwargs)

    def set_impedance(self, z):
        super().set_impedance(self._resistance)
    
    def get_mobject(self, *args, **kwargs):
        if self.circuit is None:
            raise ValueError("Cannot get coords for Mobject. circuit is None")
        start = self.circuit.coords[self.head]
        end = self.circuit.coords[self.tail]
        return cmob.Resistor(start, end, *args, **kwargs)
    



class Capacitor(CircuitElement):
    def __init__(self, c, *args, **kwargs):
        self._capacitance = c
        super().__init__(*args, **kwargs)

    def set_impedance(self, z):
        super().set_impedance(1/(1j * self.w * self._capacitance) if self.w != 0 else np.inf)
    
    def get_mobject(self, *args, **kwargs):
        if self.circuit is None:
            raise ValueError("Cannot get coords for Mobject. circuit is None")
        start = self.circuit.coords[self.head]
        end = self.circuit.coords[self.tail]
        return cmob.Capacitor(start, end, *args, **kwargs)


class Inductor(CircuitElement):
    def __init__(self, l, *args, **kwargs):
        self._inductance = l
        super().__init__(*args, **kwargs)

    def set_impedance(self, z):
        super().set_impedance(1j * self.w * self._inductance)
    
    def get_mobject(self, *args, **kwargs):
        if self.circuit is None:
            raise ValueError("Cannot get coords for Mobject. circuit is None")
        start = self.circuit.coords[self.head]
        end = self.circuit.coords[self.tail]
        return cmob.Inductor(start, end, *args, **kwargs)


class IndependantVoltage(CircuitElement):
    def __init__(self, v, *args, **kwargs):
        self._voltage = v
        super().__init__(*args, **kwargs)

    def set_voltage(self, v, head=None, tail=None):
        super().set_voltage(v, head, tail)
        self._v = self._voltage
    
    def get_mobject(self, *args, **kwargs):
        if self.circuit is None:
            raise ValueError("Cannot get coords for Mobject. circuit is None")
        start = self.circuit.coords[self.head]
        end = self.circuit.coords[self.tail]
        return cmob.IndependantVoltage(start, end, *args, **kwargs)


class DependantVoltage(CircuitElement):
    def __init__(self, a, dplus, dminus, *args, **kwargs):
        self.a = a
        self.dplus = dplus
        self.dminus = dminus
        self.smart_update = False
        super().__init__(*args, **kwargs)
    
    def update_voltage(self):
        if not super().update_voltage() and self.circuit is not None:
            voltage = self.circuit.voltage_between(self.dplus, self.dminus)
            if isinstance(voltage, NUMBERS):
                self._v = self.a * voltage
                return True
        return False
    
    def get_mobject(self, *args, **kwargs):
        if self.circuit is None:
            raise ValueError("Cannot get coords for Mobject. circuit is None")
        start = self.circuit.coords[self.head]
        end = self.circuit.coords[self.tail]
        return cmob.IndependantVoltage(start, end, *args, **kwargs)

class Wire(CircuitElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smart_update = False
        self._v = 0
        self._z = 0

    def set_voltage(self, v, head=None, tail=None):
        super().set_voltage(0, head, tail)
    
    def get_mobject(self, *args, **kwargs):
        if self.circuit is None:
            raise ValueError("Cannot get coords for Mobject. circuit is None")
        start = self.circuit.coords[self.head]
        end = self.circuit.coords[self.tail]
        return cmob.Wire(start, end, *args, **kwargs)


class ACCircuit:
    def __init__(self, nodes=4, w=0, ground=0, coords=None, current_speed=1, current_density=2):
        # Rendering options: 
        # coords: ndarray containing the coords of the nodes on the screen
        # current speed: speed of the current in distance per second per amp
        # current density: the number of dots to render per unit distance

        self.adj = [[None] * (x+1) for x in range(nodes)]
        self.nodes = nodes
        self.w = w
        self._voltages = np.zeros(self.nodes)
        self._known_voltages = [False] * self.nodes
        self.ground = ground
        self._known_voltages[ground] = True

        if coords is None:
            self.coords = np.zeros(shape=(self.nodes, 3))
        self.current_speed = current_speed
        self.current_density = current_density
    
    def get_nodal_analysis_equ(self, node, SN=None):
        if SN is None:
            SN = {node}
        equ = np.zeros(shape=self.nodes+1, dtype=np.complex128)
        sumY = 0
        for m in range(self.nodes):
            if m in SN:
                continue
            elem = self[m, node]
            if elem is None:
                continue
            impedance = elem.get_impedance()
            if isinstance(impedance, NUMBERS):
                admittance = 1 / impedance
            else:
                admittance = 0
                print(f"Warning: Element with unknown impedance {elem}")
            sumY += admittance
            equ[m] = admittance
        equ[node] = -sumY
        return equ

    def nodal_analysis(self):
        super_nodes = [{x} for x in range(self.nodes)]
        ground_equ = np.zeros(shape=self.nodes+1)
        ground_equ[self.ground] = 1
        equs = [ground_equ]
        for i in range(self.nodes - 1):
            for j in range(i + 1, self.nodes):
                add_to_supernode = False
                if isinstance(self[i, j], DependantVoltage):
                    equ = np.zeros(shape=self.nodes+1)
                    dvolt = self[i, j]
                    equ[dvolt.head] += 1
                    equ[dvolt.tail] -= 1
                    equ[dvolt.dplus] -= dvolt.a
                    equ[dvolt.dminus] += dvolt.a
                    equs.append(equ)
                    add_to_supernode = True
                else:
                    voltage = self.get_element_voltage(i, j)
                    if isinstance(voltage, NUMBERS):
                        equ = np.zeros(shape=self.nodes+1)
                        equ[i] = 1
                        equ[j] = -1
                        equ[-1] = voltage
                        equs.append(equ)
                        add_to_supernode = True
                if add_to_supernode:
                    less, more = (i, j) if i < j else (j, i)
                    super_nodes[less].update(super_nodes[more])
                    super_nodes[more] = super_nodes[less]
        new_super_nodes = []
        for super_node in super_nodes:
            if super_node not in new_super_nodes:
                new_super_nodes.append(super_node)
        super_nodes = new_super_nodes

        for super_node in super_nodes:
            if self.ground in super_node:
                continue
            equ = np.sum([self.get_nodal_analysis_equ(node, SN=super_node) for node in super_node], axis=0)
            equs.append(equ)
        equs = np.array(equs)
        solution = linalg.solve(equs[:,:-1], equs[:,-1])
        self._voltages = solution.flatten()
        self._known_voltages = [True] * self.nodes

        [elem.update_voltage() for row in self.adj for elem in row if elem is not None]

    def calculate_currents(self):
        trees = []

        nodes_checked = set()

        for i in range(self.nodes):
            if i in nodes_checked:
                continue
            tree = {i: set()}
            queue = [i]

            while len(queue) != 0:
                end = queue.pop(0)
                for j in range(self.nodes):
                    if j in nodes_checked or j in tree:
                        continue
                    if self[end, j] is not None and self.get_element_current(end, j) is None:
                        tree[end].add(j)
                        tree[j] = {end}
                        queue.append(j)
            nodes_checked.add(i)
            [nodes_checked.add(x) for x in tree.keys()]
            if len(tree) > 1:
                trees.append(tree)

        def action(node, parent):
            if parent is not None:
                success = self.KCL(node, parent)
                if not success:
                    raise CircuitError("Voltage loop or insufficient information. Be sure to call nodal_analysis before calling calculate_currents.")

        for tree in trees:
            nodes = list(tree.keys())
            root = nodes[0]
            self.r_post_order(tree, root, None, action)

        
    def r_post_order(self, tree, node, parent, action):
        connections = tree[node]
        for sub in connections:
            if sub != parent:
                self.r_post_order(tree, sub, node, action)
        action(node=node, parent=parent)
    
    def KCL(self, head, tail):
        current_sum = 0
        for j in range(self.nodes):
            if j != head and j != tail and self[j, head] is not None:
                current = self.get_element_current(j, head)
                if not isinstance(current, NUMBERS):
                    return False
                current_sum += current
        self[head, tail].set_current(current_sum, head=head)
        return True

    def get_adj(self, i, j):
        return self.adj[i][j] if i > j else self.adj[j][i]

    def set_adj(self, i, j, obj):
        if i > j:
            self.adj[i][j] = obj
        else:
            self.adj[j][i] = obj

    def __getitem__(self, coord):
        return self.get_adj(coord[0], coord[1])

    def __setitem__(self, coord):
        self.set_adj(coord[0], coord[1])

    def add(self, *obj: CircuitElement):
        for o in obj:
            self.set_adj(o.head, o.tail, o)
            o.set_circuit(self)
    
    def get_element_voltage(self, i, j):
        elem = self[i, j]
        if elem is None:
            return None
        return elem.get_voltage(head=i)
    
    def get_element_current(self, i, j):
        elem = self[i, j]
        if elem is None:
            return None
        return elem.get_current(head=i)

    def voltage_between(self, plus, minus):
        if self._known_voltages[plus] and self._known_voltages[minus]:
            return self._voltages[plus] - self._voltages[minus]
        return None

    def get_voltage(self, i):
        return self._voltages[i] if self._known_voltages[i] else None

    def get_mobjects(self, coords, mob_kwargs : dict = None, *args, **kwargs):
        self.coords = coords
        return cmob.ACCircuit(self, mob_kwargs, *args, **kwargs)


if __name__ == "__main__":
    circuit = ACCircuit(nodes=9)
    circuit.add(Wire(0, 1))
    circuit.add(Wire(1, 2))
    circuit.add(IndependantVoltage(v=5, head=3, tail=0))
    circuit.add(Resistor(r=1, head=4, tail=1))
    circuit.add(IndependantVoltage(v=4, head=5, tail=2))
    circuit.add(Resistor(r=5, head=4, tail=3))
    circuit.add(Resistor(r=2, head=4, tail=5))
    circuit.add(Resistor(r=4, head=6, tail=3))
    circuit.add(Resistor(r=3, head=7, tail=4))
    circuit.add(DependantVoltage(a=3, dplus=4, dminus=1, head=8, tail=5))
    circuit.add(Wire(head=6, tail=7))
    circuit.add(IndependantVoltage(v=6, head=8, tail=7))

    circuit.nodal_analysis()
    circuit.calculate_currents()

    print(circuit._voltages)
    print(circuit._known_voltages)
    currents = [
        [
            circuit.get_element_current(i, j)
            for j in range(circuit.nodes)
        ] for i in range(circuit.nodes)
    ]
    print()

