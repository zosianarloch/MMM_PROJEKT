import numpy as np 
import matplotlib.pyplot as plt
from scipy.signal import sawtooth

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

def simulator():
    # Parametry obiektu
    a1, a0 = 1, 2
    b2, b1, b0 = 1, 3, 2

    # Parametry sterownika
    c2, c1, c0 = 1, 1, 1
    d2, d1, d0 = 1, 2, 1

    # Czas symulacji
    dt = 0.01
    t = np.arange(0, 10, dt)
    f = 0.5

    # Wybór sygnału wejściowego
    print("Wybierz rodzaj sygnału:")
    print("1 - Prostokątny")
    print("2 - Trójkątny")
    print("3 - Harmoniczny")

    while True: 
        wybor = input('Podaj numer:') 
        if wybor == '1':
            # Sygnał prostokątny: 1 jeśli sin(2πft) >= 0, w przeciwnym razie -1
            u = np.where(np.sin(2 * np.pi * f * t) >= 0, 1, -1)
            break
        elif wybor == '2':
            u = sawtooth(2 * np.pi * f * t, 0.5)  # trójkątny
            break
        elif wybor == '3':
            u = np.sin(2 * np.pi * 1 * t) # harmoniczny
            break
        else:
            print('Nieprawidłowy wybór.')

    # Inicjalizacja wektorów i stanów
    y = np.zeros_like(t)        # wyjście układu
    u_c = np.zeros_like(t)      # wyjście sterownika

    dy_obj = 0                  # pochodna obiektu
    dy_ctrl = 0                 # pochodna sterownika
    y_obj = 0                   # aktualna wartość wyjścia obiektu
    y_ctrl = 0                  # aktualna wartość wyjścia sterownika (sygnał sterujący)
    e_prev = 0                  # błąd sterowania
    u_c_prev = 0                # błąd sterowania z poprzedniego kroku

    # Symulacja układu zamkniętego
    for i in range(len(t) - 1):
        e = u[i] - y[i]  # ujemne sprzężenie zwrotne

        # Sterownik
        y_ctrl, dy_ctrl = simulate_block_step(
            [c2, c1, c0], [d2, d1, d0],
            e, e_prev,
            y_ctrl, dy_ctrl, dt
        )     
        # sygnał sterujący i jego pochodna
        u_c[i+1] = y_ctrl
        e_prev = e

        # Obiekt
        y_obj, dy_obj = simulate_block_step(
            [a1, a0], [b2, b1, b0],
            u_c[i+1], u_c_prev,
            y_obj, dy_obj, dt
        )   
        # sygnał wyjściowy i jego pochodna
        y[i+1] = y_obj
        u_c_prev = u_c[i+1]

    # Wykres
    plt.figure()
    plt.plot(t, u, 'r--', label='Sygnał zadany (u)')
    plt.plot(t, y, 'b', label='Wyjście układu (y)')
    plt.xlabel('Czas [s]')
    plt.ylabel('Amplituda')
    plt.title('Układ z ujemnym sprzężeniem zwrotnym')
    plt.grid(True)
    plt.legend()
    plt.show()

# Uruchomienie
if __name__ == "__main__":
    simulator()