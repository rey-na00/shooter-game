from random import randint
from time import time as timer
from pygame import *
#menambahkan picture
img_back = 'galaxy.jpg' #background game
img_hero = 'rocket.png' #player
img_enemy = 'ufo.png' #enemy
img_bullet = 'bullet.png' #peluru
img_asteroid = 'asteroid.png' #enemy ke-2

#Layar game
lebar = 700
tinggi = 500
display.set_caption('Game Shooter')
window = display.set_mode((lebar, tinggi))
background = transform.scale(image.load(img_back),(lebar,tinggi))

#musik latar
mixer.init()
# mixer.music.load('song.mp3')
# mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

#font and label
font.init()
font1 = font.SysFont('Calibri', 25)
font2 = font.SysFont('Arial', 80)
menang = font2.render('KAMU MENANG', True, (255,255,255))
kalah = font2.render('KAMU KALAH!!!', True, (180,0,0))

score = 0 #menghitung jumlah pesawat yang ditembak
lost = 0 #menghitung jumlah pesawat yang dilewati
goal = 20 #menghitung target pesawat yang ditembak
max_lost = 10 #menghitung akumulasi jumlah pesawat yang dilewati
life = 3 #nyawanya pesawat

#class sprite
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_w, size_h, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_w, size_h))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    
    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

#class player
class Player(GameSprite):
    def gerak(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < lebar - 80:
            self.rect.x += self.speed
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < tinggi - 100:
            self.rect.y += self.speed
    #membuat methode untuk menembak
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

#class Enemy
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > tinggi:
            self.rect.x = randint(80, lebar-80)
            self.rect.y = 0
            lost = lost + 1    

#class peluru
class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        #menghilang jika mencapai tepi layar atas
        if self.rect.y < 0:
            self.kill()

#membuat fungsi reset_game()
def reset_game():
    global score, lost, finish, monsters, bullets, asteroids
    score = 0
    lost = 0
    finish = False
    monsters.empty()
    bullets.empty()
    asteroids.empty()
    for i in range(1,6): #ufo
        monster = Enemy(img_enemy, randint(80, lebar-80), -40, 80, 50, randint(3,7))
        monsters.add(monster)
    for i in range(1,4): #asteroid
        asteroid = Enemy(img_asteroid, randint(30, lebar-30), -40, 80, 50, randint(1,5))
        asteroids.add(asteroid)
    pesawat.rect.x = 5
    pesawat.rect.y = tinggi-100

#objek game
pesawat = Player(img_hero, 5, tinggi-100, 80, 100, 20)
#membuat group enemy
monsters = sprite.Group()
for i in range(1,6):
    monster = Enemy(img_enemy, randint(80, lebar-80), -40, 80, 50, randint(3,7))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(1,4): 
    asteroid = Enemy(img_asteroid, randint(30, lebar-30), -40, 80, 50, randint(1,5))
    asteroids.add(asteroid)

#membuat group peluru
bullets = sprite.Group()

#loop game
finish = False
run = True

#membuat variabel reload dan waktu reload
reload_time = False
num_fire = 0

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        #menggunakan tombol spasi untuk menembak
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and reload_time == False:
                    num_fire += 1
                    fire_sound.play()
                    pesawat.fire()
                #memeriksa tembakan lebih dari 5
                if num_fire >= 5 and reload_time == False:
                    last_time = timer()
                    reload_time = True
            #menggunakan tombol R untuk Reset dan Q untuk Quit
            elif e.key == K_r and finish:
                reset_game()
            elif e.key == K_q:
                run = False

    if not finish:
        window.blit(background,(0,0))
        pesawat.gerak()
        monsters.update()
        bullets.update()
        asteroids.update()

        pesawat.draw()
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window)

        #membuat reload time
        if reload_time == True:
            now_time = timer() #membaca waktu
            if now_time - last_time < 3:
                reload = font1.render('wait, reload...reload...reload', True, (255,255,255))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0
                reload_time = False

        #menulis missed
        text_lose = font1.render('Missed: ' + str(lost), 1, (255,255,255))
        window.blit(text_lose, (10, 50))

        #memeriksa tabrakan peluru-ufo
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(img_enemy, randint(80, lebar-80), -40, 80, 50, randint(3,7))
            monsters.add(monster)
        
        #memeriksa tabrakan peluru - asteroid
        collides = sprite.groupcollide(asteroids, bullets, True, True)
        for c in collides:
            score += 1
            asteroid = Enemy(img_asteroid, randint(30, lebar-30), -40, 80, 50, randint(1,5))
            asteroids.add(asteroid)

        #memeriksa tabrakan pesawat-musuh
        # if sprite.spritecollide(pesawat, monsters, False) or sprite.spritecollide(pesawat, asteroids, False) or lost >= max_lost:
        #     finish = True
        #     window.blit(kalah, (100,200))
        
        #mengurangi nyawa/life pesawat jika terjadi tabrakan
        if sprite.spritecollide(pesawat, monsters, False) or sprite.spritecollide(pesawat, asteroids, False):
            sprite.spritecollide(pesawat, monsters, True)
            sprite.spritecollide(pesawat, asteroids, True)
            life -= 1
        
        #memeriksa kondisi kalah
        if life == 0 or lost >= max_lost:
            finish = True
            window.blit(kalah, (100,200))
        
        #memeriksa kondisi menang
        if score >= goal:
            finish = True
            window.blit(menang, (100,200))
        
        #membuat warna untuk tampilan nyawa pesawat
        if life == 3:
            life_color = (0,150,0)
        if life == 2:
            life_color = (150,150,0)
        if life == 1:
            life_color = (150,0,0)
        text_life = font2.render(str(life), True, life_color)
        window.blit(text_life, (650,10))

        #menulis score
        text_score = font1.render('Score: ' + str(score), 1, (255,255,255))
        window.blit(text_score, (10, 20))
    else:
        score = 0
        lost = 0
        num_fire = 0
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        for a in asteroids:
            a.kill()
        #menampilakan R untuk Reset dan Q untuk Quit
        reset_quit_label = font1.render('Press R to Reset or Q to Quit', 1, (255,255,255))
        window.blit(reset_quit_label, (150, 300))
    display.update()
    time.delay(60)