import pygame
import math
from collections import deque


def draw_shape(surface, t, col, sp, ep, w=2):
    if t == 'rect':
        rect = pygame.Rect(sp, (ep[0]-sp[0], ep[1]-sp[1]))
        pygame.draw.rect(surface, col, rect, w)

    elif t == 'square':
        side   = min(abs(ep[0]-sp[0]), abs(ep[1]-sp[1]))
        sign_x = 1 if ep[0] >= sp[0] else -1
        sign_y = 1 if ep[1] >= sp[1] else -1
        pygame.draw.rect(surface, col,
                         pygame.Rect(sp, (sign_x*side, sign_y*side)), w)

    elif t == 'circle':
        r = int(math.hypot(ep[0]-sp[0], ep[1]-sp[1]))
        pygame.draw.circle(surface, col, sp, r, w)

    elif t == 'line':
        pygame.draw.line(surface, col, sp, ep, w)

    elif t == 'right_triangle':
        p2 = (ep[0], sp[1])
        pygame.draw.polygon(surface, col, [sp, p2, ep], w)

    elif t == 'equilateral_triangle':
        mid_x  = (sp[0]+ep[0]) / 2
        mid_y  = (sp[1]+ep[1]) / 2
        bvx    = ep[0]-sp[0]
        bvy    = ep[1]-sp[1]
        perp_x = -bvy * (math.sqrt(3) / 2)
        perp_y =  bvx * (math.sqrt(3) / 2)
        apex   = (int(mid_x+perp_x), int(mid_y+perp_y))
        pygame.draw.polygon(surface, col, [sp, ep, apex], w)

    elif t == 'rhombus':
        cx = (sp[0]+ep[0]) // 2
        cy = (sp[1]+ep[1]) // 2
        pygame.draw.polygon(surface, col,
            [(cx, sp[1]), (ep[0], cy), (cx, ep[1]), (sp[0], cy)], w)


def flood_fill(surface, pos, fill_color):
    target = surface.get_at(pos)[:3]
    if target == fill_color:
        return
    w, h    = surface.get_size()
    queue   = deque([pos])
    visited = {pos}
    while queue:
        x, y = queue.popleft()
        surface.set_at((x, y), fill_color)
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in visited:
                if surface.get_at((nx, ny))[:3] == target:
                    visited.add((nx, ny))
                    queue.append((nx, ny))


def draw_pencil(canvas, color, last_pos, current_pos):
    pygame.draw.line(canvas, color, last_pos, current_pos, 1)


def draw_brush(canvas, color, last_pos, current_pos, size):
    pygame.draw.line(canvas, color, last_pos, current_pos, size)


def draw_eraser(canvas, last_pos, current_pos, size):
    pygame.draw.line(canvas, (0, 0, 0), last_pos, current_pos, size)


def commit_text(canvas, text, pos, color, font):
    surf = font.render(text, True, color)
    canvas.blit(surf, pos)