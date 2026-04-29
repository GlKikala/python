import pygame

def flood_fill(surface, x, y, new_color):
    # Қазіргі нүктенің түсін аламыз
    target_color = surface.get_at((x, y))
    if target_color == new_color:
        return

    # Өңделетін пиксельдер кезегі
    pixels = [(x, y)]
    width, height = surface.get_size()

    while pixels:
        curr_x, curr_y = pixels.pop()
        
        if surface.get_at((curr_x, curr_y)) != target_color:
            continue
        
        # Түсті өзгерту
        surface.set_at((curr_x, curr_y), new_color)

        # Көрші пиксельдерді тексеру (жоғары, төмен, сол, оң)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = curr_x + dx, curr_y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if surface.get_at((nx, ny)) == target_color:
                    pixels.append((nx, ny))