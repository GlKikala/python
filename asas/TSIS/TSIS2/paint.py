import pygame
import datetime


from tools import flood_fill

pygame.init()


WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Paint Extension")
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
current_color = BLACK
active_tool = 'pencil' # pencil, line, rect, circle, square, triangle, rhombus, eraser, fill, text
brush_size = 2
start_pos = None
running = True


font = pygame.font.SysFont("Arial", 24)
text_input = ""
text_pos = None
is_typing = False

def draw_shape(surf, tool, start, end, color, size):
    x1, y1 = start
    x2, y2 = end
    width = abs(x1 - x2)
    height = abs(y1 - y2)
    top_left = (min(x1, x2), min(y1, y2))

    if tool == 'line':
        pygame.draw.line(surf, color, start, end, size)
    elif tool == 'rect':
        pygame.draw.rect(surf, color, (*top_left, width, height), size)
    elif tool == 'circle':
        center = (x1 + (x2-x1)//2, y1 + (y2-y1)//2)
        radius = int(((x1-x2)**2 + (y1-y2)**2)**0.5) // 2
        pygame.draw.circle(surf, color, center, radius, size)
    elif tool == 'square':
        side = max(width, height)
        pygame.draw.rect(surf, color, (top_left[0], top_left[1], side, side), size)
    elif tool == 'triangle': # Тік бұрышты үшбұрыш
        pygame.draw.polygon(surf, color, [start, (x1, y2), end], size)
    elif tool == 'rhombus':
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        points = [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
        pygame.draw.polygon(surf, color, points, size)

while running:
    screen.fill((200, 200, 200)) # Фон (интерфейс үшін)
    screen.blit(canvas, (0, 0))
    
    pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_1: brush_size = 2
            if event.key == pygame.K_2: brush_size = 5
            if event.key == pygame.K_3: brush_size = 10
            
            
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                pygame.image.save(canvas, filename)
                print(f"Saved as {filename}")

        
            if is_typing:
                if event.key == pygame.K_RETURN:
                    
                    txt_surf = font.render(text_input, True, current_color)
                    canvas.blit(txt_surf, text_pos)
                    text_input = ""
                    is_typing = False
                elif event.key == pygame.K_ESCAPE:
                    text_input = ""
                    is_typing = False
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode


            if event.key == pygame.K_p: active_tool = 'pencil'
            if event.key == pygame.K_l: active_tool = 'line'
            if event.key == pygame.K_f: active_tool = 'fill'
            if event.key == pygame.K_t: active_tool = 'text'

        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if active_tool == 'fill':
                flood_fill(canvas, pos[0], pos[1], current_color)
            elif active_tool == 'text':
                is_typing = True
                text_pos = pos
                text_input = ""
            else:
                start_pos = pos

        if event.type == pygame.MOUSEBUTTONUP:
            if start_pos and active_tool not in ['pencil', 'fill', 'text']:
                draw_shape(canvas, active_tool, start_pos, pos, current_color, brush_size)
                start_pos = None
            elif active_tool == 'pencil':
                start_pos = None

        if event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]: 
                if active_tool == 'pencil':
                    if start_pos:
                        pygame.draw.line(canvas, current_color, start_pos, pos, brush_size)
                    start_pos = pos
                elif active_tool == 'eraser':
                    pygame.draw.circle(canvas, WHITE, pos, brush_size * 2)

    
    if pygame.mouse.get_pressed()[0] and start_pos and active_tool not in ['pencil', 'eraser', 'fill', 'text']:
        draw_shape(screen, active_tool, start_pos, pos, current_color, brush_size)

    
    if is_typing:
        temp_txt = font.render(text_input + "|", True, current_color)
        screen.blit(temp_txt, text_pos)

    pygame.display.flip()

pygame.quit()