import pygame
from datetime import datetime
from tools import (draw_shape, flood_fill,
                   draw_pencil, draw_brush, draw_eraser, commit_text)


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Mini Paint")
    clock  = pygame.time.Clock()

    canvas = pygame.Surface((640, 480))
    canvas.fill((0, 0, 0))

    brush_size  = 2
    color       = (0, 0, 255)
    tool        = 'brush'

    drawing   = False
    start_pos = None
    last_pos  = None

    text_active = False
    text_pos    = None
    text_buffer = ""
    text_font   = pygame.font.SysFont("monospace", 20)

    SHAPE_TOOLS = ('rect', 'square', 'circle', 'line',
                   'right_triangle', 'equilateral_triangle', 'rhombus')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:

                # Text input mode — block all shortcuts
                if text_active:
                    if event.key == pygame.K_RETURN:
                        commit_text(canvas, text_buffer, text_pos, color, text_font)
                        text_active = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        text_buffer += event.unicode
                    continue

                if event.key == pygame.K_ESCAPE:
                    return

                # Ctrl+S → save
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    fname = "canvas_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
                    pygame.image.save(canvas, fname)
                    print(f"Saved: {fname}")

                # Colors
                if   event.key == pygame.K_r: color = (255, 0,   0  )
                elif event.key == pygame.K_g: color = (0,   255, 0  )
                elif event.key == pygame.K_b: color = (0,   0,   255)
                elif event.key == pygame.K_w: color = (255, 255, 255)
                elif event.key == pygame.K_k: color = (0,   0,   0  )

                # Brush sizes
                elif event.key == pygame.K_q: brush_size = 2
                elif event.key == pygame.K_e: brush_size = 5
                elif event.key == pygame.K_z: brush_size = 10

                # Tools
                elif event.key == pygame.K_1:  tool = 'pencil'
                elif event.key == pygame.K_2:  tool = 'brush'
                elif event.key == pygame.K_3:  tool = 'eraser'
                elif event.key == pygame.K_l:  tool = 'line'
                elif event.key == pygame.K_4:  tool = 'rect'
                elif event.key == pygame.K_5:  tool = 'square'
                elif event.key == pygame.K_6:  tool = 'circle'
                elif event.key == pygame.K_7:  tool = 'right_triangle'
                elif event.key == pygame.K_8:  tool = 'equilateral_triangle'
                elif event.key == pygame.K_9: tool = 'rhombus'
                elif event.key == pygame.K_f: tool = 'fill'
                elif event.key == pygame.K_t: tool = 'text'

                elif event.key == pygame.K_c:
                    canvas.fill((0, 0, 0))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if tool == 'fill':
                    flood_fill(canvas, event.pos, color)
                elif tool == 'text':
                    text_active = True
                    text_pos    = event.pos
                    text_buffer = ""
                else:
                    drawing   = True
                    start_pos = event.pos
                    last_pos  = event.pos

            if event.type == pygame.MOUSEWHEEL:
                brush_size = max(1, min(50, brush_size + event.y))

            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                if tool in SHAPE_TOOLS:
                    draw_shape(canvas, tool, color, start_pos, event.pos, w=brush_size)

            if event.type == pygame.MOUSEMOTION and drawing:
                if tool == 'pencil':
                    draw_pencil(canvas, color, last_pos, event.pos)
                    last_pos = event.pos
                elif tool == 'brush':
                    draw_brush(canvas, color, last_pos, event.pos, brush_size)
                    last_pos = event.pos
                elif tool == 'eraser':
                    draw_eraser(canvas, last_pos, event.pos, brush_size)
                    last_pos = event.pos

        # ── Render ────────────────────────────────────────────────────────
        screen.blit(canvas, (0, 0))

        if drawing and tool in SHAPE_TOOLS:
            draw_shape(screen, tool, color, start_pos,
                       pygame.mouse.get_pos(), w=brush_size)

        if text_active and text_pos:
            preview = text_font.render(text_buffer + "|", True, color)
            screen.blit(preview, text_pos)

        # ── HUD ───────────────────────────────────────────────────────────
        hud_font = pygame.font.SysFont("monospace", 13)
        size_label = {2: "Small", 5: "Medium", 10: "Large"}.get(brush_size, f"{brush_size}px")
        hud_lines = [
            f"Tool : {tool}",
            f"Color: R={color[0]} G={color[1]} B={color[2]}",
            f"Size : {size_label}  (Q=small E=med Z=large | scroll)",
            "Colors: R G B W K",
            "Tools: 1=pencil 2=brush 3=eraser L=line",
            "       4=rect 5=square 6=circle",
            "       7=right|tr 8=equil|tr 9=rhombus",
            "       F=fill T=text",
            "C=clear  Ctrl+S=save",
        ]
        hud_bg = pygame.Surface((260, len(hud_lines)*15 + 6), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 160))
        screen.blit(hud_bg, (2, 2))
        for i, line in enumerate(hud_lines):
            surf = hud_font.render(line, True, (200, 200, 200))
            screen.blit(surf, (6, 6 + i*15))

        pygame.display.flip()
        clock.tick(60)


main()