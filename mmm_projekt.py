import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider
from scipy.signal import sawtooth

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

def generate_signal(f, A, t, wybor):
    if wybor == 'Prostokątny':
        return A * np.where(np.sin(2 * np.pi * f * t) >= 0, 1, -1)
    elif wybor == 'Trójkątny':
        return A * (2 * np.abs(2 * ((t*f) % 1) - 1) - 1)
    elif wybor == 'Sinusoidalny':
        return A * np.sin(2 * np.pi * f * t)
    else:
        raise ValueError("Nieznany typ sygnału: " + wybor)

def system_response(num, den, licz, mian, u, t, dt):
    y = np.zeros_like(t)
    u_c = np.zeros_like(t)
    b2, b1, b0 = den
    a1, a0 = num
    c2, c1, c0 = licz
    d2, d1, d0 = mian
    dy_obj = 0
    dy_ctrl = 0
    y_obj = 0
    y_ctrl = 0
    e_prev = 0
    u_c_prev = 0

    for i in range(len(t) - 1):
        e = u[i] - y[i]
        y_ctrl, dy_ctrl = simulate_block_step([c2, c1, c0], [d2, d1, d0], e, e_prev, y_ctrl, dy_ctrl, dt)
        u_c[i + 1] = y_ctrl
        e_prev = e
        y_obj, dy_obj = simulate_block_step([a1, a0], [b2, b1, b0], u_c[i + 1], u_c_prev, y_obj, dy_obj, dt)
        y[i + 1] = y_obj
        u_c_prev = u_c[i + 1]
    return y

def simulator_with_sliders():
    # Parametry transmitancji
    a1, a0 = 1, 2
    b2, b1, b0 = 1, 3, 2
    num = a1, a0
    den = b2, b1, b0

    c2, c1, c0 = 1, 1, 1
    d2, d1, d0 = 1, 2, 1
    licz = c2, c1, c0
    mian = d2, d1, d0

    dt = 0.01
    t = np.arange(0, 10, dt)
    f = 0.5
    A = 1.0

    signal_type = 'Prostokątny'
    u = generate_signal(f, A, t, signal_type)
    y = system_response(num, den, licz, mian, u, t, dt)

    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.35, bottom=0.3)
    input_line, = ax.plot(t, u, 'r--', label='Sygnał wejściowy')
    output_line, = ax.plot(t, y, 'b', label='Odpowiedź układu')
    ax.set_xlabel('Czas [s]')
    ax.set_ylabel('Amplituda')
    ax.set_title('Symulacja układu')
    ax.grid(True)
    ax.legend()

    ax_radio = plt.axes([0.05, 0.6, 0.25, 0.2])
    radio = RadioButtons(ax_radio, ['Prostokątny', 'Trójkątny', 'Sinusoidalny'])

    ax_slider_f = plt.axes([0.05, 0.15, 0.25, 0.03])
    slider_f = Slider(ax_slider_f, 'Częstotliwość [Hz]', 0.1, 7.0, valinit=f)

    ax_slider_A = plt.axes([0.05, 0.1, 0.25, 0.03])
    slider_A = Slider(ax_slider_A, 'Amplituda [V]', 0.0, 10.0, valinit=A)

    def update_plot(_):
        f = slider_f.val
        A = slider_A.val
        typ = radio.value_selected
        u = generate_signal(f, A, t, typ)
        y = system_response(num, den, licz, mian, u, t, dt)
        input_line.set_ydata(u)
        output_line.set_ydata(y)

        # Automatyczne skalowanie osi Y
        y_min = min(np.min(u), np.min(y))
        y_max = max(np.max(u), np.max(y))
        ax.set_ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))

        fig.canvas.draw_idle()

    radio.on_clicked(update_plot)
    slider_f.on_changed(update_plot)
    slider_A.on_changed(update_plot)

    plt.show()

if __name__ == "__main__":
    simulator_with_sliders()
