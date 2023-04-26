## Sudoku 

Implemented the below algorithms:
1. AC-3 and Maintaining Arc Consistency
2. Backtracking Search for CSPs

### Requirements
Python 3.10

### Install Dependencies
```console
pip install -r requirements.txt
```

### Run the program
```console
python -m flask --app backtrack_search.py run
```

### Validate the program
1. Once the flask application is running, visit this url [`http://127.0.0.1:5000`](http://127.0.0.1:5000) or click on the url given in the terminal.
2. Select one of the given puzzle from dropdown menu and click on `Solve!` button.
3. For custom puzzle, select Custom Puzzle option from the dropdown menu and click on Solve! button. Then, input values in the cells and click on `Use this for custom puzzle` button rather than `Solve!` button. (only for custom puzzle)
4. Use `Step by Step Solution` button to see the solution on each cell in order the algorithm filled.
