import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons

#zastosowanie rozwinięcia Taylora i metody Eulera
def simulate_block_step(num, den, u_now, u_prev, u_prev2, y, dy, dt): 
    MAX_VALUE = 1e6
    b2, b1, b0 = den
    a2 = num[0] if len(num) == 3 else 0
    a1 = num[-2] if len(num) >= 2 else 0
    a0 = num[-1] if len(num) >= 1 else 0
    #pochodne wejścia
    du = (u_now - u_prev) / dt if a1 != 0 else 0    
    ddu = (u_now - 2 * u_prev + u_prev2) / dt**2 if a2 != 0 else 0
    rhs = a2 * ddu + a1 * du + a0 * u_now
    rhs = np.clip(rhs, -MAX_VALUE, MAX_VALUE)
    #pochodne wyjśćia
    if abs(b2) > 1e-8:  
        ddy = (rhs - b1 * dy - b0 * y) / b2
        dy_new = dy + dt * ddy
        y_new = y + dt * dy_new
    elif abs(b1) > 1e-8: #przypadek b2=0
        dy_new = (rhs - b0 * y) / b1
        y_new = y + dt * dy_new
    elif abs(b0) > 1e-8:  #przypadek b2=0, b1=0
        y_new = rhs / b0
        dy_new = 0
    else:
        raise ZeroDivisionError("Wszystkie współczynniki mianownika = 0 – brak rozwiązania.")
    #ograniczenia dla wartości odpowiedzi
    y_new = np.clip(y_new, -MAX_VALUE, MAX_VALUE)     
    dy_new = np.clip(dy_new, -MAX_VALUE, MAX_VALUE)
    return y_new, dy_new

#generowanie sygnału
def generate_signal(f, A, t, typ):    
    if typ == 'Prostokątny':
        return A * np.where(np.sin(2 * np.pi * f * t) >= 0, 1, -1)
    elif typ == 'Trójkątny':
        return A * (2 * np.abs(2 * ((t * f) % 1) - 1) - 1)
    elif typ == 'Sinusoidalny':
        return A * np.sin(2 * np.pi * f * t)
    else:
        raise ValueError("Nieznany typ sygnału: " + typ)

# połączenie układu (sygnałów z sterownika )
def system_response(num, den, licz, mian, u, t, dt):
    # inicjalizacja zmiennych
    y = np.zeros_like(t)
    u_c = np.zeros_like(t)
    dy_obj = dy_ctrl = y_obj = y_ctrl = 0
    e_prev = e_prev2 = u_c_prev = u_c_prev2 = 0
    # układ w sprzężeniu zwrotnym
    for i in range(1, len(t) - 1):
        e = u[i] - y[i]    # uchyb
        y_ctrl, dy_ctrl = simulate_block_step(licz, mian, e, e_prev, e_prev2, y_ctrl, dy_ctrl, dt)  #sygnałze sterownika
        u_c[i + 1] = y_ctrl 
        e_prev2 = e_prev 
        e_prev = e
        y_obj, dy_obj = simulate_block_step(num, den, u_c[i + 1], u_c_prev, u_c_prev2, y_obj, dy_obj, dt) #sygnał z obiektu
        y[i + 1] = y_obj 
        u_c_prev2 = u_c_prev
        u_c_prev = u_c[i + 1]
    return y

def simulator_with_combined_and_separate_plots():
    dt = 0.01
    t = np.arange(0, 10, dt)
    # parametry default        
    f = 0.5                    
    A = 1.0
    signal_type = 'Prostokątny'     
    param_defaults = {
        'a1': 1.0, 'a0': 2.0,
        'b2': 1.0, 'b1': 3.0, 'b0': 2.0,
        'c2': 1.0, 'c1': 1.0, 'c0': 1.0,
        'd2': 1.0, 'd1': 2.0, 'd0': 1.0,
    }
    # rozkład okna wykresu
    fig = plt.figure(figsize=(13, 7))     
    gs = fig.add_gridspec(6, 4)
    ax_combined = fig.add_subplot(gs[0:2, 1:])
    ax_input = fig.add_subplot(gs[2:4, 1:])
    ax_output = fig.add_subplot(gs[4:6, 1:])
    sliders = {}
    y_pos = 0.65
    # slidery dla parametrów transmitancji
    fig.text(0.01, 0.7, "Parametry transmitancji", fontsize=12, fontweight='bold')
    for param in param_defaults:
        ax_slider = plt.axes([0.03, y_pos, 0.25, 0.025])
        sliders[param] = Slider(ax_slider, param, 0.0, 4.0, valinit=param_defaults[param])
        y_pos -= 0.035

    # slidery dla sygnału
    fig.text(0.01, 0.18, "Parametry sygnału wejściowego", fontsize=12, fontweight='bold')
    ax_slider_f = plt.axes([0.035, 0.08, 0.25, 0.03])
    slider_f = Slider(ax_slider_f, 'f[Hz]', 0.0, 10.0, valinit=f)

    ax_slider_A = plt.axes([0.035, 0.13, 0.25, 0.03])
    slider_A = Slider(ax_slider_A, 'A[V]', 0.0, 10.0, valinit=A)
    # radio buttons
    fig.text(0.01, 0.9, "Wybór sygnału wejściowego", fontsize=12, fontweight='bold')
    ax_radio = plt.axes([0.01, 0.75, 0.25, 0.12])
    radio = RadioButtons(ax_radio, ['Prostokątny', 'Trójkątny', 'Sinusoidalny'])

    u = generate_signal(f, A, t, signal_type)
    y = system_response(
        [param_defaults['a1'], param_defaults['a0']],
        [param_defaults['b2'], param_defaults['b1'], param_defaults['b0']],
        [param_defaults['c2'], param_defaults['c1'], param_defaults['c0']],
        [param_defaults['d2'], param_defaults['d1'], param_defaults['d0']],
        u, t, dt
    )
    
    #wykresy
    line_u_combined, = ax_combined.plot(t, u, 'r--', label='Sygnał wejściowy')
    line_y_combined, = ax_combined.plot(t, y, 'b', label='Odpowiedź układu')
    line_u_separate, = ax_input.plot(t, u, 'r', label='Sygnał wejściowy')
    line_y_separate, = ax_output.plot(t, y, 'b', label='Odpowiedź układu')
    for ax in [ax_combined, ax_input, ax_output]:
        ax.grid(True)
        ax.legend()

    ax_combined.set_title("Symulacja układu")
    ax_output.set_xlabel("Czas [s]")
    ax_combined.set_ylabel("Amplituda [V]")
    ax_output.set_ylabel("Amplituda [V]")
    ax_input.set_ylabel("Amplituda [V]")

    #zmiany parametrów i sygnału wejściowego
    def update_plot(_):
        # pobieranie parametrów sygnału wejściowego
        f_val = slider_f.val
        A_val = slider_A.val
        typ = radio.value_selected
        u = generate_signal(f_val, A_val, t, typ)
        # pobieranie współczynników transmitancji
        num = [sliders['a1'].val, sliders['a0'].val]
        den = [sliders['b2'].val, sliders['b1'].val, sliders['b0'].val]
        licz = [sliders['c2'].val, sliders['c1'].val, sliders['c0'].val]
        mian = [sliders['d2'].val, sliders['d1'].val, sliders['d0'].val]
        # błąd dzielenia przez zero
        if all(p == 0 for p in den) or all(p == 0 for p in mian):
            ax_combined.set_title("Błąd: Wszystkie współczynniki mianownika = 0", color='red')
            line_y_combined.set_ydata([np.nan] * len(t))
            line_y_separate.set_ydata([np.nan] * len(t))
            return
        y = system_response(num, den, licz, mian, u, t, dt)
        # aktualizacja danych na wykresach
        for l in [line_u_combined, line_u_separate]:
            l.set_ydata(u)
        for l in [line_y_combined, line_y_separate]:
            l.set_ydata(y)
        # dopasowanie osi Y
        ax_combined.set_ylim(np.min(u + y) - 1, np.max(u + y) + 1)
        ax_input.set_ylim(np.min(u) - 1, np.max(u) + 1)
        ax_output.set_ylim(np.min(y) - 1, np.max(y) + 1)
        ax_combined.set_title("Symulacja układu", color='black')
        fig.canvas.draw_idle()

    for s in sliders.values():
        s.on_changed(update_plot)
    slider_f.on_changed(update_plot)
    slider_A.on_changed(update_plot)
    radio.on_clicked(update_plot)

    #dopasowanie wykresow do okna
    plt.subplots_adjust(left=0.15, right=0.99, top=0.95, bottom=0.07, wspace=0.25, hspace=0.4)
    plt.show()

if __name__ == "__main__":
    simulator_with_combined_and_separate_plots()