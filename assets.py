import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 600))
my_image = pygame.image.load("images.png")


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  

    screen.fill("#090909")
    screen.blit(my_image, (90, 0))
    pygame.display.flip()


pygame.quit()