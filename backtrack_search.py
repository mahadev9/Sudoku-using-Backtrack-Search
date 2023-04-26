import queue
import copy
import functools
from flask import Flask, render_template, request
from sudoku_constraints import *

app = Flask(__name__)

class Sudoku:
    def __init__(self, puzzle, constraints):
        self.puzzle = puzzle
        self.size = len(self.puzzle)
        self.constraints = constraints
        self.domains, self.cell_names, self.pruned, self.prefilled_cell_names = \
            self.get_domain_cellname_pruned()
        self.neighbors = self.get_neighbors()
        self.assignments = []

    def get_domain_cellname_pruned(self):
        domain = {}
        cell_name = []
        pruned = {}
        prefilled_cell_names = {}
        for row, horizontal in enumerate(self.puzzle):
            for col, vertical in enumerate(horizontal):
                index = 'C{}{}'.format(row+1, col+1)
                cell_name.append(index)
                pruned[index] = []
                if vertical:
                    domain[index] = [vertical]
                    pruned[index] = [vertical]
                    prefilled_cell_names[index] = [vertical]
                else:
                    domain[index] = list(range(1, self.size+1))
        return domain, cell_name, pruned, prefilled_cell_names
    
    def get_neighbors(self):
        neighbor = {}
        for d in self.domains:
            neighbor[d] = []
            for constraint in self.constraints:
                if constraint[0] == d:
                    neighbor[d].append(constraint[1])
        return neighbor
    
    def goal_test(self, final_puzzle):
        for cn in self.cell_names:
            for neighbor in self.neighbors[cn]:
                if final_puzzle[cn] == final_puzzle[neighbor]:
                    return False
        return True

def revise(csp, Xi, Xj):
    revised = False
    for di in csp.domains[Xi]:
        if not any([di, dj] in csp.constraints[(Xi, Xj)] for dj in csp.domains[Xj]):
            csp.domains[Xi].remove(di)
            revised = True
    return revised

def AC3(csp):
    qStates = queue.Queue()
    for key in csp.constraints.keys():
        qStates.put(key)
    while not qStates.empty():
        (Xi, Xj) = qStates.get()
        if revise(csp, Xi, Xj):
            if len(csp.domains[Xi]) == 0:
                return False
            # Given Binary Constraints covers all the domains and constraints for the 9x9 sudoku
            # for Xk in csp.neighbors[Xi]:
            #     if Xk != Xi:
            #         qStates.put((Xk, Xi))
    return True

def minimum_remaining_values(csp, assignment):
    least_value_cell = None
    len_least_value_cell = 99
    for cell_name in csp.cell_names:
        if cell_name not in assignment and len_least_value_cell > len(csp.domains[cell_name]):
            least_value_cell = cell_name
            len_least_value_cell = len(csp.domains[cell_name])
    return least_value_cell

def order_domain_values(csp, assignment, cell_name):
    return csp.domains[cell_name]

def is_consistent(csp, assignment, cell_name, value):
    consistent = True
    for assigned_cell, assigned_value in assignment.items():
        if assigned_value == value and assigned_cell in csp.neighbors[cell_name]:
            consistent = False
    return consistent

def inference(csp, assignment, cell_name, value):
    return True

def assign(csp, assignment, cell_name, value):
    assignment[cell_name] = value
    if csp.domains:
        for neighbor in csp.neighbors[cell_name]:
            if neighbor not in assignment:
                if value in csp.domains[neighbor]:
                    csp.domains[neighbor].remove(value)
                    csp.pruned[cell_name].append((neighbor, value))

def unassign(csp, assignment, cell_name, value):
    if cell_name in assignment:
        for (location, value) in csp.pruned[cell_name]:
            csp.domains[location].append(value)
        csp.pruned[cell_name] = []
        del assignment[cell_name]

def backtracking(csp, assignment):
    csp.assignments.append(copy.deepcopy(assignment))
    if len(assignment) == csp.size**2:
        return assignment
    cell_name = minimum_remaining_values(csp, assignment)
    for value in order_domain_values(csp, assignment, cell_name):
        if is_consistent(csp, assignment, cell_name, value):
            assign(csp, assignment, cell_name, value)
            if inference(csp, assignment, cell_name, value):
                result = backtracking(csp, assignment)
                if result:
                    return result
            unassign(csp, assignment, cell_name, value)
    return None

def backtracking_search(csp):
    return backtracking(csp, {})

puzzle1 = [[7, None, None, 4, None, None, None, 8, 6],
            [None, 5, 1, None, 8, None, 4, None, None],
            [None, 4, None, 3, None, 7, None, 9, None],
            [3, None, 9, None, None, 6, 1, None, None],
            [None, None, None, None, 2, None, None, None, None],
            [None, None, 4, 9, None, None, 7, None, 8],
            [None, 8, None, 1, None, 2, None, 6, None],
            [None, None, 6, None, 5, None, 9, 1, None],
            [2, 1, None, None, None, 3, None, None, 5]]

puzzle2 = [[1, None, None, 2, None, 3, 8, None, None],
            [None, 8, 2, None, 6, None, 1, None, None],
            [7, None, None, None, None, 1, 6, 4, None],
            [3, None, None, None, 9, 5, None, 2, None],
            [None, 7, None, None, None, None, None, 1, None],
            [None, 9, None, 3, 1, None, None, None, 6],
            [None, 5, 3, 6, None, None, None, None, 1,],
            [None, None, 7, None, 2, None, 3, 9, None],
            [None, None, 4, 1, None, 9, None, None, 5]]

puzzle3 = [[1, None, None, 8, 4, None, None, 5, None],
            [5, None, None, 9, None, None, 8, None, 3],
            [7, None, None, None, 6, None, 1, None, None],
            [None, 1, None, 5, None, 2, None, 3, None],
            [None, 7, 5, None, None, None, 2, 6, None],
            [None, 3, None, 6, None, 9, None, 4, None],
            [None, None, 7, None, 5, None, None, None, 6],
            [4, None, 1, None, None, 6, None, None, 7],
            [None, 6, None, None, 9, 4, None, None, 2]]

puzzle4 = [[None, None, None, None, 9, None, None, 7, 5],
            [None, None, 1, 2, None, None, None, None, None],
            [None, 7, None, None, None, None, 1, 8, None],
            [3, None, None, 6, None, None, 9, None, None],
            [1, None, None, None, 5, None, None, None, 4],
            [None, None, 6, None, None, 2, None, None, 3],
            [None, 3, 2, None, None, None, None, 4, None],
            [None, None, None, None, None, 6, 5, None, None],
            [7, 9, None, None, 1, None, None, None, None]]

puzzle5 = [[None, None, None, None, None, 6, None, 8, None],
            [3, None, None, None, None, 2, 7, None, None],
            [7, None, 5, 1, None, None, 6, None, None],
            [None, None, 9, 4, None, None, None, None, None],
            [None, 8, None, None, 9, None, None, 2, None],
            [None, None, None, None, None, 8, 3, None, None],
            [None, None, 4, None, None, 7, 8, None, 5],
            [None, None, 2, 8, None, None, None, None, 6],
            [None, 5, None, 9, None, None, None, None, None]]

puzzle6 = [[1, None, None, None],
            [None, 2, None, None],
            [None, None, 3, None],
            [None, None, None, 4]]

customPuzzle = None

sudokuObject = None

solvedPuzzleForColor = None

# s = Sudoku(puzzle1, CONSTRAINTS9)
# if AC3(s):
#     sol_dict = backtracking_search(s)
#     assert s.goal_test(sol_dict) == True
#     # print(s.pruned)
#     grid_values = {name: [] for name in s.cell_names}
#     for assignment in s.assignments:
#         for cell_name, cell_value in assignment.items():
#             if cell_value not in grid_values[cell_name]:
#                 grid_values[cell_name].append(cell_value)
#     # print(grid_values)
#     sol = dict(sorted(sol_dict.items()))
#     for i in range(s.size):
#         for j in range(s.size):
#             print(s.puzzle[i][j] if s.puzzle[i][j] else 0, end=' ')
#         print()
#     print('Solutions:')
#     for i in range(s.size):
#         for j in range(s.size):
#             print(sol['C{}{}'.format(i+1, j+1)], end=' ')
#         print()
# else:
#     print("Solution not found!!!")

colors = ['deepskyblue', 'darkorange', 'purple', 'green', 'red', 'magenta', 'brown', 'greenyellow']

def generateCustomPuzzleTable():
    customPuzzleTable = ['<form method="POST"><div class="text-align-webkit-center"><table id="grid">']
    for i in range(9):
        customPuzzleTable.append('<tr>')
        for j in range(9):
            customPuzzleTable.append(f'<td><input type="number" maxlength="1" name="C{i+1}{j+1}" id="C{i+1}{j+1}" class="input_class" oninput="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);"></td>')
        customPuzzleTable.append('</tr>')
    customPuzzleTable.append('</table></div>')
    customPuzzleTable.append('<button type="submit" id="custom_solve_btn" name="custom_solve_btn" class="">Use this for custom puzzle</button>')
    customPuzzleTable.append('</form>')
    return ''.join(customPuzzleTable)

def generateInitialTable(puzzle):
    if puzzle:
        html = ['<div class="text-align-webkit-center"><table id="initial_table">']
        for i, row in enumerate(puzzle):
            html.append('<tr>')
            for j, col in enumerate(row):
                if col:
                    html.append(f'<td><span id="C{i+1}{j+1}">{ col }</span></td>')
                else:
                    html.append(f'<td><span id="C{i+1}{j+1}"></span></td>')
            html.append('</tr>')
        html.append('</table></div>')
        return ''.join(html)
    return ""

def generateSolutionTable(solvedPuzzle, failedValues):
    if solvedPuzzle:
        html = ['<div class="text-align-webkit-center"><table id="solution_table">']
        for i, cell_name in enumerate(solvedPuzzle):
            if int(cell_name[-1]) == 1:
                html.append('<tr>')
            html.append(f'<td style="color:{ solvedPuzzle[cell_name]["color"] };"><span id="{cell_name}_sol">{ solvedPuzzle[cell_name]["value"] }</span>')
            for val in failedValues[cell_name]:
                html.append(f'<span>, <s>{ val }</s></span>')
            html.append('</td>')
            if int(cell_name[-1]) == 9:
                html.append('</tr>')
        html.append('</table>')
        html.append('<form action="/stepsolutions"><button id="step_solution" name="step_solution" type="submit" class="margin-y-16px">Step by Step Solution</button></form>')
        html.append('</div>')
        return ''.join(html)
    return '<h2>No Solution Found!!!</h2>'

@app.route("/", methods=["GET", "POST"])
def homePage():
    global sudokuObject, solvedPuzzleForColor
    selectedPuzzle = None
    solvedPuzzle = None
    failedValues = None
    customPuzzle = None
    initialTable = ""
    solutionTable = ""
    customPuzzleTable = ""
    puzzleNames = [
        { 'value': '', 'label': '', 'selected': True },
        { 'value': 'puzzle1', 'label': 'Puzzle 1', 'selected': False },
        { 'value': 'puzzle2', 'label': 'Puzzle 2', 'selected': False },
        { 'value': 'puzzle3', 'label': 'Puzzle 3', 'selected': False },
        { 'value': 'puzzle4', 'label': 'Puzzle 4', 'selected': False },
        { 'value': 'puzzle5', 'label': 'Puzzle 5', 'selected': False },
        { 'value': 'customPuzzle', 'label': 'Custom Puzzle', 'selected': False}
    ]
    if request.method == "POST":
        puzzlename = request.form.get('puzzlename')
        if puzzlename == 'customPuzzle':
            customPuzzleTable = generateCustomPuzzleTable()
        for p in puzzleNames:
            if p['value'] == puzzlename:
                p['selected'] = True
                selectedPuzzle = globals().get(puzzlename)
            else:
                p['selected'] = False
        if 'custom_solve_btn' in request.form:
            puzzlename = 'customPuzzle'
            customPuzzle = []
            for i in range(9):
                row = []
                for j in range(9):
                    idx = 'C{}{}'.format(i+1, j+1)
                    row.append(int(request.form.get(idx)) if request.form.get(idx) else None)
                customPuzzle.append(row)
            selectedPuzzle = customPuzzle
        if selectedPuzzle:
            s = Sudoku(selectedPuzzle, CONSTRAINTS9)
            if AC3(s):
                sol_dict = backtracking_search(s)
                assert s.goal_test(sol_dict) == True
                solvedPuzzle = {}
                for i in range(s.size):
                    for j in range(s.size):
                        idx = 'C{}{}'.format(i+1, j+1)
                        solvedPuzzle[idx] = {}
                        solvedPuzzle[idx]['value'] = sol_dict[idx]
                failedValues = { name: [] for name in s.cell_names }
                for assignment in s.assignments:
                    for cell_name, cell_value in assignment.items():
                        if cell_value not in failedValues[cell_name] and cell_value is not solvedPuzzle[cell_name]['value']:
                            failedValues[cell_name].append(cell_value)
                for cell_name in solvedPuzzle:
                    if cell_name in s.prefilled_cell_names:
                        solvedPuzzle[cell_name]['color'] = 'black'
                    else:
                        solvedPuzzle[cell_name]['color'] = colors[len(failedValues[cell_name])]
                sudokuObject = copy.deepcopy(s)
                solvedPuzzleForColor = copy.deepcopy(solvedPuzzle)
        initialTable = generateInitialTable(selectedPuzzle)
        solutionTable = generateSolutionTable(solvedPuzzle, failedValues)
    return render_template('index.html', 
                           puzzleNames=puzzleNames,
                           initialTable=initialTable,
                           solutionTable=solutionTable,
                           customPuzzleTable=customPuzzleTable)

@app.route("/stepsolutions")
def setpSolutionPage():
    stepByStepSolution = [sudokuObject.prefilled_cell_names]
    prefilled_keys = sudokuObject.prefilled_cell_names.keys()
    reducedAssignments = []
    for assignment in sudokuObject.assignments:
        localAssignment = {}
        for key in assignment:
            if key not in prefilled_keys:
                localAssignment[key] = assignment[key]
        if localAssignment and localAssignment not in reducedAssignments:
            reducedAssignments.append(localAssignment)
    stepSol = {}
    for j in range(len(reducedAssignments)):
        for k in list(reducedAssignments[j]):
            if k not in stepSol:
                stepSol[k] = [reducedAssignments[j][k]]
            elif reducedAssignments[j][k] not in stepSol[k]:
                stepSol[k].insert(0, reducedAssignments[j][k])
    counter = 0
    for cell_name in stepSol:
        stepByStepSolution.append({ **stepByStepSolution[counter], cell_name: stepSol[cell_name] })
        counter += 1
    return render_template('solution.html', 
                           stepByStepSolution=stepByStepSolution,
                           solvedPuzzleForColor=solvedPuzzleForColor)
