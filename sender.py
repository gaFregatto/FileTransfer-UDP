from tkinter import *
from tkinter.filedialog import askopenfilename
from socket import socket, AF_INET, SOCK_DGRAM
import threading
import time
import os


JANELA = 3
TIMEOUT = 0.2


class Sender():
    def __init__(self, root, ip, port, buffer, sleep, bufferConfirm):
        self.root = root
        self.ip = ip
        self.port = port
        self.buffer = buffer
        self.sleep = sleep
        self.bufferConfirm = bufferConfirm

    def close(self):
        self.root.quit()

    def setIp(self):
        global e1, e2
        self.ip = e1.get()
        self.port = int(e2.get())
        e1.destroy()
        e2.destroy()
        setIpButton.destroy()
        print("Current connection >> %s:%s" % (self.ip, self.port))

    def set_file(self):
        self.pathfile = askopenfilename()
        self.buffer = BUFFER
        sendFileButton = Button(
            self.root, text='Enviar Arquivo', command=self.send_file)
        sendFileButton.place(x=20, y=130)
        selectFileButton.destroy()

    def send_file(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect((self.ip, self.port))
        file = open(self.pathfile, "rb")
        data = file.read()

        # Para o pacote ter espaço de 4 bytes para armazenar número do pacote corrente
        n = int(len(data)/(self.buffer-4))
        numberPacketsInBytes = n.to_bytes(4, 'big')
        b = numberPacketsInBytes + self.getFileName().encode()

        print("Filename: "+self.getFileName())
        print("Número de pacotes: "+str(n))

        s.settimeout(TIMEOUT)

        iniciot = time.time()   # inicio da transmissão
        s.sendto(b, (self.ip, self.port))
        # os.system("pause")

        j = 0  # Controla o tamanho da janela de transmissao
        k = 1  # Numero de tentativas de retransmissão
        i = 0
        while(i in range(n+1)):
            # Número do pacote em bytes para ser enviado no pacote
            npackage = i.to_bytes(4, 'big')
            package = npackage + self.partOfData(data, i)
            s.sendto(package, (self.ip, self.port))
            print("Enviado pacote numero: "+str(i)+" || "+str(package))

            # Controle de janela de transmissao
            if j == JANELA:
                j = -1

                try:
                    response = s.recv(self.buffer).decode()
                    # print(">>"+response)
                    if(response.find('erro') == 0 and response.find('confirmado') < 0):
                        print("Erro na transmissao, tentando enviar novamente..")
                        i = i - JANELA - 1
                        j = - 1
                        print("I depois da notificação de erro: "+str(i))
                        # os.system("pause")
                    elif(response.find('confirmado') == 0):
                        print("Confirmacao recebida, continuando transmissao..")
                    response = '\0'
                    # Aguarda 2ms o recebimento da confirmacao, caso contrario, lanca o timeout

                except TimeoutError:
                    print("Timeout numero " + str(k))
                    if(k < 3):
                        print("Tentando retransmissão")
                        i = i - JANELA - 1
                        j = -1
                        k = k + 1
                    else:
                        print(
                            "Timeouts excessivos, melhore sua conexão e tente novamente.")
                        break
                except:
                    print("Houve algum erro desconhecido.")
                    break
            i = i + 1
            j = j + 1

        fimt = time.time()  # fim da transmissão
        print("\n\n\n\n===========================================\n\n\n")
        print("Arquivo enviado com sucesso!")
        print("Tamanho do arquivo: " + str(n * (BUFFER-4)) + " B.")
        print("Numero de pacotes enviados: " + str(n+1))
        print("Nome do arquivo: " + self.getFileName())
        print("Duração de envio: "+str(fimt - iniciot) + " segundos.")
        print("Numero total de timeouts: " + str(k-1))
        print("Velocidade: "+str(n*((BUFFER-4)/1000000)/(fimt-iniciot)))
        file.close()
        # s.close()

    def getFileName(self):
        size = len(self.pathfile)
        i = size - 1
        while i > 0:
            if self.pathfile[i] == '/':
                filename = self.pathfile[i+1:size]
                return filename
            i = i - 1
        return ''

    def partOfData(self, data, i):
        # Multiplicamos por 196 pois o tamanho do buffer é 200 e agora com a janela de transmissão
        # guardamos 4 bytes (200 - 4 = 196) para enviar em todos pacotes,
        # qual pacote está sendo enviado
        return data[(i*(self.buffer-4)):(self.buffer-4)*(i+1)]


if __name__ == '__main__':
    # Definindo algumas constantes
    BUFFER = 2000
    SLEEP_TIME = 0.02
    IP = '127.0.0.1'
    PORT = 6061

    # Armazenada na estância da classe Sender, sender, o root para a janela
    window = Tk()
    sender = Sender(window, IP, PORT, BUFFER, SLEEP_TIME, 11)

    sender.root.title("Troca de arquivos - Sender")
    sender.root.geometry("300x300")
    e1 = Entry(sender.root)
    e2 = Entry(sender.root)

    selectFileButton = Button(
        sender.root, text='Selecionar Arquivo', command=sender.set_file)
    selectFileButton.place(x=20, y=100)

    setIpButton = Button(
        sender.root, text='Configurar Conexão', command=sender.setIp)
    setIpButton.place(x=20, y=60)

    closeButton = Button(sender.root, text='Fechar', command=sender.close)
    closeButton.place(x=20, y=250)

    e1.place(x=20, y=20)
    e2.place(x=20, y=40)
    e1.insert(END, IP)
    e2.insert(END, str(PORT))

    # Função que cria a janela
    sender.root.mainloop()
