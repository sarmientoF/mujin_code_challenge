# %%
lines = """4 8 4 6
.......#
..#....#
.###...#
.....###
G=ub(B)
B=ub(m)lib(l)(m)
H=ib()(mmHllmll)
I=III
1 1 w
G
1 1 e
G
2 2 n
G
4 1 s
ib(lib()(mmm))(mmmm)
1 1 e
H 
2 2 s
I
"""
lines = lines.splitlines()

# %%
import numpy as np
from dataclasses import dataclass, field
from enum import Enum

# %%
r, c, p, q = [int(c) for c in lines[0].split(" ")]
r, c, p, q

# %%
map = np.full((r + 2, c + 2), True, dtype=bool)
map[1 : r + 1, 1 : c + 1] = [[c == "#" for c in [*line]] for line in lines[1 : r + 1]]

# %%
procedures: dict[str, list] = dict()
for line in lines[r + 1 : r + 1 + p]:
    name, program = line.split("=")
    procedures[name] = [*program]
procedures


# %%
class Direction(Enum):
    n = (-1, 0)
    w = (0, -1)
    s = (+1, 0)
    e = (0, +1)


left_mapping = {
    Direction.n: Direction.w,
    Direction.w: Direction.s,
    Direction.s: Direction.e,
    Direction.e: Direction.n,
}


@dataclass
class Robot:
    x: int
    y: int
    d: Direction
    map: np.array = field(repr=False)
    b: bool = field(init=False)

    def __post_init__(self):
        self.checkBlock()

    def m(self):
        dx, dy = self.d.value
        self.x += dx
        self.y += dy
        self.checkBlock()

    def l(self):
        self.d = left_mapping[self.d]
        self.checkBlock()

    def condition(self, c):
        if c == "b":
            return self.b
        return self.d == Direction[c]

    def checkBlock(self) -> bool:
        dx, dy = self.d.value
        x = self.x + dx
        y = self.y + dy
        self.b = self.map[x, y]


# %%


def closingParenthesis(program):
    i = 0
    for j, _c in enumerate(program):
        if _c == "(":
            i += 1
        if _c == ")":
            i -= 1
        if i == 0:
            return program[1:j], program[j + 1 :]


def runProgram(program: list):
    if not program:
        return
    program = program.copy()

    l = program.pop(0)
    if l == "i":
        c = program.pop(0)
        yes, rest = closingParenthesis(program)
        no, program = closingParenthesis(rest)
        runProgram(yes if robot.condition(c) else no)
    if l == "u":
        c = program.pop(0)
        yes, program = closingParenthesis(program)
        while not robot.condition(c):
            runProgram(yes)
    if l in ["m", "l"]:
        robot.l() if l == "l" else robot.m()
    if l in procedures:
        program = [*procedures[l], *program]
    runProgram(program)


for i in range(q):
    x0, y0, d0 = lines[1 + r + p + 2 * i].split(" ")
    procedureCall = lines[1 + r + p + 2 * i + 1]

    program = (
        procedures[procedureCall].copy()
        if procedureCall in procedures
        else [*procedureCall]
    )
    robot = Robot(int(x0), int(y0), Direction[d0], map)
    try:
        runProgram(program)
        print(robot)
    except:
        print("inf")
