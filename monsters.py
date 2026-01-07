import random


directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def extract_monsters(maze):
    monsters = []
    rows = len(maze)

    for r in range(rows):
        for c in range(len(maze[r])):
            if maze[r][c] == "M":
                dr, dc = random.choice(directions)
                monsters.append({"row": r, "col": c, "dr": dr, "dc": dc})
                maze[r][c] = " "
    return monsters


def move_monsters_random(maze, monsters):
    rows = len(maze)
    cols = len(maze[0])

    def in_bounds(r, c):
        return 0 <= r < rows and 0 <= c < cols

    for m in monsters:
        new_r = m["row"] + m["dr"]
        new_c = m["col"] + m["dc"]

        if not in_bounds(new_r, new_c) or maze[new_r][new_c] == "#":
            possible = []
            for dr, dc in directions:
                r2 = m["row"] + dr
                c2 = m["col"] + dc
                if in_bounds(r2, c2) and maze[r2][c2] != "#":
                    possible.append((dr, dc))

            if not possible:
                continue

            m["dr"], m["dc"] = random.choice(possible)
            m["row"] += m["dr"]
            m["col"] += m["dc"]
            continue

        m["row"] = new_r
        m["col"] = new_c

        if maze[new_r][new_c] == "@":
            possible = []
            for dr, dc in directions:
                if (dr, dc) == (-m["dr"], -m["dc"]):
                    continue

                r2 = m["row"] + dr
                c2 = m["col"] + dc
                if in_bounds(r2, c2) and maze[r2][c2] != "#":
                    possible.append((dr, dc))

            if possible:
                m["dr"], m["dc"] = random.choice(possible)



def player_hit_monster(player_row, player_col, monsters):
    return any((player_row, player_col) == (m["row"], m["col"]) for m in monsters)
