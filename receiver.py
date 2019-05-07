from tkinter import *
from tkinter.filedialog import askdirectory
from socket import socket, AF_INET, SOCK_DGRAM, gethostname
import struct
import time
import os

JANELA = 3
BUFFER = 2000
FIRST_BUFFER = 60

class Receiver():
    def __init__(self, root, ip, port, buffer):
        self.root = root
        self.ip = ip
        self.port = port
        self.buffer = buffer
        self.dir = './'

    def close(self):
        self.root.quit()

    def setIp(self):
        global e
        self.port = int(e.get())
        e.destroy()
        setIpButton.destroy()

    def setDirectory(self):
        self.dir = askdirectory()
        if len(self.dir) > 0:
            receiveButton = Button(
                receiver.root, text='Receber arquivo', command=self.receiveFile)
            receiveButton.place(x=20, y=100)

    def receiveFile(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('', self.port))
        print("AGUARDANDO INICIO DO RECEBIMENTO")
        # tempo em que recebe primeiro pacote
        # com o número de pacotes totais e o nome do arquivo
        data, addr = s.recvfrom(FIRST_BUFFER)
        iniciot = time.time()
        print("PRIMEIRO PACOTE RECEBIDO")
        # Pegando o número de pacotes
        b = data[0:4]
        n = struct.unpack((">I").encode(), bytearray(b))[0]
        fileName = data[4:len(data)].decode('iso-8859-1')
        print("Tamanho do primeiro pacote: " + str(len(data)))
        print("Número de pacotes a serem recebidos: "+str(n))
        print("Nome do arquivo: "+fileName)
        print("addr: "+str(addr))
        # os.system("pause")

        dataTemp = []
        # Armazena temporariamente os dados numa lista, quando confirmar o recebimento da janela
        # Armazena na lista 'dataWrite', que é a lista definitiva
        dataWrite = []

        j = 0
        aux_i = 0
        i = 0
        while(i in range(n+1)):
            data = s.recv(BUFFER)
            # print("data >> "+str(data))
            b = data[0:4]

            # Transforma os 4 primeiros bytes do pacote em inteiro
            npackage = struct.unpack((">I").encode(), bytearray(b))[0]
            print("Numero do pacote: "+str(npackage) + " | I: " +
                  str(i) + " | Buffer data: "+str(len(data)))
            # os.system("pause")
            # Verifica se é o pacote que deve ser recebido
            if(npackage == i and len(data) == BUFFER):
                print("Recebido pacote numero: " + str(i))
                data_arq = data[4:len(data)]
                dataTemp.append(data_arq)
            elif(len(data) != BUFFER and npackage == n):
                print("Recebido ultimo pacote: " + str(i))
                data_arq = data[4:len(data)]
                dataTemp.append(data_arq)
            else:
                i = aux_i
                j = -1
                dataTemp.clear()
                print("I depois da notificação: "+str(i))
                s.sendto(("erro").encode(), addr)
                print("Erro notificado")

            if j == JANELA:
                j = -1
                aux_i = i
                print("Enviando confirmacao de recebimento")
                s.sendto(("confirmado").encode(), addr)
                print("Confirmacao enviada")

                for d in dataTemp:  # Transferindo os dados da lista temporaria para a lista definitiva
                    dataWrite.append(d)
                    # print(">>>PASSANDO PARA DATAWRITE")
                dataTemp.clear()

            i = i + 1
            j = j + 1

        # Se houver dados na lista temporaria, termina de pega-los
        for d in dataTemp:
            dataWrite.append(d)

        fimt = time.time()  # tempo em que todos os pacotes foram recebidos
        # Geracao de relatorios
        print("\n\n\n\n\n===========================================\n")
        print("Arquivo recebido com sucesso!")
        print("Tamanho do arquivo: " + str(n * BUFFER - 4) + " B")
        print("Numero de pacotes recebidos: " + str(n+1))
        print("Nome do arquivo: " + fileName)
        print("Duração do recebimento: "+str(fimt - iniciot) + " segundos.")
        print("Gravando em " + self.dir + "/" + fileName)
        # print("")
        file = open(self.dir+'/'+fileName, "wb")
        finalData = bytes(0)
        for i in range(len(dataWrite)):
            finalData = finalData + dataWrite[i]

        file.write(finalData)
        file.close()
        # s.close()


if __name__ == '__main__':
    # Definindo algumas constantes
    
    IP = '127.0.0.1'
    PORT = 6061

    # Armazena na estância da classe Receiver, receiver, as contantes definidas e o root para a janela
    window = Tk()
    receiver = Receiver(window, IP, PORT, BUFFER)

    # Configura layout da janela
    receiver.root.title("Troca de arquivos - Receiver")
    receiver.root.geometry("300x300")

    selectDirButton = Button(
        receiver.root, text='Selecionar diretorio', command=receiver.setDirectory)
    selectDirButton.place(x=20, y=40)

    setIpButton = Button(
        receiver.root, text='Configurar conexão', command=receiver.setIp)
    setIpButton.place(x=20, y=60)

    closeButton = Button(receiver.root, text='Fechar', command=receiver.close)
    closeButton.place(x=20, y=250)

    e = Entry(receiver.root)
    e.place(x=20, y=40)
    e.insert(END, str(PORT))
    e.focus()

    # Funçao que cria a janela
    receiver.root.mainloop()
