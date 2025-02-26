import time
import neat  # Essa é a parada de AI
import pygame
import os
import random
pygame.font.init()  # Iniciar a biblioteca das fontes do SDL

# Definição do tamanho da janela pra ficar com a mesma proporção de um iPhone
WIN_HEIGHT = 800
WIN_WIDTH = 500

GEN = 0
initSPEED = 5
speed = 2
highestSpeed = 0
highScore = 0

# Isoo de ampliar é provavelmente pq a imagem é em pixels
# Isso é um array de várias imagens, o Python cria automaticamente os tipos de tudo
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

#STAT_FONT = pygame.font.SysFont("comicsansms",50)
STAT_FONT = pygame.font.SysFont("minecraft",50)


# Agora vamos criar os objetos de cada coisa
class Bird:
    # Constantes do pássaros.
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # O máximo que a imagem do pássaro pode girar.
    ROT_VEL = 20
    ANIMATION_TIME = 5

    # Inicialização do objeto:
    # Acho que isso tudo são as posições iniciais.
    # As variáveis que realmente mudam.
    def __init__(self,x,y):  # Esses parâmetros servem para definir a posição inicial do pássaro quando criamos um deles
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0  # A velocidade do pássaro que vai aumentando?
        self.height = self.y  # N entendi pq tem 2x isso de y, pq n usa o mesmo?
        self.img_count = 0
        self.img = self.IMGS[0]  # Começar com a imagem 0

    # Agora vamos definir uma das ações que o pássaro pode fazer (Programação Orientada à Objetos)
    def jump(self):
        # Agora que já defini os objetos no def antecedente, posso affetar suas variáveis já criadas
        self.vel = -10.5
        self.tick_count = 0  # Ainda n etendi para que esse serve, mas acho que são os frames
        self.height = self.y  # N entendi pq tem 2x isso de y, pq n usa o mesmo?

    def move(self):
        self.tick_count += 1
        # Acho que isso de tanto self é pq vão ter vários pássaros de uma vez por geração
        # Essa fórmula representa o quanto o pássaro vai subir ou descer de acordo com sua velocidade. É uma fórmula de física.
        # d significa displacement
        d = self.vel*self.tick_count + 1.5*self.tick_count**2  # **2 significa ^2
        # isso faz o pássaro desenhar um arco

        # Evitar passar de 16 pixels ("Fail-Safe")
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        # Alterar efetivamente a posição salva nele
        #self.y += d  # eu
        self.y = self.y + d  # ele

        # Agora vamos ver o ângulo do pássaro
        # Se está subindo
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:  # Para evitar de passar da rotação máxima
                self.tilt = self.MAX_ROTATION
        else:
             if self.tilt > -90:  # Se ele ficar com a cara totalmente para baixo, ele deve descer rapidão em stall. Pra cima ele só vira um pouco e pra baixo ele vira tudo.
                 self.tilt -= self.ROT_VEL

    def draw(self,win):
        self.img_count +=1

        # A alteração das imagens  (eu faria com um Switch case)
        if self.img_count < self.ANIMATION_TIME:  # Começar pela imagem inicial?
            self.img = self.IMGS[0]
        elif  self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif  self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif  self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif  self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # Para ele não ficar batendo as asas quando estiver caindo, escolhemos uma imagem só
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2  # Isso é pra na hora que ele voltar a subir, já subir batendo as asas

        # Girar a imagem
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)  # self.x, self.y é basicamente o Top Left da imagem
        win.blit(rotated_image, new_rect.topleft)  # Blit = desenhar

    # Para detectar colisões
    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)  # Pegar a superfície da imagem atual

class Pipe():
   
    GAP = 200 # Distancia entre tubos
    VEL = speed

    def __init__(self,x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True)  # A imagem de cima é a mesma imagem, só que invertida
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False  # Para verificar se ele já passou pelo pássaro
        self.set_height()  # Método

    def set_height(self):
        # Definindo a posição dos dois tubos
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self, vel):
        #self.x -= self.VEL  # Ele vai se movendo para a esquerda de acordo com a velocidade atual
        self.x -= vel  # Ele vai se movendo para a esquerda de acordo com a velocidade atual


    # Desenhar os dois tubos
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # Pixel perfect collision
    def colide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)  # As imagens que eu defini como constantes lá no começo dos tubos
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Calcular a distância dos objetos
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Pontos onde se colidem, se n colidir, vão retornar "False"
        b_point = bird_mask.overlap(bottom_mask,bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        # Então se colidir:
        if b_point or t_point:
            return True  # Sim, tem uma colisão
        return False  # else

# O piso
class Base:
    VEL = speed
    WIDTH = BASE_IMG.get_width()  # O caminho da imagem foi definido lá encima
    IMG = BASE_IMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH  # Isso serve para pegar as posições da esquerda, como a imagem se repete, ele vai começar exatamente onde acaba a outra

    def move(self, vel):
        self.x1 -= vel
        self.x2 -= vel

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # Desenhamos os tubos
    def draw(self,win):
        win.blit(self.IMG,((self.x1,self.y)))
        win.blit(self.IMG,((self.x2,self.y)))




def draw_window(win, birds, pipes, base, score, gen, SPEED):
    win.blit(BG_IMG, (0,0))  # Desenhar o fundo

    for pipe in pipes:
        pipe.draw(win)

    # Escrever o texto na tela
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    sombra = STAT_FONT.render("Score: " + str(score), 1, (55,55,55))

    win.blit(sombra,(WIN_WIDTH - 12 - sombra.get_width(),10))
    win.blit(text,(WIN_WIDTH - 8 - text.get_width(),10))

    # Escrever as gerações na tela
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    sombra = STAT_FONT.render("Gen: " + str(gen), 1, (55,55,55))

    win.blit(sombra,(10,10))
    win.blit(text,(14,10))

    # Escrever a velocidade na tela
    text = STAT_FONT.render("Speed: " + str(SPEED), 1, (255,255,255))
    sombra = STAT_FONT.render("Speed: " + str(SPEED), 1, (55,55,55))

    win.blit(sombra,(10,70))
    win.blit(text,(14,70))

    base.draw(win)
    for bird in birds:
        bird.draw(win)  # Usamos o método que criamos

    pygame.display.update()  # Atualizar a tela


def main(genomes, config):

    global GEN
    GEN += 1

    nets = []
    ge = []  # Genomes (Isso é o que vai controlar os pássaros)
    birds = []

    for _, g in genomes:  # Esse underline é porque os genomes tem index tbm e n podemos
                          # deixar de recuperá-lo, mas no final ele não será usado para nada.
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)  # n entendi
        birds.append(Bird(230,350))
        ge.append(g)  # Adicionar o Genome à lista


    BASE_HEIGHT = 730

    base = Base(BASE_HEIGHT)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))  # Preciso desses dois parentesis para que a função entenda que são as coordenadas
    clock = pygame.time.Clock()  # Usar FPS ao invés da velocidade máxima do PC

    # Init variables
    score = 0
    speed = initSPEED
    highestSpeed = 0
    highScore = 0

    run = True  # Para podermos parar o jogo depois

    while run:
        clock.tick(120)  # 30 FPS
        for event in pygame.event.get():  # Detectar eventos
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()


        # Para saber com qual tubo estamos verificamos a colisão
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:  # Caso não sobre nenhum pássaro, queremos sair dessa geração
            run = False
            break



        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # Para motivar o pássaro a continuar (1 ponto por segundo a 30 FPS)

            # O valor que a AI vai mandar como resposta
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            # Vemos se está maior que 0.5 (Pq? pq > 0.5 => 50%?)
            if output[0] > 0.5:  # 0 = 1, pq nesse caso só temos um neurônio de saída, posso ter mais
                bird.jump()

        add_pipe = False
        rem = []  # Lista para remover


        for pipe in pipes:

            for x, bird in enumerate(birds):  # Isso serve para obter o conteúdo do item,
                                              # mas também o seu index.
                # Verificar a colisão com o pássaro
                if pipe.colide(bird):
                    ge[x].fitness -= 1  # Mostrar pra AI que isso é ruim
                    birds.pop(x)  # Excluir esse pássaro
                    nets.pop(x)  # Apagar também a rede neural associada à esse pássaro
                    ge.pop(x)


                # Contar o score, ver quando o tubo passou
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # Verificar se o tubo passou do limite da tela
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move(speed)

        if add_pipe:
            score += 1
            speed += 0.2

            # Salvar vel e score max
            if speed > highestSpeed:
                #os.system("clear")
                highestSpeed = speed
                highScore = score
                print(f"Nova vel max: {highestSpeed} | Score: {highScore}")
                

            for g in ge:
                g.fitness += 5  # 5 porque o objetivo não é simplesmente de ir mais longe,
                                # mas bater, ele tem que ser motivado a passar pelo meio
                                # dos túneis.

            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)


        # Verificação da colisão de cada pássaro com o piso ou no teto
        for x, bird in enumerate(birds):
            # Vai pegar a altura da imagem atual, porque a imagem troca junto com o movimento do pássaro
            if bird.y + bird.img.get_height() >= BASE_HEIGHT or bird.y < 0:
                birds.pop(x)  # Usa o index para tirar ele da lista
                nets.pop(x)
                ge.pop(x)

        base.move(speed)
        draw_window(win,birds,pipes,base,score, GEN, speed)  # Para relmente desenhar a tela a cada frame


# Loop infinito do jogo, pra ficar rodando enquando o jogo estiver aberto


# Aparentemente isso é o que vai fazer rodar a AI
def run(config_file):
    # config = neat.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultStagnation, config_path)
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)



    # Criamos a população, chamamos ela de "p"
    p = neat.Population(config)

    # Para ter em detalhes de tudo o que acontece, sobre cada geração, fitness
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # A função de fitness sera a main() pq é ela que faz o passaro mover

    # O melhor de todos os pássaros
    # posso salvar ele usando a bilbioteca pickle para reutilisar dps
    # eu teria que escolher um score maximo, senão vai ficar rodando pra sempre
    # if score > [qto quero] ; break
    while True:
        winner = p.run(main,50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)  # Recuperar o caminho do arquivo atual
    # Juntamos o caminho que encontramos com o arquivo de configuração
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)  # Run é so a função que criamos antes
