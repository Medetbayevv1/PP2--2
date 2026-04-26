import pygame
import math

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Mini Paint")
    clock = pygame.time.Clock()

    # ── Canvas ────────────────────────────────────────────────────────────
    # A separate surface that holds all permanent drawings.
    # We blit it onto the screen each frame so nothing is lost.
    canvas = pygame.Surface((640, 480))
    canvas.fill((0, 0, 0))          # start with a black background

    # ── State ─────────────────────────────────────────────────────────────
    radius   = 5                    # brush/eraser half-width (scroll to change)
    color    = (0, 0, 255)          # current drawing color
    tool     = 'brush'              # active tool name

    drawing   = False               # True while the left mouse button is held
    start_pos = None                # where the current drag started
    last_pos  = None                # previous mouse position (used for brush lines)

    # ── Helper: draw shape onto a surface ─────────────────────────────────
    # Putting draw logic in one place means both the live preview (screen)
    # and the permanent commit (canvas) use identical code.

    def draw_shape(surface, t, col, sp, ep, w=2):
        """
        Draw tool shape `t` from start point `sp` to end point `ep`
        onto `surface` using colour `col` and line width `w`.
        """
        if t == 'rect':
            # Axis-aligned rectangle defined by two corner points
            rect = pygame.Rect(sp, (ep[0] - sp[0], ep[1] - sp[1]))
            pygame.draw.rect(surface, col, rect, w)

        elif t == 'square':
            # Force equal width and height – use the shorter side
            side = min(abs(ep[0] - sp[0]), abs(ep[1] - sp[1]))
            # Preserve drag direction so the square follows the cursor
            sign_x = 1 if ep[0] >= sp[0] else -1
            sign_y = 1 if ep[1] >= sp[1] else -1
            rect = pygame.Rect(sp, (sign_x * side, sign_y * side))
            pygame.draw.rect(surface, col, rect, w)

        elif t == 'circle':
            # Radius = distance from start to current mouse position
            dx = ep[0] - sp[0]
            dy = ep[1] - sp[1]
            r = int(math.hypot(dx, dy))
            pygame.draw.circle(surface, col, sp, r, w)

        elif t == 'right_triangle':
            # Right angle at start_pos.
            # The two legs run horizontally and vertically to end_pos.
            #   sp ──── (ep[0], sp[1])
            #   |      /
            #   ep ────
            p1 = sp
            p2 = (ep[0], sp[1])   # same row as start, same column as end
            p3 = ep
            pygame.draw.polygon(surface, col, [p1, p2, p3], w)

        elif t == 'equilateral_triangle':
            # Base runs from sp to ep; the apex sits directly above the midpoint.
            # Height of an equilateral triangle: h = (√3 / 2) × base
            base_vec_x = ep[0] - sp[0]
            base_vec_y = ep[1] - sp[1]
            mid_x = (sp[0] + ep[0]) / 2
            mid_y = (sp[1] + ep[1]) / 2
            # Perpendicular to the base, scaled by (√3 / 2)
            perp_x = -base_vec_y * (math.sqrt(3) / 2)
            perp_y =  base_vec_x * (math.sqrt(3) / 2)
            apex = (int(mid_x + perp_x), int(mid_y + perp_y))
            pygame.draw.polygon(surface, col, [sp, ep, apex], w)

        elif t == 'rhombus':
            # A rhombus has four vertices at the midpoints of its bounding box.
            #        top
            #       /   \
            #    left   right
            #       \   /
            #       bottom
            cx = (sp[0] + ep[0]) // 2   # horizontal centre
            cy = (sp[1] + ep[1]) // 2   # vertical centre
            top    = (cx,      sp[1])
            bottom = (cx,      ep[1])
            left   = (sp[0],   cy)
            right  = (ep[0],   cy)
            pygame.draw.polygon(surface, col, [top, right, bottom, left], w)

    # ── Main loop ─────────────────────────────────────────────────────────
    while True:

        # ── Event handling ────────────────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return                              # close window → exit

            # ── Keyboard ──────────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    return                          # ESC → exit

                # Color shortcuts
                if   event.key == pygame.K_r: color = (255, 0,   0  )   # R → red
                elif event.key == pygame.K_g: color = (0,   255, 0  )   # G → green
                elif event.key == pygame.K_b: color = (0,   0,   255)   # B → blue
                elif event.key == pygame.K_w: color = (255, 255, 255)   # W → white
                elif event.key == pygame.K_k: color = (0,   0,   0  )   # K → black

                # Tool shortcuts
                elif event.key == pygame.K_1: tool = 'brush'
                elif event.key == pygame.K_2: tool = 'rect'
                elif event.key == pygame.K_3: tool = 'circle'
                elif event.key == pygame.K_4: tool = 'eraser'
                elif event.key == pygame.K_5: tool = 'square'
                elif event.key == pygame.K_6: tool = 'right_triangle'
                elif event.key == pygame.K_7: tool = 'equilateral_triangle'
                elif event.key == pygame.K_8: tool = 'rhombus'

                # Clear canvas
                elif event.key == pygame.K_c:
                    canvas.fill((0, 0, 0))

            # ── Mouse button down: begin a new stroke / shape ──────────────
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing   = True
                start_pos = event.pos
                last_pos  = event.pos

            # ── Mouse wheel: resize brush / eraser ─────────────────────────
            if event.type == pygame.MOUSEWHEEL:
                radius = max(1, min(50, radius + event.y))

            # ── Mouse button up: commit shape to canvas ─────────────────────
            if event.type == pygame.MOUSEBUTTONUP:
                drawing  = False
                end_pos  = event.pos

                # Commit every shape-based tool to the permanent canvas
                if tool in ('rect', 'square', 'circle',
                            'right_triangle', 'equilateral_triangle', 'rhombus'):
                    draw_shape(canvas, tool, color, start_pos, end_pos, w=2)

            # ── Mouse motion: freehand brush / eraser ──────────────────────
            if event.type == pygame.MOUSEMOTION and drawing:
                if tool == 'brush':
                    # Connect last position to current with a thick line
                    pygame.draw.line(canvas, color, last_pos, event.pos, radius * 2)
                    last_pos = event.pos

                elif tool == 'eraser':
                    # Same as brush but draws in background black
                    pygame.draw.line(canvas, (0, 0, 0), last_pos, event.pos, radius * 2)
                    last_pos = event.pos

        # ── Render ────────────────────────────────────────────────────────

        # 1. Stamp the permanent canvas onto the screen first
        screen.blit(canvas, (0, 0))

        # 2. Draw a live preview of the current shape while dragging.
        #    This is drawn on `screen` only (not canvas) so it disappears
        #    when the mouse moves and is redrawn fresh each frame.
        if drawing and tool in ('rect', 'square', 'circle',
                                'right_triangle', 'equilateral_triangle', 'rhombus'):
            mouse_pos = pygame.mouse.get_pos()
            draw_shape(screen, tool, color, start_pos, mouse_pos, w=2)

        # 3. Draw a HUD in the top-left so the user knows the active tool
        hud_font = pygame.font.SysFont("monospace", 14)
        tool_labels = {
            'brush':               '1 Brush',
            'rect':                '2 Rect',
            'circle':              '3 Circle',
            'eraser':              '4 Eraser',
            'square':              '5 Square',
            'right_triangle':      '6 Right triangle',
            'equilateral_triangle':'7 Equilateral triangle',
            'rhombus':             '8 Rhombus',
        }
        hud_lines = [
            f"Tool : {tool_labels.get(tool, tool)}",
            f"Color: R={color[0]} G={color[1]} B={color[2]}",
            f"Size : {radius}  (scroll to change)",
            "C = clear canvas",
        ]
        for i, line in enumerate(hud_lines):
            surf = hud_font.render(line, True, (200, 200, 200))
            screen.blit(surf, (6, 6 + i * 16))

        pygame.display.flip()
        clock.tick(60)

main()