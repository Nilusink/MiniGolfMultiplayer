import pygame, json
pygame.init()
black = ( 0, 0, 0)
white   = ( 255, 255, 255)
w_w = 640
w_h = 480
screen = pygame.display.set_mode((w_w, w_h))
pygame.display.set_caption("Minigolf")
aktiv = True
clock = pygame.time.Clock()
with open('s.json') as f:
    data = json.load(f)
while aktiv:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            aktiv = False
    screen.fill(black)
    total = int(data["total"])
    for i in range(1, total+1):
        i = str(i)
        pos_x = int(data[i]["pos_x"])
        pos_y = int(data[i]["pos_y"])
        width = int(data[i]["width"])
        height = int(data[i]["height"])
        pygame.draw.rect(screen, white, [pos_x, pos_y, width, height])
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
quit()