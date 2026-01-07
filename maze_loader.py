MAZE_FILES = [
    "levels/maze1.txt",
    "levels/maze2.txt",
    "levels/maze3.txt",
]

current_maze_index = 0


def load_maze(filename):
    maze = []
    start_pos = None

    with open(filename, "r") as f:
        lines = [line.rstrip("\n") for line in f]

    max_len = max(len(line) for line in lines)

    for r, line in enumerate(lines):
        row = list(line.ljust(max_len))
        for c, ch in enumerate(row):
            if ch == "P":
                start_pos = (r, c)
                row[c] = " "
        maze.append(row)

    return maze, start_pos


def load_next_level():
    global current_maze_index

    if current_maze_index >= len(MAZE_FILES):
        return None, None

    maze, start = load_maze(MAZE_FILES[current_maze_index])
    current_maze_index += 1
    return maze, start
