import numpy as np 
import matplotlib.pyplot as plt
from scipy.signal import square, sawtooth

# Parametry układu
a1, a0 = 1, 2
b2, b1, b0 = 1, 3, 2

c2, c1, c0 = 1, 1, 1
d2, d1, d0 = 1, 2, 1

# Parametry symulacji
dt = 0.01
t = np.arange(0, 10, dt)

# Wybór sygnału wejściowegop
print('Wybierz rodzaj sygnału:')
print('1 - Prostokątny')
print('2 - Trójkątny')
print('3 - Harmoniczny')


while True: 
    wybor = input('Podaj numer:') 
    if wybor == '1':
        u = square(2 * np.pi * 0.5 * t) # prostokątny
        break
    elif wybor == '2':
        u = sawtooth(2 * np.pi * 0.5 * t, 0.5)  # trójkątny
        break
    elif wybor == '3':
        u = np.sin(2 * np.pi * 1 * t) # harmoniczny
        break
    else:
        print('Nieprawidłowy wybór.')


