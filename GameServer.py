import threading
import pygame
import socket
import sys
import random

# Global variables
name = "test"
posx = 300
posy = 300
score = 0
bucket_speed = 10
game_over = False

def reset_game():
    """Reset game variables to their initial state."""
    global posx, posy, score, bucket_speed, game_over, falling_object, falling_speed
    posx = 300
    posy = 300
    score = 0
    bucket_speed = 10
    game_over = False
    falling_object.x = random.randint(0, 600 - falling_object.width)
    falling_object.y = 0
    falling_speed = 1

def GameThread():
    pygame.init()
    fps = pygame.time.Clock()
    screen_size = screen_width, screen_height = 600, 400
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Bucket Catch Game')

    # Load assets
    background = pygame.image.load("sky_background.jpg")
    background = pygame.transform.scale(background, screen_size)
    bucket_image = pygame.image.load("bucket.png").convert_alpha()
    bucket_image = pygame.transform.scale(bucket_image, (75, 75))
    falling_item_image = pygame.image.load("apple.png")
    falling_item_image = pygame.transform.scale(falling_item_image, (25, 25))

    font = pygame.font.SysFont('Comic Sans MS', 30)
    global falling_object, falling_speed
    falling_object = pygame.Rect(random.randint(0, screen_width - 25), 0, 25, 25)
    falling_speed = 1

    global posx, posy, score, bucket_speed, game_over

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                reset_game()

        if game_over:
            screen.fill((255, 255, 255, 128))  # Semi-transparent red overlay
            game_over_text = font.render("Game Over! Press R to Restart", True, (0, 0, 0))
            score_text = font.render(f"Final Score: {score}", True, (0, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - 150, screen_height // 2 - 50))
            screen.blit(score_text, (screen_width // 2 - 100, screen_height // 2))
            pygame.display.update()
            continue

        # Draw the background
        screen.blit(background, (0, 0))

        # Draw the bucket and the falling object
        bucket_rect = pygame.Rect(posx, posy, 75, 75)  # Defines the bucket's position
        falling_rect = pygame.Rect(falling_object.x, falling_object.y, falling_object.width, falling_object.height)
        screen.blit(bucket_image, bucket_rect)  # Draw only the image without a rectangle
        screen.blit(falling_item_image, falling_rect)  # Draw the falling item


        # Score display
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # Update falling object position
        falling_object.y += falling_speed

        collision = bucket_rect.colliderect(falling_object)
        if collision:
            falling_object.x = random.randint(0, screen_width - falling_object.width)
            falling_object.y = 0
            falling_speed += 0.5
            score += 1
            bucket_speed += 10
        elif falling_object.y >= screen_height:  # Object hits the floor
            game_over = True

        pygame.display.update()
        fps.tick(60)

def ServerThread():
    global posy, posx, bucket_speed, game_over
    host = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host = s.getsockname()[0]
    s.close()
    print(host)
    port = 5000  # Port number

    server_socket = socket.socket()
    server_socket.bind((host, port))
    print("Server enabled...")
    server_socket.listen(2)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))
    
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        
        print("from connected user: " + str(data))
        if data == 'w' and not game_over:
            posy -= bucket_speed
        elif data == 's' and not game_over:
            posy += bucket_speed
        elif data == 'a' and not game_over:
            posx -= bucket_speed
        elif data == 'd' and not game_over:
            posx += bucket_speed
        elif data == 'q':  # Quit game
            pygame.quit()
            sys.exit()
    conn.close()

# Create and start threads
t1 = threading.Thread(target=GameThread, args=[])
t2 = threading.Thread(target=ServerThread, args=[])
t1.start()
t2.start()
