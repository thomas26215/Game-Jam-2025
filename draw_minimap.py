import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, MINIMAP_SCALE, MINIMAP_MARGIN

def draw_minimap(surface, grid, current_pos, visited_rooms):
	if not visited_rooms:
		return
	rows = [r for r, _ in visited_rooms]
	cols = [c for _, c in visited_rooms]
	min_r, max_r, min_c, max_c = min(rows), max(rows), min(cols), max(cols)
	width = (max_c - min_c + 1) * MINIMAP_SCALE
	height = (max_r - min_r + 1) * MINIMAP_SCALE
	x_offset, y_offset = SCREEN_WIDTH - width - MINIMAP_MARGIN, MINIMAP_MARGIN
	for (r, c) in visited_rooms:
		room = grid[(r, c)]
		x, y = x_offset + (c - min_c) * MINIMAP_SCALE + MINIMAP_SCALE // 2, \
			   y_offset + (r - min_r) * MINIMAP_SCALE + MINIMAP_SCALE // 2
		for direction, _ in room.doors:
			dr, dc = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}[direction]
			neighbor = (r + dr, c + dc)
			if neighbor in visited_rooms:
				nx = x_offset + (neighbor[1] - min_c) * MINIMAP_SCALE + MINIMAP_SCALE // 2
				ny = y_offset + (neighbor[0] - min_r) * MINIMAP_SCALE + MINIMAP_SCALE // 2
				pygame.draw.line(surface, (100, 100, 100), (x, y), (nx, ny), 2)
	for (r, c) in visited_rooms:
		room = grid[(r, c)]
		x, y = x_offset + (c - min_c) * MINIMAP_SCALE, y_offset + (r - min_r) * MINIMAP_SCALE
		if (r, c) == current_pos:
			color = (255, 0, 0)
		elif getattr(room, "is_final", False):
			color = (255, 255, 0)
		else:
			color = (200, 200, 200)
		pygame.draw.rect(surface, color, (x, y, MINIMAP_SCALE - 2, MINIMAP_SCALE - 2))


