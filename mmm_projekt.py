import numpy as np 
import matplotlib.pyplot as plt
from scipy.signal import square, sawtooth

#Symuluje blok dynamiczny 2. rzędu metodą Eulera do przodu z uwzględnieniem pochodnej wejścia
#rozważyć sytuacje gdy współczynniki w mianowniku = 0
def simulate_block_step(num, den, u_in, u_prev, y, dy, dt):
    b2, b1, b0 = den
    a1 = num[0] if len(num) > 1 else 0
    a0 = num[-1] if len(num) > 0 else 0

    du = (u_in - u_prev) / dt
    rhs = a1 * du + a0 * u_in
    ddy = (rhs - b1 * dy - b0 * y) / b2
    dy_new = dy + dt * ddy
    y_new = y + dt * dy_new
    return y_new, dy_new

# Parametry układu
a1, a0 = 1, 2
b2, b1, b0 = 1, 3, 2

c2, c1, c0 = 1, 1, 1
d2, d1, d0 = 1, 2, 1

# Parametry symulacji
dt = 0.01
t = np.arange(0, 10, dt)
f=0.5

# Wybór sygnału wejściowegop
print('Wybierz rodzaj sygnału:')
print('1 - Prostokątny')
print('2 - Trójkątny')
print('3 - Harmoniczny')


while True: 
    wybor = input('Podaj numer:') 
    if wybor == '1':
        # Sygnał prostokątny: 1 jeśli sin(2πft) >= 0, w przeciwnym razie 0
        u = np.where(np.sin(2 * np.pi * f * t) >= 0, 1, 0)
        break
    elif wybor == '2':
        u = sawtooth(2 * np.pi * f * t, 0.5)  # trójkątny
        break
    elif wybor == '3':
        u = np.sin(2 * np.pi * 1 * t) # harmoniczny
        break
    else:
        print('Nieprawidłowy wybór.')

plt.plot(t, u)
plt.show()