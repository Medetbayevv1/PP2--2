import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Mini Paint")
    clock = pygame.time.Clock()

    # Canvas (important so drawings stay)
    canvas = pygame.Surface((640, 480))
    canvas.fill((0, 0, 0))

    radius = 5
    color = (0, 0, 255)
    tool = 'brush'  # brush, rect, circle, eraser

    drawing = False
    start_pos = None
    last_pos = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                # Exit
                if event.key == pygame.K_ESCAPE:
                    return

                # Colors
                if event.key == pygame.K_r:
                    color = (255, 0, 0)
                elif event.key == pygame.K_g:
                    color = (0, 255, 0)
                elif event.key == pygame.K_b:
                    color = (0, 0, 255)
                elif event.key == pygame.K_w:
                    color = (255, 255, 255)
                elif event.key == pygame.K_k:
                    color = (0, 0, 0)

                # Tools
                elif event.key == pygame.K_1:
                    tool = 'brush'
                elif event.key == pygame.K_2:
                    tool = 'rect'
                elif event.key == pygame.K_3:
                    tool = 'circle'
                elif event.key == pygame.K_4:
                    tool = 'eraser'

            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos

            if event.type == pygame.MOUSEWHEEL:
                radius += event.y
                radius = max(1, min(50, radius))


            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                end_pos = event.pos

                if tool == 'rect':
                    rect = pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
                    pygame.draw.rect(canvas, color, rect, 2)

                elif tool == 'circle':
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    r = int((dx**2 + dy**2) ** 0.5)
                    pygame.draw.circle(canvas, color, start_pos, r, 2)

            if event.type == pygame.MOUSEMOTION and drawing:
                if tool == 'brush':
                    pygame.draw.line(canvas, color, last_pos, event.pos, radius * 2)
                    last_pos = event.pos

                elif tool == 'eraser':
                    pygame.draw.line(canvas, (0, 0, 0), last_pos, event.pos, radius * 2)
                    last_pos = event.pos

        # Draw canvas
        screen.blit(canvas, (0, 0))

# Draw preview shape while dragging
        if drawing and tool in ['rect', 'circle']:
            mouse_pos = pygame.mouse.get_pos()

            if tool == 'rect':
                rect = pygame.Rect(start_pos, (mouse_pos[0]-start_pos[0], mouse_pos[1]-start_pos[1]))
                pygame.draw.rect(screen, color, rect, 2)

            elif tool == 'circle':
                dx = mouse_pos[0] - start_pos[0]
                dy = mouse_pos[1] - start_pos[1]
                r = int((dx**2 + dy**2) ** 0.5)
                pygame.draw.circle(screen, color, start_pos, r, 2)

        pygame.display.flip()
        clock.tick(60)

main()