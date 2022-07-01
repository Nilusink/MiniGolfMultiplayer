import pygame, json
pygame.init()
black = ( 0, 0, 0)
white   = ( 255, 255, 255)
screen_info = pygame.display.Info()
window_size = (screen_info.current_w, screen_info.current_h)
w_w = window_size[0]
w_h = window_size[1]
screen = pygame.display.set_mode((window_size))
pygame.display.set_caption("Minigolf")
aktiv = True
clock = pygame.time.Clock()
class ball:
    def erstellen():
        colour = (0,0,255) #green
        pos_x_y = (150, 150)
        circle_radius = 12
        border_width = 0 #0 = filled circle
        pygame.draw.circle(screen, colour, pos_x_y, circle_radius, border_width)
with open('Maps/Map1.json') as f:
    data = json.load(f)
while aktiv:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            aktiv = False
    screen.fill(black)
    total = data["total"]
    for i in range(1, total+1):
        i = str(i)
        p1_x = data[i]["p1_x"]
        p1_y = data[i]["p1_y"]
        p2_x = data[i]["p2_x"]
        p2_y = data[i]["p2_y"]
        print(p1_y*w_h)
        print(p2_x*w_w)
        ball.erstellen()
        pygame.draw.line(screen, white, (p1_x*w_w, p1_y*w_h), (p2_x*w_w, p2_y*w_h))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
quit()
#"": {"p1_x": 0., "p1_y": 0., "p2_x": 0., "p2_y": 0.}