import numpy as np
from scipy.integrate import solve_ivp

class ApproxCircuit:
    states = {
        "building",
        "analyzing"
    }
    def __init__(self, nodes, ground = 0):
        self.nodes = nodes
        self.ground = ground
        self.v = []
        self.i = []
        self.SN = []
        self.SNsw = None
        self.switch_equs = []
        self.dep_coeffs = []
        self.T = []
        self.Y = np.zeros((nodes, nodes))
        self.NA = None
        self.G = None
        self.C = []
        self.L = []
        self.super_nodes = None

        self.switch_info = []
        self.switch_events = []
        self.initial_switch_states = []
        self.switch_states = None

        self.A = None
        self.e = None
        self.r_to_v = None
        self.t = 0

        # state = "building" or "analyzing"
        self.state = "building"
    
    def check_state(self, state):
        if self.state != state:
            raise ValueError()
    
    def add_resistor(self, r, i, j):
        self.check_state("building")
        self.Y[i, j] = self.Y[j, i] = r
    
    def add_voltage_source(self, v, i, j):
        self.check_state("building")
        self.v.append(v)
        equ = np.zeros(self.nodes)
        equ[i] = 1
        equ[j] = -1
        self.SN.append(equ)
        self.dep_coeffs.append(np.zeros(self.nodes))

    def add_wire(self, i, j):
        self.check_state("building")
        self.add_voltage_source(0, i, j)
    
    def add_capacitor(self, c, i, j):
        self.check_state("building")
        self.v.insert(len(self.C), 0)
        equ = np.zeros(self.nodes)
        equ[i] = 1
        equ[j] = -1
        self.SN.append(equ)
        self.C.append(c)
        self.dep_coeffs.append(np.zeros(self.nodes))
    
    def add_dependant_voltage_source(self, a, i, j, di, dj):
        self.check_state("building")
        self.v.append(0)
        equ = np.zeros(self.nodes)
        dep_coeffs = np.zeros(self.nodes)
        equ[i] = 1
        equ[j] = -1
        dep_coeffs[di] -= a
        dep_coeffs[dj] += a
        self.SN.insert(len(self.C), equ)
        self.dep_coeffs.append(dep_coeffs)
    
    def add_current_source(self, ii, i, j):
        self.check_state("building")
        self.i.append(ii)
        equ = np.zeros(self.nodes)
        equ[i] = 1
        equ[j] = -1
        self.T.append(equ)

    def add_inductor(self, l, i, j):
        self.check_state("building")
        self.i.insert(len(self.L), 0)
        equ = np.zeros(self.nodes)
        equ[i] = 1
        equ[j] = -1
        self.T.insert(len(self.L), equ)
        self.L.append(l)
    
    def add_switch(self, i, j, initial_state=False):
        self.check_state("building")
        self.switch_info.append((i, j))
        self.switch_events.append([])
        self.initial_switch_states.append(initial_state)

    def add_SPDT_switch(self, i, j, k, initial_state=False):
        self.check_state("building")
        self.switch_info.append((i, j, k))
        self.switch_events.append([])
        self.initial_switch_states.append(initial_state)
    
    def add_switch_events(self, s, *events):
        self.switch_events[s] += events
    
    def reset_switch_states(self):
        self.switch_states = self.initial_switch_states.copy()
    
    def _update_switches(self, old_t, t):
        updated = False
        switch_equs = []
        for s in range(len(self.switch_info)):
            for e in self.switch_events[s]:
                if old_t < e and t >= e:
                    updated = True
                    self.switch_states[s] = not self.switch_states[s]
                if not self.switch_states[s]:
                    p, m, *_ = self.switch_info[s]
                elif len(self.switch_info[s]) == 3:
                    p, _, m = self.switch_info[s]
                else:
                    continue
                equ = np.zeros(self.nodes)
                equ[p] = 1
                equ[m] = -1
                switch_equs.append(equ)
        if updated:
            self.switch_equs = switch_equs
        return updated


    def _F(self, t, r):
        old_t = self.t
        if self._update_switches(old_t, t):
            self._update_super_nodes()

        self.t = t
        return self.A @ r + self.e
    
    def _prepare_for_nodal_analysis(self):
        self.SN = np.array(self.SN)
        self.T = np.array(self.T).T
        self.NA = self.Y.copy()
        for i, eq in enumerate(self.NA):
            eq[i] = np.sum(eq)
    
    def _update_super_nodes(self):
        self.check_state("analyzing")
        if len(self.switch_equs) != 0:
            self.SNsw = np.concatenate((self.SN, self.switch_equs))
        else:
            self.SNsw = self.SN.copy()
        # len(SNsw) = #VSs
        # len(T.T)  = #CSs
        V = len(self.SNsw)
        I = len(self.T.T)
        Rv = len(self.C)
        Ri = len(self.L)

        # Find super nodes
        super_nodes = [{x} for x in range(self.nodes)]
        non_base = set()
        for vs in self.SNsw:
            i, j = np.argwhere(vs)[:, 0]
            i, j = (i, j) if i < j else (j, i)
            super_nodes[i].update(super_nodes[j])
            super_nodes[j] = super_nodes[i]
            non_base.add(j)
        super_nodes = np.array([
            [1 if n in super_nodes[j] else 0 for n in range(self.nodes)]
            for j in range(self.nodes)
            if j not in non_base
        ])
        self.super_nodes = super_nodes

        # Calculate G
        self.G = np.zeros((V, self.nodes))
        for i, n in enumerate(self.G):
            plus = np.argwhere(self.SNsw[i] == 1)[0, 0]
            checked_vss = {i}
            n[plus] = 1
            queue = [plus]
            while len(queue) != 0:
                node = queue.pop(0)
                vss = (vs for vs in np.argwhere(self.SNsw[:, node])[:, 0] if vs not in checked_vss)
                for vs in vss:
                    head, tail = np.argwhere(self.SNsw[vs])[:, 0]
                    node = head if head != node else tail
                    checked_vss.add(vs)
                    n[node] = 1
                    queue.append(node)
        
        NAprime = (self.super_nodes @ self.NA)[:-1]
        Tprime = (self.super_nodes @ self.T)[:-1]
        gnd_equ = np.zeros((1, self.nodes))
        gnd_equ[0, self.ground] = 1
        D = np.concatenate((self.SNsw, NAprime, gnd_equ))
        D_inv = np.linalg.inv(D)
        
        temp1 = np.zeros((self.nodes, V + I))
        temp1[:V, :V] = np.identity(V)
        temp1[-2, -I:] = Tprime
        temp1[-1, -1] = 0

        temp3 = np.zeros((Rv, Rv))
        temp4 = np.zeros((Ri, Ri))
        np.fill_diagonal(temp3, self.C)
        np.fill_diagonal(temp4, self.L)
        temp5 = np.zeros((Rv + Ri, V + I))
        r_to_y = np.zeros((V + I, Rv + Ri))
        temp5[:Rv, :Rv] = temp3
        temp5[-Ri:, -Ri:] = temp4
        r_to_y[:Rv, :Rv] = np.identity(Rv)
        r_to_y[-Ri:, -Ri:] = np.identity(Ri)
        
        temp6 = np.zeros((V + I, V))
        np.fill_diagonal(temp6, 1)
        temp7 = np.concatenate((np.zeros((V, I)), np.identity(I)))
        temp8 = np.concatenate((np.zeros((I, V)), np.identity(I)), axis=1)

        sources = np.array(self.v + self.i)

        A = temp5 @ (temp6 @ (self.G @ self.NA @ D_inv @ temp1 + self.G @ self.T @ temp8) + temp7 @ self.T.T @ D_inv @ temp1)
        e = A @ sources
        A = A @ r_to_y

        self.SNsw += np.array(self.dep_coeffs + [[0] * self.nodes] * len(self.switch_equs))
        self.A = A
        self.e = e
        self.r_to_v = D_inv @ temp1 @ r_to_y

    def solve(self, t_range, r0=None):
        self.state = "analyzing"
        self._prepare_for_nodal_analysis()
        self.reset_switch_states()
        self._update_switches(t_range[0], t_range[0])
        self._update_super_nodes()

        if r0 is None:
            r0 = np.zeros(len(self.C) + len(self.L))
        sol = solve_ivp(self._F, t_range, r0)
        ts = sol.t
        rs = sol.y
        vs = self.r_to_v @ rs
        return ts, rs, vs
