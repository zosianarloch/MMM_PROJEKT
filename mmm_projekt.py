import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider

def simulate_block_step(num, den, u_now, u_prev, u_prev2, y, dy, dt):
    """Symuluje blok dynamiczny 2. rzędu metodą Eulera do przodu (adaptacyjna dla rzędu licznika)"""
    b2, b1, b0 = den

    # Dopasowanie długości licznika
    if len(num) == 3:  # np. [c2, c1, c0]
        a2, a1, a0 = num
        du = (u_now - u_prev) / dt
        ddu = (u_now - 2 * u_prev + u_prev2) / dt**2
    elif len(num) == 2:  # np. [a1, a0]
        a2 = 0
        a1, a0 = num
        du = (u_now - u_prev) / dt
        ddu = 0
    else:  # tylko [a0]
        a2 = 0
        a1 = 0
        a0 = num[0]
        du = 0
        ddu = 0

    rhs = a2 * ddu + a1 * du + a0 * u_now
    ddy = (rhs - b1 * dy - b0 * y) / b2
    dy_new = dy + dt * ddy
    y_new = y + dt * dy_new
    return y_new, dy_new

def generate_signal(f, A, t, wybor):
    if wybor == 'Prostokątny':
        return A * np.where(np.sin(2 * np.pi * f * t) >= 0, 1, -1)
    elif wybor == 'Trójkątny':
        return A * (2 * np.abs(2 * ((t * f) % 1) - 1) - 1)
    elif wybor == 'Sinusoidalny':
        return A * np.sin(2 * np.pi * f * t)
    else:
        raise ValueError("Nieznany typ sygnału: " + wybor)

def system_response(num, den, licz, mian, u, t, dt):
    y = np.zeros_like(t)
    u_c = np.zeros_like(t)
    dy_obj = 0
    dy_ctrl = 0
    y_obj = 0
    y_ctrl = 0
    e_prev = 0
    e_prev2 = 0
    u_c_prev = 0
    u_c_prev2 = 0

    for i in range(1, len(t) - 1):
        e = u[i] - y[i]
        y_ctrl, dy_ctrl = simulate_block_step(licz, mian, e, e_prev, e_prev2, y_ctrl, dy_ctrl, dt)
        u_c[i + 1] = y_ctrl
        e_prev2 = e_prev
        e_prev = e

        y_obj, dy_obj = simulate_block_step(num, den, u_c[i + 1], u_c_prev, u_c_prev2, y_obj, dy_obj, dt)
        y[i + 1] = y_obj
        u_c_prev2 = u_c_prev
        u_c_prev = u_c[i + 1]

    return y

def simulator_with_sliders():
    dt = 0.01
    t = np.arange(0, 10, dt)
    f = 0.5
    A = 1.0
    signal_type = 'Prostokątny'

    param_defaults = {
        'a1': 1.0, 'a0': 2.0,
        'b2': 1.0, 'b1': 3.0, 'b0': 2.0,
        'c2': 1.0, 'c1': 1.0, 'c0': 1.0,
        'd2': 1.0, 'd1': 2.0, 'd0': 1.0,
    }

    sliders = {}
    y_pos = 0.6
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.4, bottom=0.4)

    # Inicjalizacja sygnału i odpowiedzi
    u = generate_signal(f, A, t, signal_type)
    y = system_response(
        [param_defaults['a1'], param_defaults['a0']],
        [param_defaults['b2'], param_defaults['b1'], param_defaults['b0']],
        [param_defaults['c2'], param_defaults['c1'], param_defaults['c0']],
        [param_defaults['d2'], param_defaults['d1'], param_defaults['d0']],
        u, t, dt
    )

    input_line, = ax.plot(t, u, 'r--', label='Sygnał wejściowy')
    output_line, = ax.plot(t, y, 'b', label='Odpowiedź układu')
    ax.set_xlabel('Czas [s]')
    ax.set_ylabel('Amplituda')
    ax.set_title('Symulacja układu')
    ax.grid(True)
    ax.legend()

    # Slidery dla parametrów transmitancji
    fig.text(0.05, 0.65, "Parametry transmitancji", fontsize=12, fontweight='bold')
    for param in param_defaults:
        ax_slider = plt.axes([0.05, y_pos, 0.25, 0.025])
        sliders[param] = Slider(ax_slider, param, 0.0, 5.0, valinit=param_defaults[param])
        y_pos -= 0.035

    # Slidery dla sygnału
    fig.text(0.05, 0.18, "Parametry sygnału wejściowego", fontsize=12, fontweight='bold')
    ax_slider_f = plt.axes([0.05, 0.08, 0.25, 0.03])
    slider_f = Slider(ax_slider_f, 'f [Hz]', 0.0, 7.0, valinit=f)

    ax_slider_A = plt.axes([0.05, 0.13, 0.25, 0.03])
    slider_A = Slider(ax_slider_A, 'A [V]', 0.0, 10.0, valinit=A)

    # Radio buttons
    fig.text(0.05, 0.9, "Wybór sygnału wejściowego", fontsize=12, fontweight='bold')
    ax_radio = plt.axes([0.05, 0.75, 0.25, 0.12])
    radio = RadioButtons(ax_radio, ['Prostokątny', 'Trójkątny', 'Sinusoidalny'])

    def update_plot(_):
        f_val = slider_f.val
        A_val = slider_A.val
        typ = radio.value_selected

        u = generate_signal(f_val, A_val, t, typ)

        num = [sliders['a1'].val, sliders['a0'].val]
        den = [sliders['b2'].val, sliders['b1'].val, sliders['b0'].val]
        licz = [sliders['c2'].val, sliders['c1'].val, sliders['c0'].val]
        mian = [sliders['d2'].val, sliders['d1'].val, sliders['d0'].val]

        y = system_response(num, den, licz, mian, u, t, dt)
        input_line.set_ydata(u)
        output_line.set_ydata(y)

        y_min = min(np.min(u), np.min(y))
        y_max = max(np.max(u), np.max(y))
        ax.set_ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))

        fig.canvas.draw_idle()

    for s in sliders.values():
        s.on_changed(update_plot)
    slider_f.on_changed(update_plot)
    slider_A.on_changed(update_plot)
    radio.on_clicked(update_plot)

    plt.get_current_fig_manager().resize(1200, 800)
    plt.show()

if __name__ == "__main__":
    simulator_with_sliders()