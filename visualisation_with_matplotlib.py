import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# -----------------------------
# PARAMÈTRES DE L'ASTÉROÏDE
# -----------------------------
a = 1.5          # Demi-grand axe en UA
e = 0.3          # Excentricité
i_deg = 10       # Inclinaison en degrés
theta = np.linspace(0, 2*np.pi, 500)  # angle vrai

# Rayon de l'orbite
r = a * (1 - e**2) / (1 + e * np.cos(theta))
i_rad = np.radians(i_deg)
x = r * np.cos(theta)
y = r * np.sin(theta) * np.cos(i_rad)
z = r * np.sin(theta) * np.sin(i_rad)

# Position Terre
x_earth, y_earth, z_earth = 1.0, 0.0, 0.0

# -----------------------------
# CRÉATION DE LA FIGURE
# -----------------------------
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')

# Soleil et Terre
ax.scatter(0, 0, 0, color='yellow', s=150, label='Soleil')
ax.scatter(x_earth, y_earth, z_earth, color='blue', s=100, label='Terre')

# Trace initiale de l'astéroïde
line, = ax.plot([], [], [], color='red', label='Astéroïde')
point, = ax.plot([], [], [], 'o', color='red')

ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([-1, 1])
ax.set_xlabel('X (UA)')
ax.set_ylabel('Y (UA)')
ax.set_zlabel('Z (UA)')
ax.set_title("Animation 3D de l'orbite d'un astéroïde")
ax.legend()

# -----------------------------
# FONCTION D'ANIMATION
# -----------------------------
def update(num):
    line.set_data(x[:num], y[:num])
    line.set_3d_properties(z[:num])
    point.set_data(x[num-1:num], y[num-1:num])
    point.set_3d_properties(z[num-1:num])
    return line, point

ani = FuncAnimation(fig, update, frames=len(theta), interval=20, blit=True)

plt.show()