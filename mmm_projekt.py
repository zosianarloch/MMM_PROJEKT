import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from scipy.signal import sawtooth

def simulate_block_step(num, den, u_in, u_prev, y, dy, dt):
    """Symuluje blok dynamiczny 2. rzędu metodą Eulera do przodu z uwzględnieniem pochodnej wejścia"""
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

    den = b2, b1, b0 
    num = a1, a0 

    # Parametry sterownika
    c2, c1, c0 = 1, 1, 1
    d2, d1, d0 = 1, 2, 1

    licz = c2, c1, c0
    mian = d2, d1, d0

    # Czas symulacji
    dt = 0.01
    t = np.arange(0, 10, dt)
    f = 0.5

    # Domyślny sygnał wejściowy i odpowiedź
    default_label = 'Prostokątny'
    u = generate_signal(f, t, default_label)
    y = system_response(num, den, licz, mian, u, t, dt)


    # Tworzenie okna i osi wykresu
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.3)  
    input_line, = ax.plot(t, u, 'r--', label='Sygnał wejściowy')
    output_line, = ax.plot(t, y, 'b', label='Odpowiedź układu')
    ax.legend()
    ax.set_title('Symulacja układu')
    ax.set_xlabel('Czas [s]')
    ax.set_ylabel('Amplituda')
    ax.grid(True)
    # Dodanie radio buttons
    ax_radio = plt.axes([0.05, 0.4, 0.185, 0.2])  # [left, bottom, width, height]
    radio = RadioButtons(ax_radio, ['Prostokątny', 'Trójkątny', 'Sinusoidalny'])

    # Funkcja aktualizująca wykres po kliknięciu
    def update(label):
        u = generate_signal(f, t, label)
        y = system_response(num, den, licz, mian, u, t, dt)
        input_line.set_ydata(u)
        output_line.set_ydata(y)
        fig.canvas.draw_idle()

    
    radio.on_clicked(update)

    plt.show()

def generate_signal(f, t, wybor):
        # Wybór sygnału wejściowego
        """print("Wybierz rodzaj sygnału:")
        print("1 - Prostokątny")
        print("2 - Trójkątny")
        print("3 - Harmoniczny")"""
        #while True:
            #wybor = input("Podaj numer: ")
        if wybor == 'Prostokątny':
            # Sygnał prostokątny: 1 jeśli sin(2πft) >= 0, w przeciwnym razie -1
            return np.where(np.sin(2 * np.pi * f * t) >= 0, 1, -1)
        elif wybor == 'Trójkątny':
            return sawtooth(2 * np.pi * f * t, 0.5)
        elif wybor == 'Sinusoidalny':
            return np.sin(2 * np.pi * f * t)
        else:
            raise ValueError("Nieznany typ sygnału: " + wybor)

def system_response(num, den, licz, mian, u, t, dt):
    # Inicjalizacja wektorów i stanów
    y = np.zeros_like(t)        # wyjście układu
    u_c = np.zeros_like(t)      # wyjście sterownika (sygnał sterujący)
    b2, b1, b0 = den
    a1, a0 = num
    c2, c1, c0 = licz
    d2, d1, d0 = mian

    dy_obj = 0                  # pochodna wyjścia obiektu
    dy_ctrl = 0                 # pochodna wyjścia sterownika (sygnał sterujący)
    y_obj = 0                   # aktualna wartość wyjścia obiektu
    y_ctrl = 0                  # aktualna wartość wyjścia sterownika (sygnał sterujący)
    e_prev = 0                  # błąd sterowania z poprzedniego kroku
    u_c_prev = 0                # sygnał sterujący z poprzedniego kroku

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
    return y

# Uruchomienie
if __name__ == "__main__":
    simulator()