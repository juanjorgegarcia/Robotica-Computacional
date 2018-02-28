# -*- coding: utf-8 -*-
import cv2
import numpy as np
from matplotlib import pyplot as plt

#tamanho da caixa 36.5 cm
#distancia da caixa(l)=55.3
#hpix = 420px
# Para usar o vídeo
#cap = cv2.VideoCapture('hall_box_battery_mp2.mp4')

# As 3 próximas linhas são para usar a webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

box_height=36.5 #cm
init_distance=55
init_height_pix=420
init_distance_pix=(init_height_pix*init_distance)/box_height

def calc_distance(new_height_pix):
    
    new_distance_pix = (new_height_pix*init_distance_pix)/init_height_pix
    
    
    new_distance = (init_distance_pix*init_distance)/new_distance_pix
    
    return new_distance



def identifica_cor(frame):
    '''
    Segmenta o maior objeto cuja cor é parecida com cor_h (HUE da cor, no espaço HSV).
    '''

    # No OpenCV, o canal H vai de 0 até 179, logo cores similares ao 
    # vermelho puro (H=0) estão entre H=-8 e H=8. 
    # Veja se este intervalo de cores está bom
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    cor_menor = np.array([0, 50, 150])
    cor_maior = np.array([5, 255, 255])
    segmentado_cor = cv2.inRange(frame_hsv, cor_menor, cor_maior)

    # Será possível limpar a imagem segmentado_cor? 
    # Pesquise: https://docs.opencv.org/trunk/d9/d61/tutorial_py_morphological_ops.html
    kernel = np.ones((5,5),np.uint8)
    opening = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)

    # Encontramos os contornos na máscara e selecionamos o de maior área
    img_out, contornos, arvore = cv2.findContours(segmentado_cor.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    maior_contorno = None
    maior_contorno_area = 0


    cv2.drawContours(frame, contornos, -1, [255, 0, 255], 5)


    for cnt in contornos:
        area = cv2.contourArea(cnt)


        if area > maior_contorno_area:
            maior_contorno = cnt
            maior_contorno_area = area

    
    x,y,w,h = cv2.boundingRect(maior_contorno)
    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

        # cv2.putText(img, text, org, fontFace, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
    

    
    rect = cv2.minAreaRect(maior_contorno)
    #print(rect[1])
    w1,h1=rect[1]
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img,[box],0,(0,0,255),2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    #print(rect[1])
    if h1 > w1:
        #print("caixa ta em pe")
        cv2.putText(frame,'Distancia: {}cm'.format(calc_distance(h1)),(100,40), font,1,(255,255,255),3,cv2.LINE_AA)
    else:
        #print("caixa ta deitada")
        cv2.putText(frame,'Distancia: {}cm'.format(calc_distance(w1)),(100,40), font,1,(255,255,255),3,cv2.LINE_AA)

        
    # Encontramos o centro do contorno fazendo a média de todos seus pontos.
    if not maior_contorno is None :
        cv2.drawContours(frame, [maior_contorno], -1, [0, 0, 255], 5)
        maior_contorno = np.reshape(maior_contorno, (maior_contorno.shape[0], 2))
        media = maior_contorno.mean(axis=0)
        media = media.astype(np.int32)
        cv2.circle(frame, tuple(media), 5, [0, 255, 0])
    else:
        media = (0, 0)

    cv2.imshow('', frame)
    #cv2.imshow('imagem in_range', segmentado_cor)
    cv2.waitKey(1)

    centro = (frame.shape[0]//2, frame.shape[1]//2)

    return media, centro


while(True):
    # Capture frame-by-frame
    #print("Novo frame")
    ret, frame = cap.read()


    img = frame.copy()

    media, centro = identifica_cor(img)

    #More drawing functions @ http://docs.opencv.org/2.4/modules/core/doc/drawing_functions.html
  

    # Display the resulting frame
    #cv2.imshow('original',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    #print("No circles were found")
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
