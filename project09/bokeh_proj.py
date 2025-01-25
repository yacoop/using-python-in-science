from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
import numpy as np
from scipy.integrate import odeint


# poetry run bokeh serve --show ./project09/bokeh_proj.py

def sir_model(y, t, beta, gamma):
    s, i, r = y
    dS_dt = -beta * s * i
    dI_dt = beta * s * i - gamma * i
    dR_dt = gamma * i
    return [dS_dt, dI_dt, dR_dt]

def simulate_sir(beta, gamma, s0, i0, r0, t_max):
    
    dt = 0.1 
    t = np.arange(0, t_max + dt, dt)
    y0 = [s0, i0, r0]
    solution = odeint(sir_model, y0, t, args=(beta, gamma))
    s, i, r = solution.T

    return s, i, r, t

beta = 0.3
gamma = 0.1
s0 = 0.99
i0 = 0.01
r0 = 0.0
t_max = 100

s, i, r, t = simulate_sir(beta, gamma, s0, i0, r0, t_max)

source = ColumnDataSource(data={"t": t, "S": s, "I": i, "R": r})

plot = figure(title="SIR Model", x_axis_label="Time", y_axis_label="Population Fraction", height=720, width=1280)
plot.line("t", "S", source=source, color="blue", legend_label="Susceptible")
plot.line("t", "I", source=source, color="red", legend_label="Infected")
plot.line("t", "R", source=source, color="green", legend_label="Removed")
plot.legend.location = "right"
plot.grid.grid_line_dash = [6,4]

beta_slider = Slider(title="Beta", value=beta, start=0.001, end=1.0, step=0.001)
gamma_slider = Slider(title="Gamma", value=gamma, start=0.001, end=1.0, step=0.001)
tmax_slider = Slider(title="Time", value=t_max, start=10, end=200, step=1)

def update(attr, old, new):
    beta = beta_slider.value
    gamma = gamma_slider.value
    t_max = tmax_slider.value
    s, i, r, t = simulate_sir(beta, gamma, s0, i0, r0, t_max)
    source.data = {"t": t, "S": s, "I": i, "R": r}

beta_slider.on_change("value", update)
gamma_slider.on_change("value", update)
tmax_slider.on_change("value", update)

dashboard = column(plot, row(beta_slider, gamma_slider, tmax_slider))

curdoc().add_root(dashboard)
curdoc().title = "SIR Model"