import pygame
from collections import deque


def flood_fill(surface, start_pos, fill_color):
    """BFS flood fill on a pygame Surface."""
    x, y = int(start_pos[0]), int(start_pos[1])
    w, h = surface.get_size()
    if not (0 <= x < w and 0 <= y < h):
        return

    target = surface.get_at((x, y))[:3]
    new_col = fill_color[:3] if len(fill_color) > 3 else tuple(fill_color)

    if target == new_col:
        return

    queue = deque([(x, y)])
    visited = {(x, y)}

    while queue:
        cx, cy = queue.popleft()
        if surface.get_at((cx, cy))[:3] != target:
            continue
        surface.set_at((cx, cy), new_col)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
