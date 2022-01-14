from tape import ClauseTape

connectives = ['/\\', '\\/', '->', '~']

class Sequent:
    left_tapes: list[ClauseTape]
    right_tapes: list[ClauseTape]
    chlidren: list
    parent: object
    is_calculated: bool
    level: int
    level_idx: int
    size: int
    space_before: int

    def __init__(self, left_tapes=[], right_tapes=[], level=1, level_idx=1) -> None:
        self.left_tapes = left_tapes
        self.right_tapes = right_tapes
        self.children = []
        self.is_calculated = False
        self.parent = None
        self.level = level
        self.level_idx = level_idx
        self.space_before = 0
        self.size = 0

    def __str__(self) -> None:
        left = ", ".join([str(t) for t in self.left_tapes])
        right = ", ".join([str(t) for t in self.right_tapes])
        return f"{left} => {right}"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def init_by_formula(cls, formula) -> None:
        tape = ClauseTape.init_by_formula(formula, connectives)
        return cls(right_tapes=[tape])

    def calculate(self) -> bool:
        self.is_calculated = True
        left_atomics, left_highway = self.get_atomics_and_highway(self.left_tapes)
        right_atomics, right_highway = self.get_atomics_and_highway(self.right_tapes)
        common_atomics = left_atomics.intersection(right_atomics)
        if common_atomics:
            return True
        if left_highway < 0 and right_highway < 0:
            return False
        if left_highway >= 0:
            return self.operate_on_highway(True, left_highway)
        return self.operate_on_highway(False, right_highway)

    def operate_on_highway(self, is_left, highway):
        if is_left:
            if self.left_tapes[highway].connective == "~":
                return self.left_neg(highway)
            elif self.left_tapes[highway].connective == "/\\":
                return self.left_and(highway)
            elif self.left_tapes[highway].connective == "\\/":
                return self.left_or(highway)
            else:
                return self.left_imp(highway)
        if self.right_tapes[highway].connective == "~":
            return self.right_neg(highway)
        elif self.right_tapes[highway].connective == "/\\":
            return self.right_and(highway)
        elif self.right_tapes[highway].connective == "\\/":
            return self.right_or(highway)
        else:
            return self.right_imp(highway)

    def left_neg(self, highway) -> bool:
        tape1 = ClauseTape.init_by_formula(self.left_tapes[highway].subs[0], connectives)
        ltapes1 = [t for i, t in enumerate(self.left_tapes) if i != highway]
        rtapes1 = self.right_tapes.copy()
        rtapes1.append(tape1)
        child1 = Sequent(left_tapes=ltapes1, right_tapes=rtapes1, level=self.level+1, level_idx=self.level_idx)
        self.add_child(child1)
        return child1.calculate()

    def right_neg(self, highway) -> bool:
        tape1 = ClauseTape.init_by_formula(self.right_tapes[highway].subs[0], connectives)
        ltapes1 = self.left_tapes.copy()
        ltapes1.append(tape1)
        rtapes1 = [t for i, t in enumerate(self.right_tapes) if i != highway]
        child1 = Sequent(left_tapes=ltapes1, right_tapes=rtapes1, level=self.level+1, level_idx=self.level_idx)
        self.add_child(child1)
        return child1.calculate()

    def left_and(self, highway) -> bool:
        tape1 = ClauseTape.init_by_formula(self.left_tapes[highway].subs[0], connectives)
        tape2 = ClauseTape.init_by_formula(self.left_tapes[highway].subs[1], connectives)
        ltapes1 = [t for i, t in enumerate(self.left_tapes) if i != highway]
        ltapes1 += [tape1, tape2]
        rtapes1 = self.right_tapes.copy()
        child1 = Sequent(left_tapes=ltapes1, right_tapes=rtapes1, level=self.level+1, level_idx=self.level_idx)
        self.add_child(child1)
        return child1.calculate()

    def right_and(self, highway) -> bool:
        tape1 = ClauseTape.init_by_formula(self.right_tapes[highway].subs[0], connectives)
        tape2 = ClauseTape.init_by_formula(self.right_tapes[highway].subs[1], connectives)
        ltapes1 = self.left_tapes.copy()
        ltapes2 = self.left_tapes.copy()
        rtapes1 = [t for i, t in enumerate(self.right_tapes) if i != highway]
        rtapes2 = rtapes1.copy()
        rtapes1.append(tape1)
        rtapes2.append(tape2)
        child1 = Sequent(left_tapes=ltapes1, right_tapes=rtapes1, level=self.level+1, level_idx=self.level_idx)
        child2 = Sequent(left_tapes=ltapes2, right_tapes=rtapes2, level=self.level+1, level_idx=self.level_idx+1)
        self.add_child(child1)
        self.add_child(child2)
        return child1.calculate() and child2.calculate()

    def left_or(self, highway) -> bool:
        tape1 = ClauseTape.init_by_formula(self.left_tapes[highway].subs[0], connectives)
        tape2 = ClauseTape.init_by_formula(self.left_tapes[highway].subs[1], connectives)
        ltapes1 = [t for i, t in enumerate(self.left_tapes) if i != highway]
        ltapes2 = ltapes1.copy()
        ltapes1.append(tape1)
        ltapes2.append(tape2)
        rtapes1 = self.right_tapes.copy()
        rtapes2 = self.right_tapes.copy()
        child1 = Sequent(left_tapes=ltapes1, right_tapes=rtapes1, level=self.level+1, level_idx=self.level_idx)
        child2 = Sequent(left_tapes=ltapes2, right_tapes=rtapes2, level=self.level+1, level_idx=self.level_idx+1)
        self.add_child(child1)
        self.add_child(child2)
        return child1.calculate() and child2.calculate()

    def right_or(self, highway) -> bool:
        tape1 = ClauseTape.init_by_formula(self.right_tapes[highway].subs[0], connectives)
        tape2 = ClauseTape.init_by_formula(self.right_tapes[highway].subs[1], connectives)
        ltapes1 = self.left_tapes.copy()
        rtapes1 = [t for i, t in enumerate(self.right_tapes) if i != highway]
        rtapes1 += [tape1, tape2]
        child1 = Sequent(left_tapes=ltapes1, right_tapes=rtapes1, level=self.level+1, level_idx=self.level_idx)
        self.add_child(child1)
        return child1.calculate()

    def left_imp(self, highway) -> bool:
        tape1 = ClauseTape.init_by_formula(self.left_tapes[highway].subs[0], connectives)
        tape2 = ClauseTape.init_by_formula(self.left_tapes[highway].subs[1], connectives)
        ltapes1 = [t for i, t in enumerate(self.left_tapes) if i != highway]
        ltapes2 = ltapes1.copy()
        ltapes1.append(tape1)
        ltapes2.append(tape2)
        rtapes1 = self.right_tapes.copy()
        rtapes2 = self.right_tapes.copy()
        child1 = Sequent(left_tapes=ltapes1, right_tapes=rtapes1, level=self.level+1, level_idx=self.level_idx)
        child2 = Sequent(left_tapes=ltapes2, right_tapes=rtapes2, level=self.level+1, level_idx=self.level_idx+1)
        self.add_child(child1)
        self.add_child(child2)
        return child1.calculate() and child2.calculate()

    def right_imp(self, highway) -> bool:
        tape1 = ClauseTape.init_by_formula(self.right_tapes[highway].subs[0], connectives)
        tape2 = ClauseTape.init_by_formula(self.right_tapes[highway].subs[1], connectives)
        ltapes1 = self.left_tapes.copy()
        ltapes1.append(tape1)
        rtapes1 = [t for i, t in enumerate(self.right_tapes) if i != highway]
        rtapes1.append(tape2)
        child1 = Sequent(left_tapes=ltapes1, right_tapes=rtapes1, level=self.level+1, level_idx=self.level_idx)
        self.add_child(child1)
        return child1.calculate()

    def cal_size(self):
        if not self.children:
            self.size = 1
            return 1
        s = 0
        for ch in self.children:
            s += ch.cal_size()
        self.size = s
        return s

    def cal_children_space_before(self):
        s = 0
        for ch in self.children:
            ch.space_before = self.space_before + s 
            s += ch.size
            ch.cal_children_space_before()

    def cal_max_length(self):
        ml = len(str(self))
        for ch in self.children:
            l = ch.cal_max_length()
            if l > ml:
                ml = l 
        return ml
    
    def add_child(self, child) -> None:
        self.children.append(child)
        child.parent = self

    def get_level(self) -> int:
        lv = 0
        p = self.parent
        while p:
            lv += 1
            p = p.parent
        return lv

    def print_tree(self) -> None:
        spaces = " " * self.get_level() * 3
        prefix = spaces + "=>"  if self.parent else ""
        print(prefix + self.left_tapes)
        for child in self.children:
            child.print_tree()

    @staticmethod
    def get_atomics_and_highway(tapes):
        highway = -1
        atomics = set()
        for idx, tape in enumerate(tapes):
            if tape.is_atomic:
                atomics.add(tape.subs[0])
            else:
                highway = idx
        return atomics, highway