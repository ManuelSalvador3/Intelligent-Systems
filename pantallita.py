import pickle

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QStyle, QSizePolicy, QFileDialog
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl

import speech_recognition as sr

import nltk
import moviepy.editor as mp
from pydub.utils import make_chunks

import os
from pydub import AudioSegment
import unidecode






video = ""

class Window(QWidget):
    def __init__(self, app):
        super().__init__()



        self.app = app
        self.setWindowTitle("Thinking Out Loud - Práctica 1 - Sistemas Inteligentes")
        self.setGeometry(800, 200, 1800, 1000) #650, 100, 1100, 900
        self.setWindowIcon(QIcon('player.png'))


        p = self.palette()
        p.setColor(QPalette.Window, Qt.white)
        self.setPalette(p)

        self.init_ui()

        self.show()


    def init_ui(self):

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videowidget = QVideoWidget()

        openBtn = QPushButton('Open Video')
        openBtn.clicked.connect(self.open_file)

        self.guardarCambios = QPushButton('GUARDAR CAMBIOS')
        self.guardarCambios.setDisabled(True)

        self.sugerirCodigos = QPushButton('SUGERIR CÓDIGOS')
        self.sugerirCodigos.setDisabled(True)

        self.guardarCambios.setStyleSheet('QPushButton {background-color: #F64F1A; color: black; font-weight: bold;}')
        self.sugerirCodigos.setStyleSheet('QPushButton {background-color: #F64F1A; color: black; font-weight: bold;}')
        self.guardarCambios.clicked.connect(self.guardarCambiosFunc)#TODO pasarle la funcion
        self.sugerirCodigos.clicked.connect(self.aplicarCodigosDeUsuario)#TODO pasarle la funcion

        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # self.label = QtWidgets.QTextEdit()
        # self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.textbox = QtWidgets.QTextEdit()
        self.textbox.setPlainText("Selecciona un video para iniciar el proceso, gracias.\nMientras no haya video, los Botones Inferiores estarán deshabilitados")
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)
        self.textbox.setFixedWidth(1800)
        self.textbox.setFixedHeight(400)

        self.lista = []
        self.lista2 = []

        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        secondHboxLayout = QVBoxLayout()
        secondHboxLayout.setContentsMargins(10, 10, 10, 10)

        thirdHboxLayout = QHBoxLayout()
        thirdHboxLayout.setContentsMargins(10, 10, 10, 10)


        hboxLayout.addWidget(openBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(self.slider)
        secondHboxLayout.addWidget(self.textbox)
        thirdHboxLayout.addWidget(self.guardarCambios)
        thirdHboxLayout.addWidget(self.sugerirCodigos)

        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addLayout(secondHboxLayout)
        vboxLayout.addLayout(thirdHboxLayout)
        #vboxLayout.addWidget(self.label)

        self.setLayout(vboxLayout)

        self.mediaPlayer.setVideoOutput(videowidget)

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)
            self.video_to_audio(filename)
            self.lista = self.transcription("gopro.wav")
            if len(self.lista) != 0:
                print(len(self.lista))
                print(self.lista)
                for lista in self.lista:
                    for word in lista:
                        self.lista2.append(word)
                        #lista2.write(word + " ")
                    #file2.write('%s\n' % lista)
            #self.textbox.setText("")
            self.rellenarLabel()


    def guardarCambiosFunc(self):
        texto_edit = self.textbox.toPlainText()
        #ficheroNuevo = open("temporal.txt", "r")
        #contenido = ficheroNuevo.read()
        #print(contenido)
        pathGuardarModelo = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
        print(pathGuardarModelo)
        texto_edit = unidecode.unidecode(texto_edit)
        with open(pathGuardarModelo+'/Transcripcion.txt', 'wb') as f:
            pickle.dump(texto_edit, f)

        #ficheroNuevo.close()


    def video_to_audio(self, path):
        miVideo = mp.VideoFileClip(path)
        hola = miVideo.audio.write_audiofile("gopro.wav")
        return hola


    def transcription(self, path):

        myaudio = AudioSegment.from_file(path, "wav")
        chunk_length_ms = 26000
        chunks = make_chunks(myaudio, chunk_length_ms)

        folder_name = "audio-chunks"

        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

        for i, chunk in enumerate(chunks):
            chunk_name = os.path.join(folder_name, f"chunk{i}.wav")
            chunk.export(chunk_name, format="wav")
        print("Chunks exportados correctamente...")
        r = sr.Recognizer()
        lista_chunks = []
        for i, audio_chunk in enumerate(chunks, start=0):  # Antes era 1

            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")

            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                try:
                    text = r.recognize_google(audio_listened, language='es-ES')
                    print('chunk', i)
                    tokenizar = nltk.word_tokenize(text)  # lista
                    y = 0
                    while y < len(tokenizar):
                        if tokenizar[y] == 'giro' and tokenizar[y + 1] == 'derecha':
                            tokenizar.insert(y + 2, '<SW-TL-R>')
                        elif tokenizar[y] == 'giro' and tokenizar[y + 1] == 'izquierda':
                            tokenizar.insert(y + 2, '<SW-TL-L>')
                        elif tokenizar[y] == 'subo' and tokenizar[y + 1] == 'marcha':
                            tokenizar.insert(y + 2, '<GU>')
                        elif tokenizar[y] == 'bajo' and tokenizar[y + 1] == 'marcha':
                            tokenizar.insert(y + 2, '<GD>')
                        elif tokenizar[y] == 'bajo' and tokenizar[y + 1] == 'de' and tokenizar[y + 2] == 'marcha':
                            tokenizar.insert(y + 3, '<GD>')
                        elif tokenizar[y] == 'intermitente' and tokenizar[y + 1] == 'izquierda':
                            tokenizar.insert(y + 2, '<LB-ON>')
                        elif tokenizar[y] == 'intermitente' and tokenizar[y + 1] == 'derecha':
                            tokenizar.insert(y + 2, '<RB-ON>')
                        elif tokenizar[y] == 'piso' and tokenizar[y + 1] == 'embrague':
                            tokenizar.insert(y + 2, '<G-ON>')
                        elif tokenizar[y] == 'suelto' and tokenizar[y + 1] == 'embrague':
                            tokenizar.insert(y + 2, '<G-OFF>')
                        elif tokenizar[y] == 'piso' and tokenizar[y + 1] == 'acelerador':
                            tokenizar.insert(y + 2, '<T-ON>')
                        elif tokenizar[y] == 'suelto' and tokenizar[y + 1] == 'acelerador':
                            tokenizar.insert(y + 2, '<T-OFF>')
                        elif tokenizar[y] == 'piso' and tokenizar[y + 1] == 'freno':
                            tokenizar.insert(y + 2, '<B-ON>')
                        elif tokenizar[y] == 'piso' and tokenizar[y + 1] == 'frenos':
                            tokenizar.insert(y + 2, '<B-ON>')
                        elif tokenizar[y] == 'suelto' and tokenizar[y + 1] == 'freno':
                            tokenizar.insert(y + 2, '<B-OFF>')
                        ##CODIGOS DE ESTIMULOS
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'frente':
                            tokenizar.insert(y + 2, '<FV>')
                        elif tokenizar[y] == 'mira' and tokenizar[y + 1] == 'enfrente':
                            tokenizar.insert(y + 2, '<FV>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'retrovisor' and tokenizar[
                            y + 2] == 'central':
                            tokenizar.insert(y + 3, '<FV-MIRROR>')
                        elif tokenizar[y] == 'mira' and tokenizar[y + 1] == 'retrovisor' and tokenizar[
                            y + 2] == 'central':
                            tokenizar.insert(y + 3, '<FV-MIRROR>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'central':
                            tokenizar.insert(y + 2, '<FV-MIRROR>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'izquierda':
                            tokenizar.insert(y + 2, '<LV>')
                        elif tokenizar[y] == 'retrovisor' and tokenizar[y + 1] == 'izquierda':
                            tokenizar.insert(y + 2, '<LV-MIRROR>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'retrovisor' and tokenizar[y + 2] == 'izquierda':
                            tokenizar.insert(y + 3, '<LV-MIRROR>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'frente' and tokenizar[y + 2] == 'izquierda':
                            tokenizar.insert(y + 3, '<FLV>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'derecha':
                            tokenizar.insert(y + 2, '<RV>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'retrovisor' and tokenizar[
                            y + 2] == 'derecha':
                            tokenizar.insert(y + 3, '<RV-MIRROR>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'frente' and tokenizar[y + 2] == 'derecha':
                            tokenizar.insert(y + 3, '<FRV>')
                        elif tokenizar[y] == 'miro' and tokenizar[y + 1] == 'detras':
                            tokenizar.insert(y + 2, '<BV>')
                            #LIMPIEZA TEXTO
                        elif tokenizar[y] == '[':
                            tokenizar.insert('')
                        elif tokenizar[y] == ']':
                            tokenizar.insert('')
                        elif tokenizar[y] == ',':
                            tokenizar.insert(' ')
                        elif tokenizar[y] == '\'':
                            tokenizar.insert('')
                        y = y + 1

                    lista_chunks.insert(i, tokenizar)

                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text} "
        x = 0
        while x < len(lista_chunks):
            print('Chunk' + str(x) + ': ' + str(lista_chunks[x]))
            print('\n\n')
            x = x + 1

        self.guardarCambios.setDisabled(False)
        self.sugerirCodigos.setDisabled(False)

        return lista_chunks

    
    def aplicarCodigosDeUsuario(self):
        texto = self.textbox.toPlainText()
        listatexto = list(texto.split())
        # print(listatexto)
        # print(listatexto[5])
        y= 0
        while y<len(listatexto)-3:
            #GIRO DERECHA
            if listatexto[y] == 'giro' and listatexto[y + 1] == 'derecha' and listatexto[y+2] == '<SW-TL-R>':
                print("Codigo GIRO DERECHA ya existe")
            elif listatexto[y] == 'giro' and listatexto[y + 1] == 'derecha':
                listatexto.insert(y + 2, '<SW-TL-R>')

            #GIRO IZQUIERDA5
            elif listatexto[y] == 'giro' and listatexto[y + 1] == 'izquierda' and listatexto[y + 2] == '<SW-TL-L>':
                print("Codigo GIRO IZQUIERDA ya existe")
            elif listatexto[y] == 'giro' and listatexto[y + 1] == 'izquierda':
                listatexto.insert(y + 2, '<SW-TL-L>')

            #SUBO MARCHA
            elif listatexto[y] == 'subo' and listatexto[y + 1] == 'marcha' and listatexto[y+2] == '<GU>':
                print("Codigo SUBO MARCHA ya existe")
            elif listatexto[y] == 'subo' and listatexto[y + 1] == 'marcha':
                listatexto.insert(y + 2, '<GU>')

            #BAJO MARCHA
            elif listatexto[y] == 'bajo' and listatexto[y + 1] == 'marcha' and listatexto[y + 2] == '<GD>':
                print("Codigo BAJO MARCHA ya existe")
            elif listatexto[y] == 'bajo' and listatexto[y + 1] == 'marcha':
                listatexto.insert(y + 2, '<GD>')

            #BAJO DE MARCHA
            elif listatexto[y] == 'bajo' and listatexto[y + 1] == 'de' and listatexto[y + 2] == 'marcha' and listatexto[y + 3] == '<GD>':
                print("Codigo BAJO DE MARCHA ya existe")
            elif listatexto[y] == 'bajo' and listatexto[y + 1] == 'de' and listatexto[y + 2] == 'marcha':
                listatexto.insert(y + 3, '<GD>')

            #INTERMITENTE IZQUIERDA
            elif listatexto[y] == 'intermitente' and listatexto[y + 1] == 'izquierda' and listatexto[y+2] == '<LB-ON>':
                print("Codigo INTERMITENTE IZQUIERDA ya existe")
            elif listatexto[y] == 'intermitente' and listatexto[y + 1] == 'izquierda':
                listatexto.insert(y + 2, '<LB-ON>')

            #INTERMITENTE DERECHA
            elif listatexto[y] == 'intermitente' and listatexto[y + 1] == 'derecha' and listatexto[y + 2] == '<RB-ON>':
                print("Codigo INTERMITENTE DERECHA ya existe")
            elif listatexto[y] == 'intermitente' and listatexto[y + 1] == 'derecha':
                listatexto.insert(y + 2, '<RB-ON>')

            #PISO EMBRAGUE
            elif listatexto[y] == 'piso' and listatexto[y + 1] == 'embrague' and listatexto[y + 2] == '<G-ON>':
                print("Codigo PISO EMBRAGUE ya existe")
            elif listatexto[y] == 'piso' and listatexto[y + 1] == 'embrague':
                listatexto.insert(y + 2, '<G-ON>')
            
            #SUELTO EMBRAGUE
            elif listatexto[y] == 'suelto' and listatexto[y + 1] == 'embrague' and listatexto[y + 2] == '<G-OFF>':
                print("Codigo SUELTO EMBRAGUE ya existe")
            elif listatexto[y] == 'suelto' and listatexto[y + 1] == 'embrague':
                listatexto.insert(y + 2, '<G-OFF>')

            #PISO ACELERADOR
            elif listatexto[y] == 'piso' and listatexto[y + 1] == 'acelerador' and listatexto[y + 2] == '<T-ON>':
                print("Codigo PISO ACELERADOR ya existe")
            elif listatexto[y] == 'piso' and listatexto[y + 1] == 'acelerador':
                listatexto.insert(y + 2, '<T-ON>')
            
            #SUELTO ACELERADOR
            elif listatexto[y] == 'suelto' and listatexto[y + 1] == 'acelerador' and listatexto[y + 2] == '<T-OFF>':
                print("Codigo SUELTO ACELERADOR ya existe")
            elif listatexto[y] == 'suelto' and listatexto[y + 1] == 'acelerador':
                listatexto.insert(y + 2, '<T-OFF>')

            #PISO FRENO
            elif listatexto[y] == 'piso' and listatexto[y + 1] == 'freno' and listatexto[y + 2] == '<B-ON>':
                print("Codigo PISO FRENO ya existe")
            elif listatexto[y] == 'piso' and listatexto[y + 1] == 'freno':
                listatexto.insert(y + 2, '<B-ON>')
            
            #SUELTO FRENO
            elif listatexto[y] == 'suelto' and listatexto[y + 1] == 'freno' and listatexto[y + 2] == '<B-OFF>':
                print("Codigo SUELTO FRENO ya existe")
            elif listatexto[y] == 'suelto' and listatexto[y + 1] == 'freno':
                listatexto.insert(y + 2, '<B-OFF>')

            ##CODIGOS DE ESTIMULOS
            #MIRO FRENTE
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'frente' and listatexto[y + 2] == '<FV>':
                print("Codigo MIRO FRENTE ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'frente':
                listatexto.insert(y + 2, '<FV>')
            elif listatexto[y] == 'mira' and listatexto[y + 1] == 'enfrente' and listatexto[y + 2] == '<FV>':
                print("Codigo MIRA ENFRENTE ya existe")
            elif listatexto[y] == 'mira' and listatexto[y + 1] == 'enfrente':
                listatexto.insert(y + 2, '<FV>')

            #Miro 
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'retrovisor' and listatexto[y + 2] == 'central' and listatexto[y + 3] == '<FV-MIRROR>':
                print("Codigo MIRO RETROVISOR CENTRAL ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'retrovisor' and listatexto[y + 2] == 'central':
                listatexto.insert(y + 3, '<FV-MIRROR>')

            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'central' and listatexto[y + 2] == '<FV-MIRROR>':
                print("Codigo MIRO RETROVISOR CENTRAL ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'central':
                listatexto.insert(y + 2, '<FV-MIRROR>')
            
            #MIRO IZQUIERDA
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'izquierda' and listatexto[y + 2] == '<LV>':
                print('Codigo MIRO IZQUIERDA ya existe')
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'izquierda':
                listatexto.insert(y + 2, '<LV>')

            #RETROVISOR IZQUIERDA
            elif listatexto[y] == 'retrovisor' and listatexto[y + 1] == 'izquierda' and listatexto[y + 2] == '<LV-MIRROR>':
                print("Codigo RETROVISOR IZQUIERDA ya existe")
            elif listatexto[y] == 'retrovisor' and listatexto[y + 1] == 'izquierda':
                listatexto.insert(y + 2, '<LV-MIRROR>')

            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'retrovisor' and listatexto[y + 2] == 'izquierda' and listatexto[y + 3] == 'LV-MIRROR>':
                print("Codigo MIRO RETROVISOR IZQUIERDA ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'retrovisor' and listatexto[y + 2] == 'izquierda':
                listatexto.insert(y + 3, '<LV-MIRROR>')

            #FRENTE IZQUIERDA
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'frente' and listatexto[y + 2] == 'izquierda' and listatexto[y + 3] == '<FLV>':
                print("Codigo MIRO FRENTE IZQUIERDA ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'frente' and listatexto[y + 2] == 'izquierda':
                listatexto.insert(y + 3, '<FLV>')

            #FRENTE DERECHA
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'derecha' and listatexto[y + 2] == '<RV>':
                print("Codigo MIRO DERECHA ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'derecha':
                listatexto.insert(y + 2, '<RV>')

            #RETROVISOR DERECHO
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'retrovisor' and listatexto[y + 2] == 'derecha' and listatexto[y + 3] == '<RV-MIRROR>':
                print("Codigo MIRO RETROVISOR DERECHA ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'retrovisor' and listatexto[y + 2] == 'derecha':
                listatexto.insert(y + 3, '<RV-MIRROR>')
            
            #FRENTE DERECHA
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'frente' and listatexto[y + 2] == 'derecha' and listatexto[y + 3] == '<FRV>':
                print("Codigo MIRO FRENTE DERECHA ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'frente' and listatexto[y + 2] == 'derecha':
                listatexto.insert(y + 3, '<FRV>')

            #MIRO DETRAS
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'detras' and listatexto[y + 2] == '<BV>':
                print("Codigo MIRO DETRAS ya existe")
            elif listatexto[y] == 'miro' and listatexto[y + 1] == 'detras':
                listatexto.insert(y + 2, '<BV>')

            #LIMPIEZA TEXTO
            elif listatexto[y] == '[':
                listatexto.insert('')
            elif listatexto[y] == ']':
                listatexto.insert('')
            elif listatexto[y] == ',':
                listatexto.insert(' ')
            elif listatexto[y] == '\'':
                listatexto.insert('')
            y = y + 1

            #listatexto es todo mi texto nuevo. Lo paso a string y lo pongo en la interfaz
        textoFinal = " ".join(listatexto)
        self.textbox.setText(textoFinal)
        
        return textoFinal

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()#TODO STOP
            print('STOPPED VIDEO')
        else:
            #self.rellenarLabel()
            self.app.processEvents()
            self.mediaPlayer.play()
            print('VIDEO PLAYING')

    def rellenarLabel(self):
        texto = " ".join(self.lista2)
        self.textbox.setText(texto)

    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)

            )

        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)

            )

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def handle_errors(self):
        self.playBtn.setEnabled(False)
        #self.label.setText("Error: " + self.mediaPlayer.errorString())


app = QApplication(sys.argv)
window = Window(app)
sys.exit(app.exec_())

