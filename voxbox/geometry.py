def draw_box(volume, lower_corner, upper_corner, col0, col1):
    
    for plane in range(lower_corner[0], upper_corner[0] + 1):
        for col in range(lower_corner[1], upper_corner[1] + 1):
            for row in range(lower_corner[2], upper_corner[2] + 1):
                
                p = (int(plane) // 8) % 2
                c = (int(col) // 8) % 2
                r = (int(row) // 8) % 2
                    
                val = p ^ c ^ r
                
                if val == 0:                
                    volume[plane][col][row] = col0
                else:
                    volume[plane][col][row] = col1 
