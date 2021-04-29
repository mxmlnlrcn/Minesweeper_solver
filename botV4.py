from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
import random
from selenium.webdriver.common.action_chains import ActionChains

path = "C:/Users/alpmala/Codes/python/buscaminas/chromedriver.exe"
driver = webdriver.Chrome(path)
driver.get('https://minesweeperonline.com/')

level = 'b'
iteraciones = 100

if level == 'b':
    level = 'beginner'
    h , w , b = 9, 9, 10
elif level == 'i':
    level = 'intermediate'
    h, w , b = 16 , 16 ,40
elif level == 'e':
    level = 'expert'
    h , w , b = 16 , 30 , 99
else:
    print('ERROR')

game = driver.find_element_by_id("options-link")
game.click()

level = driver.find_element_by_id(level)
level.click()

close = driver.find_element_by_id('options-close')
close.click()

win = 0
lose = 0

def explorar(x, y):
    bombas = 0
    vacios = 0
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            if (x+i >= 0 and y+j >= 0 and x+i < h and y+j < w):
                if data[x+i][y+j] == 9:
                    bombas += 1
                elif np.isnan(data[x+i][y+j]):
                    vacios += 1 
    return bombas , vacios

def setear(x,y,prob):
    result = False

    for i in [-1,0,1]:
        for j in [-1,0,1]:
            if (x+i >= 0 and y+j >= 0 and x+i < h and y+j < w):
                if np.isnan(data[x+i][y+j]):
                    matrix[x+i][y+j] = prob
                    if prob == 0:
                        posicion = str(x+i+1) + '_' + str(y+j+1)
                        driver.find_element_by_id(posicion).click()
                        try:
                            data[x+i][y+j] = int(driver.find_element_by_id(posicion).get_attribute('class')[-1:])
                        except:
                            return 0
                        if data[x+i][y+j] == 0:
                            return 0
                        else:
                            result = True
                    elif prob == 1:
                        posicion = str(x+i+1) + '_' + str(y+j+1)
                        elemento = driver.find_element_by_id(posicion)
                        ActionChains(driver).key_down(Keys.CONTROL).click(elemento).key_up(Keys.CONTROL).perform()
                        data[x+i][y+j] = 9
                        result = True
                    else:
                        result = False

    return result

def mapear():
    for i in range(h):
        for j in range(w):
            if  np.isnan(data[i][j]):
                posicion = str(i+1) + '_' + str(j+1)
                celda = driver.find_element_by_id(posicion).get_attribute('class').split(' ')[1]
                if celda != 'blank' and celda != 'bombflagged':
                    data[i][j] = int(celda[-1:])
                    matrix[i][j] = 0
                elif celda == 'bombflagged':
                    data[i][j] = 9
                    matrix[i][j] = 1


for ite in range(iteraciones):
    driver.find_element_by_id("face").click()
    Nbox = w*h
    prob = b/Nbox
    data = np.empty((h,w))
    data[:] = np.NaN
    matrix = np.zeros((h,w))
    matrix[:] = prob
    posw = random.randint(1,w)
    posh = random.randint(1,h)
    idbtn = str(posh) + '_' + str(posw)

    while True:
        btn = driver.find_element_by_id(idbtn) # identify the selected button
        btn.click() # click in that button
        value = btn.get_attribute('class').split(' ')[1] # get the name of this box
        if value == 'open0' or value == 'open8': # if we don't hit a bomb
            mapear()
            i= 0
            while i < h:
                j = 0
                while j < w:
                    cambio = False
                    if (~np.isnan(data[i][j]) and data[i][j] != 0 and data[i][j] != 9): # si la celda sigue sin ser pinchada y tampoco es 0
                        bombas , vacios = explorar(i, j) # explorar a su al rededor
                        if vacios != 0: # si tiene vecinos sin explorar
                            if bombas == data[i][j]: # si existe la misma cantidad de bombas que la pista de la celda
                                cambio = setear(i,j, 0) # setear las celdas vacias a 0
                                if cambio == 0: # si este set implicó apretar una celda sin riesgo y resulto abrir mas celdas
                                    mapear() # volver a mapear terreno
                                    cambio  = 'reset' # setear cambio como reset
                            elif (data[i][j]- bombas) == vacios: # si la cantidad de espacios vacios es igual a las bombas que faltan por reconocer
                                cambio = setear(i,j,1) # setear las celdas vacias a 1
                            else:
                                restantes = sum(sum(np.isnan(data))) # identificar las celdas que no han sido descubiertas
                                tens = driver.find_element_by_id('mines_tens').get_attribute('class')[-1:] # contar decenas de las minas
                                ones = driver.find_element_by_id('mines_ones').get_attribute('class')[-1:] # contar unidades de las minas
                                bombs = int(tens+ones) # unir decenas y unidades en un numero
                                prob = bombs/restantes # calcular la probabilidad de encontrar una mina en una celda aleatorea
                                cambio = setear(i,j, prob) # setear las celdas adyacentes como aleatoreas **********
                    j += 1

                    if cambio == True: # si se hizo un cambio en la matriz
                        i -= 1 if i != 0 else 0 # retroceder un espacio en i si es posible
                        j -= 1 if j != 0 else 0 # retroceder un espacio en j si es posible
                    elif cambio == 'reset': # si se hizo reset
                        if driver.find_element_by_id('face').get_attribute('class') == 'facewin':
                            break
                        i , j = 0, 0 # volver a recorrer toda la matriz

                if driver.find_element_by_id('face').get_attribute('class') == 'facewin':
                    break
                i += 1

            face = driver.find_element_by_id('face').get_attribute('class')
            if face != 'facewin': # si aun no gano y ya recorri toda la matriz
                print('Necesito probabilidades : clickeo una celda al azar')
                # calcular la porbabilidad real de la matriz
                submatrix = np.where(matrix == 0 , 1 , matrix)
                x , y = np.where(submatrix == submatrix.min())
                posh = x[random.randint(0,len(x)-1)]+1
                posw = y[random.randint(0,len(y)-1)]+1
                idbtn = str(posh) + '_' + str(posw)
                print(posh , posw)
            elif  face == 'facewin':
                print('You Won')
                win += 1 
                break

        elif value == 'bombdeath':
            print('Game Over')
            lose += 1
            break

        else:
            data[posh-1][posw-1] = int(value[-1:])
            matrix[posh-1][posw-1] = 0
            print('Necesito probabilidades : clickeo una celda al azar')
            # calcular la porbabilidad real de la matriz
            submatrix = np.where(matrix == 0 , 1 , matrix)
            x , y = np.where(submatrix == submatrix.min())
            posh = x[random.randint(0,len(x)-1)]+1
            posw = y[random.randint(0,len(y)-1)]+1
            idbtn = str(posh) + '_' + str(posw)
            print(posh , posw)

    driver.find_element_by_id("face").click()

total = win + lose
print(f"win rate: {win/total}")