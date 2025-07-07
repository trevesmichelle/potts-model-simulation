import numpy as np
from collections import Counter
from numba import njit

@njit
def initialize_lattice(L, q):
    return np.random.randint(0, q, size=(L, L))

@njit
def delta_energy(lattice, i, j, new_state):
    L = lattice.shape[0]
    s_old = lattice[i, j]
    if s_old == new_state:
        return 0

    deltaE = 0
    neighbors = [
        lattice[i, (j+1)%L],
        lattice[i, (j-1)%L],
        lattice[(i+1)%L, j],
        lattice[(i-1)%L, j],
    ]

    for sn in neighbors:
        deltaE += 1 if s_old == sn else 0
        deltaE -= 1 if new_state == sn else 0
    return deltaE

@njit
def metropolis_step(lattice, q, T_star):
    L = lattice.shape[0]
    for _ in range(L * L):
        i = np.random.randint(0, L)
        j = np.random.randint(0, L)
        new_state = np.random.randint(0, q)
        dE = delta_energy(lattice, i, j, new_state)
        if dE <= 0 or np.random.rand() < np.exp(-dE / T_star):
            lattice[i, j] = new_state

@njit
def compute_energy(lattice, q):
    L = lattice.shape[0]
    energy = 0
    for i in range(L):
        for j in range(L):
            s = lattice[i, j]
            neighbors = [
                lattice[i, (j+1)%L],
                lattice[i, (j-1)%L],
                lattice[(i+1)%L, j],
                lattice[(i-1)%L, j],
            ]
            for sn in neighbors:
                if s == sn:
                    energy -= 1
    return energy / 2


def order_parameter(lattice, q):
    count = Counter(lattice.flatten())
    L2 = lattice.size
    max_frac = max(count[s]/L2 for s in range(q))
    return (q * max_frac - 1) / (q - 1)

def run_simulation(q=3, L=10, T_star=1.0, steps=10000, burn_in=1000):
    lattice = initialize_lattice(L, q)
    energies = []
    magnetizations = []

    for step in range(steps):
        metropolis_step(lattice, q, T_star)
        if step >= burn_in:
            E = compute_energy(lattice, q)
            m = order_parameter(lattice, q)
            energies.append(E)
            magnetizations.append(m)

    E_avg = np.mean(energies)
    E2_avg = np.mean(np.square(energies))
    m_avg = np.mean(magnetizations)
    m2_avg = np.mean(np.square(magnetizations))

    c = (E2_avg - E_avg**2) / (L**2 * T_star**2)
    chi = L**2 * (m2_avg - m_avg**2) / T_star

    return {
        "E_avg": E_avg / (L**2),
        "m_avg": m_avg,
        "c": c,
        "chi": chi,
        "energies": energies,
        "magnetizations": magnetizations
    }
