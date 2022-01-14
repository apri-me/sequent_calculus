class ClauseTape:
    connective: str
    subs: list[str]
    is_atomic: bool

    def __init__(self, subs: list[str], connective: str, is_atomic=False) -> None:
        self.subs = subs
        self.connective = connective
        self.is_atomic = is_atomic

    def __str__(self) -> str:
        if self.is_atomic:
            return self.subs[0]
        if len(self.subs) == 1:
            return f"{self.connective} {self.subs[0]}"
        else:
            return f"{self.subs[0]} {self.connective} {self.subs[1]}"

    def __repr__(self) -> str:
        return self.__str__()
    
    @classmethod
    def init_by_formula(cls, formula, connectives):
        formula1 = formula.strip()
        if formula1.startswith("(") and formula1.endswith(")"):
            formula1 = formula1[1:-1].strip()
        subs_and_cons = cls.extract_highest_order_schemes_and_connectives(formula1)
        cons = cls.extr_tape_connectives(subs_and_cons, connectives)
        if len(cons) > 1 or (len(cons) == 0 and len(subs_and_cons) != 1):
            raise Exception(f"not well-formed! {len(cons)}")
        if not cons:
            return cls(subs_and_cons, "", is_atomic=True)
        con = cons[0]
        subs_and_cons.remove(con)
        return cls(subs_and_cons, con)

    # NOTE: For a given formula, it just checks whether the number of right parens are equal to left parens.
    @staticmethod
    def check_equality_of_paranthesis(formula):
        l = formula.count("(")
        r = formula.count(")")
        if l != r:
            raise NotEqualParanthesisException(
                f"The number of right and left paranthesis are not equal: {l} != {r}")

    # NOTE: For a given string, it returns the index of outer paranthesis.
    # e.g: "(A \and (B)) \or (C \and D)" -> [(0, 11), (17, 26)]
    @staticmethod
    def find_parens(s):
        matchings = []
        pstack = []
        for i, c in enumerate(s):
            if c == '(':
                pstack.append(i)
            elif c == ')':
                if len(pstack) == 0:
                    print(s)
                    raise IndexError("No matching closing parens at: " + str(i))
                elif len(pstack) == 1:
                    matchings.append((pstack.pop(), i))
                else:
                    pstack.pop()
        return matchings

    # NOTE: For a given formula it returns highest order schemes and connnectives.
    # By highest order schemes we mean the schemes that aree in the outer paranthesis.
    # e.g: in "(A \and (B \and C)) \or D", "(A \and (B \and C))" and "D" are highest order schemes but "(B \and C)" isn't.
    # If the above example is given to function it returns -> ["(A \and (B \and C))", "\or", "D"]
    @staticmethod
    def extract_highest_order_schemes_and_connectives(formula: str):
        tape = []
        subschemes_idx = ClauseTape.find_parens(formula)
        if subschemes_idx:
            s = formula[:subschemes_idx[0][0]].strip()
            if s:
                tape += s.split()
            for i, (start_idx, end_idx) in enumerate(subschemes_idx):
                tape.append(formula[start_idx: end_idx+1].strip())
                if i < len(subschemes_idx) - 1:
                    tape.append(formula[end_idx+1: subschemes_idx[i+1][0]].strip())
                else:
                    s = formula[end_idx+1:].strip()
                    if s:
                        tape += s.split()
        else:
            tape += formula.strip().split()
        return tape


    # NOTE: Gets a tape(highest order schemes and connectives) and returns just its connectives.
    @staticmethod
    def extr_tape_connectives(tape: list, connectives) -> list:
        return [s for s in tape if s in connectives]


class NotEqualParanthesisException(Exception):
    pass
