import numpy as np
import matplotlib.pyplot as plt

def f(x): return np.sin(x)
exact = 1 - np.cos(1)

def trapezoidal_rule(f, a, b, n):
    h = (b - a) / n
    x = np.linspace(a, b, n+1)
    y = f(x)
    return (h/2) * (y[0] + 2*sum(y[1:-1]) + y[-1])

def simpsons_rule(f, a, b, n):
    if n % 2 == 1: n += 1
    h = (b - a) / n
    x = np.linspace(a, b, n+1)
    y = f(x)
    return (h/3) * (y[0] + 4*sum(y[1:-1:2]) + 2*sum(y[2:-2:2]) + y[-1])

N = [2**k for k in range(2, 8)]
errors_trap, errors_simp = [], []

for n in N:
    errors_trap.append(abs(trapezoidal_rule(f, 0, 1, n) - exact))
    errors_simp.append(abs(simpsons_rule(f, 0, 1, n) - exact))

plt.loglog(N, errors_trap, 'o-', label="Trapezoidal")
plt.loglog(N, errors_simp, 's-', label="Simpson's")
plt.legend(); plt.xlabel("N"); plt.ylabel("Error"); plt.show()