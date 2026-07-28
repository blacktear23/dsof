import copy
import math
import heapq
import itertools
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class VM:
    name: str
    vcpu: int
    mem: int
    numa_mem: Dict[int, int]
    current_socket: Optional[int] = None

    def get_move_mem(self, tgt: int):
        ret = 0
        for sock, mem in self.numa_mem.items():
            if sock != tgt:
                ret += mem
        return ret


class Op:
    pass

    
@dataclass
class Move(Op):
    vm_name: str
    vm: VM 
    src: int
    dst: int


@dataclass
class Assign(Op):
    vm_name: str
    vm: VM
    dst: int


@dataclass
class State:
    placement: Dict[str, Optional[int]]
    socket_vms: Dict[int, int]
    socket_cpu: Dict[int, int]
    socket_mem: Dict[int, int]
    socket_total_mem: Dict[int, int]
    history: List[Op] = field(default_factory=list)
    moved_mem: int = 0
    touched_vm: List[str] = field(default_factory=list)

    def can_place(self, vm: VM, socket: int):
        return (
            self.socket_total_mem[socket]
            - self.socket_mem[socket]
            >= vm.mem
        )

    def key(self):
        return tuple(sorted(self.placement.items()))


class Planner(object):
    def __init__(self, vms):
        self.vm_list = vms
        self.vms = {v.name: v for v in vms}
        self.generates = 0
        self.propose_prun_assign = 0
        self.propose_prun_move = 0
        self.memo_prun = 0
        self.beam_prun = 0
        self.iters = 0
        self.metrics = []
        self.first_best_found_iter = 0
        self.current_rule_prun = 0

    def prune_ratio(self):
        gens = self.generates
        pruns = (self.propose_prun_assign + self.propose_prun_move + self.memo_prun + self.beam_prun)
        return float(pruns) / float(gens)

    def prune_ratios(self):
        gens = self.generates
        rule = self.propose_prun_move + self.propose_prun_assign
        memo = self.memo_prun
        beam = self.beam_prun
        return (float(rule) / float(gens), 
            float(memo) / float(gens),
            float(beam) / float(gens),
            float(rule + memo + beam) / float(gens),
        )

    def cpu_imbalance(self, state: State):
        return abs(state.socket_cpu[0] - state.socket_cpu[1])

    def mem_imbalance(self, state: State):
        return abs(state.socket_mem[0] - state.socket_mem[1])

    def score(self, state: State):
        return (
            self.cpu_imbalance(state),  # Target
            self.mem_imbalance(state),  # Target
            state.moved_mem,            # Cost
        )

    def is_complete(self, state: State):
        for vm in self.vm_list:
            if state.placement.get(vm.name) is None:
                for sock in state.socket_cpu.keys():
                    if state.can_place(vm, sock):
                        return False
        return True
        
    def goal(self, state: State):
        if not self.is_complete(state):
            return False

        if abs(state.socket_cpu[0] - state.socket_cpu[1]) <= 2:
            return True

        if abs(state.socket_vms[0] - state.socket_vms[1]) <= 2:
            return True

        return False

    def propose(self, state: State):
        ops = []
        complete = self.is_complete(state)
        for vm in self.vm_list:
            loc = state.placement.get(vm.name, None)
            if loc is None:
                for dst in state.socket_cpu.keys():
                    self.generates += 1
                    if vm.name in state.touched_vm:
                        self.current_rule_prun += 1
                        self.propose_prun_assign += 1
                        continue
                        
                    if state.can_place(vm, dst):
                        ops.append(
                            Assign(vm.name, vm, dst)
                        )
                    else:
                        self.current_rule_prun += 1
                        self.propose_prun_assign += 1
            elif complete:
                for dst in state.socket_cpu.keys():
                    self.generates += 1
                    if vm.name in state.touched_vm:
                        self.current_rule_prun += 1
                        self.propose_prun_move += 1
                        continue

                    if dst != loc:
                        if state.can_place(vm, dst):
                            ops.append(
                                Move(vm.name, vm, loc, dst)
                            )
                        else:
                            self.current_rule_prun += 1
                            self.propose_prun_move += 1
                    else:
                        self.current_rule_prun += 1
                        self.propose_prun_move += 1
        return ops

    def apply(self, state: State, op: Op):
        s = copy.deepcopy(state)

        if isinstance(op, Assign):
            vm = op.vm
            s.placement[vm.name] = op.dst
            s.socket_vms[op.dst] += 1
            s.socket_cpu[op.dst] += vm.vcpu
            s.socket_mem[op.dst] += vm.mem
            s.moved_mem += vm.get_move_mem(op.dst)
        elif isinstance(op, Move):
            vm = op.vm
            s.placement[vm.name] = op.dst
            s.socket_cpu[op.src] -= vm.vcpu
            s.socket_cpu[op.dst] += vm.vcpu
            s.socket_mem[op.src] -= vm.mem
            s.socket_mem[op.dst] += vm.mem
            s.socket_vms[op.src] -= 1
            s.socket_vms[op.dst] += 1
            s.moved_mem += vm.get_move_mem(op.dst)
        
        s.touched_vm.append(op.vm_name)
        s.history.append(op)
        return s

    def solve(self, initial: State):
        frontier = []
        visited = {}
        counter = itertools.count()
        heapq.heappush(frontier, (
            self.score(initial),
            next(counter),
            initial,
        ))

        best = None
        found = 0
        max_found = 1000
        # beam_width = 1
        beam_width = 32
        # beam_width = 8
        # beam_width = len(self.vms)
        while frontier:
            self.iters += 1
            _, _, state = heapq.heappop(frontier)
            if self.goal(state):
                found += 1
                if best is None or self.score(state) < self.score(best):
                    if best is not None:
                        print(f"Found Best state = {self.score(state)}, best = {self.score(best)}")
                    else:
                        self.first_best_found_iter = self.iters
                        print(f"Found first Best {self.score(state)}")
                    best = state
                if best is not None and self.score(state) > self.score(best):
                    print(f"Score bigger than best {self.score(state)} > {self.score(best)}, return")
                    return best
                if found > max_found:
                    return best

            frontier_b = frontier[:]
            memo_prune = 0
            self.current_rule_prun = 0
            for op in self.propose(state):
                new_state = self.apply(state, op)
                key = new_state.key()
                score = self.score(new_state)
                node = (score, next(counter), new_state)
                heapq.heappush(frontier_b, node)
                if key in visited and visited[key] <= score:
                    self.memo_prun += 1
                    memo_prune += 1
                    continue

                if self.is_complete(state) and self.is_complete(new_state) and score > self.score(state):
                    self.memo_prun += 1
                    memo_prune += 1
                    continue

                visited[key] = score
                heapq.heappush(frontier, node)
            
            if beam_width is not None:
                self.beam_prun += max(0, len(frontier) - beam_width)
                frontier_a = heapq.nsmallest(len(frontier), frontier)
                frontier_b = heapq.nsmallest(len(frontier_b), frontier_b)
                djs = js_divergence(frontier_a, frontier_b)
                jaccard = jaccard_simi(frontier_a, frontier_b)
                # print(f"Iter {self.iters} JS Divergence Beam = {beam_width}, Memo Prune = {memo_prune + self.current_rule_prun}, Found = {found}, Frontier = {len(frontier)} With Memo vs Without Memo:", djs, jaccard)
                self.metrics.append((self.iters, memo_prune, djs, jaccard))
                frontier = heapq.nsmallest(beam_width, frontier)
                heapq.heapify(frontier)
        return best


def jaccard_simi(P, Q):
    states_a = set(state_key(s) for _, _, s in P)
    states_b = set(state_key(s) for _, _, s in Q)
    return len(states_a & states_b) / len(states_a | states_b)


def state_key(state: State):
    return tuple(sorted(state.placement.items()))


def kl_divergence(P, Q, eps=1e-12):
    ret = 0
    for p, q in zip(P, Q):
        if p == 0:
            continue
        ret += p * math.log2(
            p / max(q, eps)
        )
    return ret


def merge_distribution(P, Q):
    keys = set(P) | set(Q)
    p = []
    q = []
    for k in keys:
        p.append(P.get(k, 0.0))
        q.append(Q.get(k, 0.0))
    return p, q


def js_divergence(frontier_a, frontier_b):
    PA = frontier_distribution(frontier_a)
    PB = frontier_distribution(frontier_b)
    P, Q = merge_distribution(PA, PB)
    M = [(p + q) / 2 for p, q in zip(P, Q)]

    return (
        kl_divergence(P, M)
        +
        kl_divergence(Q, M)
    ) / 2


def frontier_distribution(frontier, temp=3.0):
    return calculate_frontier_entropy(frontier, temp)[1]


def calculate_frontier_entropy(frontier, temp=3.0):
    weights = {}
    pweights = []
    for rank, (_, _, state) in enumerate(frontier):
        w = math.exp(-rank / temp)
        weights[state_key(state)] = w
        pweights.append(w)

    s = sum(pweights)
    probs = [w / s for w in pweights]
    h = 0.0
    for p in probs:
        if p > 0:
            h -= p * math.log2(p)
    for k in weights:
        weights[k] /= s
    return h, weights


def calculate_state_decision_entropy(vms: Dict[str, VM], state: State, sockets: int = 2):
    ret = 0
    for vm_name in vms:
        assigned = state.placement.get(vm_name, None) is not None
        if assigned:
            ret += math.log2(sockets-1)
        else:
            ret += math.log2(sockets)
    return ret


def build_state_from_vms(vms: List[VM], total_mem: Dict[int, int]):
    state = State(placement={}, socket_cpu={}, socket_vms={}, socket_mem={}, socket_total_mem=total_mem)
    for key in total_mem.keys():
        state.socket_vms[key] = 0
        state.socket_cpu[key] = 0
        state.socket_mem[key] = 0

    for vm in vms:
        if vm.current_socket is not None:
            sock = vm.current_socket
            state.placement[vm.name] = sock
            state.socket_vms[sock] += 1
            state.socket_cpu[sock] += vm.vcpu
            state.socket_mem[sock] += vm.mem
    print(state)
    return state
        

def decision_entropy(vms: List[VM], sockets: int):
    ret = 0
    for vm in vms:
        if vm.current_socket is None:
            ret += math.log2(sockets)
        else:
            ret += math.log2(sockets-1)
    return ret


def test():
    vms = [
        VM("A", 16, 16, {0: 16, 1: 0}, 0),  # 0
        VM("B", 16, 16, {0: 0, 1: 16}, 1),  # 1
        VM("C", 16, 16, {0: 16, 1: 0}, 0),  # 0
        VM("D", 16, 16, {0: 7, 1: 9}, None),
        VM("E", 16, 16, {0: 2, 1: 14}, None),
        VM("F", 16, 16, {0: 0, 1: 16}, None),
        VM("G", 16, 8, {0: 1, 1: 7}, None),
        VM("H", 8, 8, {0: 1, 1: 7}, 1),
        VM("I", 8, 8, {0: 7, 1: 1}, 0),
        VM("I1", 8, 8, {0: 7, 1: 1}, None),
        VM("I2", 8, 8, {0: 7, 1: 1}, None),
        VM("I3", 8, 8, {0: 7, 1: 1}, None),
        VM("I4", 8, 8, {0: 7, 1: 1}, None),
        VM("I5", 8, 8, {0: 7, 1: 1}, None),
        VM("I6", 8, 8, {0: 7, 1: 1}, None),
        VM("I7", 8, 8, {0: 7, 1: 1}, None),
        VM("I8", 8, 8, {0: 7, 1: 1}, None),
        VM("I9", 8, 8, {0: 7, 1: 1}, None),
        VM("I10", 8, 8, {0: 7, 1: 1}, None),
        VM("I11", 8, 8, {0: 7, 1: 1}, None), 
        VM("J1", 8, 8, {0: 7, 1: 1}, None),
        VM("J2", 8, 8, {0: 7, 1: 1}, None),
        VM("J3", 8, 8, {0: 7, 1: 1}, None),
        VM("J4", 8, 8, {0: 7, 1: 1}, None),
        VM("J5", 8, 8, {0: 7, 1: 1}, None),
        VM("J6", 8, 8, {0: 7, 1: 1}, None),
        VM("J7", 8, 8, {0: 7, 1: 1}, None),
        VM("J8", 8, 8, {0: 7, 1: 1}, None),
        VM("J9", 8, 8, {0: 7, 1: 1}, None),
        VM("J10", 8, 8, {0: 7, 1: 1}, None),
        VM("J11", 8, 8, {0: 7, 1: 1}, None),
    ]
    vms1_e = decision_entropy(vms, 2)

    vms2 = [
        VM("A", 16, 16, {0: 16, 1: 0}, 0),  # 0
        VM("B", 16, 16, {0: 0, 1: 16}, 1),  # 1
        VM("C", 16, 16, {0: 16, 1: 0}, 0),  # 0
        VM("D", 16, 16, {0: 7, 1: 9}, None),
        VM("E", 16, 16, {0: 2, 1: 14}, None),
        VM("F", 16, 16, {0: 0, 1: 16}, None),
        VM("G", 16, 8, {0: 1, 1: 7}, None),
        VM("H", 8, 8, {0: 1, 1: 7}, 1),
        VM("I", 8, 8, {0: 7, 1: 1}, 0),
        VM("I1", 8, 8, {0: 7, 1: 1}, 0),
        VM("I2", 8, 8, {0: 7, 1: 1}, 0),
        VM("I3", 8, 8, {0: 7, 1: 1}, 1),
        VM("I4", 8, 8, {0: 7, 1: 1}, 1),
        VM("I5", 8, 8, {0: 7, 1: 1}, 0),
        VM("I6", 8, 8, {0: 7, 1: 1}, 1),
        VM("I7", 8, 8, {0: 7, 1: 1}, 0),
        VM("I8", 8, 8, {0: 7, 1: 1}, 0),
        VM("I9", 8, 8, {0: 7, 1: 1}, 0),
        VM("I10", 8, 8, {0: 7, 1: 1}, 0),
        VM("I11", 8, 8, {0: 7, 1: 1}, 1), 
        VM("J1", 8, 8, {0: 7, 1: 1}, 1),
        VM("J2", 8, 8, {0: 7, 1: 1}, 1),
        VM("J3", 8, 8, {0: 7, 1: 1}, 1),
        VM("J4", 8, 8, {0: 7, 1: 1}, 0),
        VM("J5", 8, 8, {0: 7, 1: 1}, 1),
        VM("J6", 8, 8, {0: 7, 1: 1}, 0),
        VM("J7", 8, 8, {0: 7, 1: 1}, 0),
        VM("J8", 8, 8, {0: 7, 1: 1}, 0),
        VM("J9", 8, 8, {0: 7, 1: 1}, 0),
        VM("J10", 8, 8, {0: 7, 1: 1}, 0),
        VM("J11", 8, 8, {0: 7, 1: 1}, 0),
    ]
    vms2_e = decision_entropy(vms2, 2)

    state = build_state_from_vms(vms, {0: 512, 1: 512})

    planner = Planner(vms)
    best = planner.solve(state)
    vms1_pr = planner.prune_ratios()
    print("VMs:", best.socket_vms)
    print("CPU:", best.socket_cpu)
    print("MEM:", best.socket_mem)
    print("Moved:", best.moved_mem)

    print("Generates:     ", planner.generates)
    print("Propose Prune: ", "Assign: ", planner.propose_prun_assign, "Move: ", planner.propose_prun_move)
    print("Memo Prune:    ", planner.memo_prun)
    print("Beam Prune:    ", planner.beam_prun)
    print("Prune Ratio:   ", planner.prune_ratio())
    print()
    for op in sorted(best.history, key=lambda x: x.vm_name):
        print(op)
    print(len(best.history))

    state = build_state_from_vms(vms2, {0: 512, 1: 512})
    planner2 = Planner(vms2)
    best = planner2.solve(state)
    vms2_pr = planner2.prune_ratios()
    print("VMs:", best.socket_vms)
    print("CPU:", best.socket_cpu)
    print("MEM:", best.socket_mem)
    print("Moved:", best.moved_mem)

    print("Generates:     ", planner2.generates)
    print("Propose Prune: ", "Assign: ", planner.propose_prun_assign, "Move: ", planner2.propose_prun_move)
    print("Memo Prune:    ", planner2.memo_prun)
    print("Beam Prune:    ", planner2.beam_prun)
    print("Prune Ratio:   ", planner2.prune_ratio())
    print()
    for op in sorted(best.history, key=lambda x: x.vm_name):
        print(op)
    print(len(best.history))

    print()
    print(vms1_e, vms1_pr)
    print(vms2_e, vms2_pr)

    draw_plot(planner.metrics, planner.first_best_found_iter)

    
def draw_plot(data, first_best_iter):
    import matplotlib.pyplot as plt
    import numpy as np
    iters = []
    prunes = []
    jaccards = []
    d_js = []
    for (i, p, djs, jaccard) in data:
        iters.append(i)
        prunes.append(p)
        d_js.append(djs)
        jaccards.append(jaccard)

    plt.figure(figsize=(12, 6), dpi=120)
    scatter = plt.scatter(d_js, jaccards, c=prunes, s=15,
                          cmap='turbo', alpha=0.6, edgecolors='none')
    cbar = plt.colorbar(scatter)
    cbar.set_label('Prunes', fontsize=11)

    plt.xlabel('Djs')
    plt.ylabel('Jaccard')
    plt.title('Search Dynamics: Jaccard x JS Divergence')

    # 刻度精细化：重点展示 0 ~ 0.1 之间的细密变化
    plt.ylim(-0.001, 1.1)
    plt.grid(True, linestyle='--', alpha=0.4)

    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()
    
if __name__ == '__main__':
    test()