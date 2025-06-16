import matplotlib
matplotlib.use("Qt5Agg")                 # любой интерактивный backend
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
from matplotlib.animation import FFMpegWriter

# ------------------- константы сцены ------------------- #
LANE_WIDTH = 3.5
NUM_LANES = 6
LANE_CENTERS = [(i - (NUM_LANES - 1) / 2) * LANE_WIDTH for i in range(NUM_LANES)]
ROAD_HALF = NUM_LANES / 2 * LANE_WIDTH           # ≈ 10.5 м

EGO_WIDTH, EGO_LENGTH = 2.0, 4.0
EGO_VY = 20.0                                     # м/с
EGO_LANE = 4                                      # 5-я полоса (index 4)
EGO_START_Y = 0.35 * 140                          # ≈ 49 м

PRIMARY_W, PRIMARY_L = 8 * EGO_WIDTH, 10 * EGO_LENGTH
SECOND_W,  SECOND_L  = 2 * EGO_WIDTH,  2 * EGO_LENGTH

SIM_TIME, DT = 15.0, 0.05
FRAMES = int(SIM_TIME / DT)

# ------------------- класс ТС ------------------- #
class Vehicle:
    def __init__(self, lane_idx, y, vy, is_ego=False):
        self.x = LANE_CENTERS[lane_idx]
        self.y = y
        self.vx = 0.0
        self.vy = vy
        self.is_ego = is_ego
        self.nvo = False
        self.timer = 0        # кадры «запоминания» НВО
        self.adaptive = False
        self.patch: Rectangle | None = None
        self.arrow:  FancyArrowPatch | None = None
        self.text  = None
    # прямоугольник (xmin,xmax,ymin,ymax)
    def bounds(self):
        return (self.x - EGO_WIDTH/2, self.x + EGO_WIDTH/2,
                self.y - EGO_LENGTH/2, self.y + EGO_LENGTH/2)
    def step(self, dt):
        self.y += self.vy * dt

# ------------------- создаём ТС ------------------- #
vehicles = [
    Vehicle(3,  0,  30),      # попутная
    Vehicle(2, 110, -15),      # встречная
    Vehicle(4,  10,  20),      # попутная (должна стать НВО)
    Vehicle(1, 120, -20),      # встречная, быстрее
    Vehicle(0,  80, -12),      # встречная, медленнее
    Vehicle(3,  5,  50),      # попутная, медленная
    Vehicle(4, 150,  13),      # попутная далеко
    Vehicle(5, 150,  0)       # попутная далеко
]

vehicles[2].adaptive = True     
ego = Vehicle(EGO_LANE, EGO_START_Y, EGO_VY, is_ego=True)
vehicles.insert(0, ego)        # эго-ТС всегда первая в списке

# ------------------- графика ------------------- #
fig, ax = plt.subplots(figsize=(7, 9))
ax.set_aspect("equal")
ax.set_xlim(-ROAD_HALF-1, ROAD_HALF+1)
ax.set_ylim(ego.y - 20, ego.y + 100)
ax.set_xlabel("X, м")
ax.set_ylabel("Y, м")
ax.set_title("Алгоритм НВО")

# дорога и разметка
road = Rectangle((-ROAD_HALF, -400), 2*ROAD_HALF, 1500, facecolor="lightgray", zorder=0)
ax.add_patch(road)
for dx in (-0.05, +0.05):
    ax.plot([dx, dx], [-400, 1500], color="yellow", linewidth=3)           # двойная сплошная
for idx in (0, 1, 3, 4):
    xc = (LANE_CENTERS[idx] + LANE_CENTERS[idx+1]) / 2
    ax.plot([xc, xc], [-400, 1500], color="white", linewidth=2, linestyle=(0, (10,10)))

# зоны безопасности (patch'и будут перемещаться вместе с эго)
primary = Rectangle((0,0), PRIMARY_W, PRIMARY_L,
                    facecolor="none", edgecolor="turquoise",
                    linestyle="--", linewidth=2, zorder=1)
secondary = Rectangle((0,0), SECOND_W, SECOND_L,
                      facecolor="none", edgecolor="magenta",
                      linestyle="dashdot", linewidth=2, zorder=1)
ax.add_patch(primary); ax.add_patch(secondary)

# счётчик НВО
nvo_text = ax.text(0.99, 0.99, "", transform=ax.transAxes,
                   ha="right", va="top", fontsize=12, color="black",
                   bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))

# создаём графические объекты для ТС
for v in vehicles:
    clr = "cyan" if v.is_ego else "lightgray"
    v.patch = Rectangle((v.x - EGO_WIDTH/2, v.y - EGO_LENGTH/2),
                        EGO_WIDTH, EGO_LENGTH,
                        facecolor=clr, edgecolor="black", zorder=3)
    ax.add_patch(v.patch)
    # стрелка-заглушка (координаты обновим в анимации)
    v.arrow = FancyArrowPatch((0,0), (0,0), arrowstyle='->', mutation_scale=15,
                              color='black', linewidth=1.5, zorder=4)
    ax.add_patch(v.arrow)
    v.text = ax.text(v.x, v.y + EGO_LENGTH/2 + 1.5, s="", fontsize=7,
                     ha="center", va="bottom", zorder=4)

# ------------------- вспомогательные функции ------------------- #
def rects_intersect(a, b):
    ax1, ax2, ay1, ay2 = a
    bx1, bx2, by1, by2 = b
    return (ax2 > bx1 and ax1 < bx2 and ay2 > by1 and ay1 < by2)

def update_zones():
    primary.set_xy((ego.x - PRIMARY_W/2, ego.y - PRIMARY_L/2))
    secondary.set_xy((ego.x - SECOND_W/2, ego.y - SECOND_L/2))

# ------------------- основная анимация ------------------- #
collision_flag = False

def adapt_speed(v: Vehicle):

    SAFE_GAP   = SECOND_L             # хотим держать переднюю кромку
    K_P        = 1               # коэффициент «жёсткости»
    MAX_A      = 6.0                  # макс |ускорение|, м/с²
    MAX_V, MIN_V = 60.0, 0.0

    front_v   = v.y + EGO_LENGTH
    front_ego = ego.y + EGO_LENGTH
    err       = (front_v - front_ego) + SAFE_GAP        # (+) далеко / (–) близко

    desired_v = ego.vy - K_P * err
    desired_v = np.clip(desired_v, MIN_V, MAX_V)

    dv = desired_v - v.vy
    a  = np.clip(dv / DT, -MAX_A, MAX_A)
    v.vy += a * DT

def animate(_):
    global collision_flag

    # === 0. адаптивное ТС регулирует скорость ===
    for v in vehicles:
        if getattr(v, "adaptive", False):
            adapt_speed(v)

    # 1. движение
    for v in vehicles:
        v.step(DT)

    # 2. пересчёт зон
    update_zones()
    zone1 = (ego.x - PRIMARY_W/2, ego.x + PRIMARY_W/2,
             ego.y - PRIMARY_L/2, ego.y + PRIMARY_L/2)
    zone2 = (ego.x - SECOND_W/2, ego.x + SECOND_W/2,
             ego.y - SECOND_L/2, ego.y + SECOND_L/2)

    # 3. проверка НВО / цвета / стрелок
    active_nvo = 0
    for v in vehicles:
        # графика прямоугольника
        v.patch.set_xy((v.x - EGO_WIDTH/2, v.y - EGO_LENGTH/2))
        # подпись координат/скорости
        v.text.set_position((v.x, v.y + EGO_LENGTH/2 + 1.5))
        v.text.set_text(f"({v.x:+.1f},{v.y:+.1f})\nv={v.vy:+.1f}")

        if v.is_ego:
            continue

        # --- условия НВО ---
        veh_rect = v.bounds()
        cond_a = rects_intersect(veh_rect, zone2)                     # пересёк зону-2

        speed   = abs(v.vy)
        moving_with_flow = ((v.vy > 0 and v.x > 0) or (v.vy < 0 and v.x < 0))
        cond_b = (speed >= 50 and moving_with_flow               # скорость >50
          and rects_intersect(veh_rect, zone1))         # ТОЛЬКО если в зоне-1

        same_lane_ahead = (abs(v.x - ego.x) < LANE_WIDTH/2 and v.y > ego.y)
        cond_c = (same_lane_ahead and rects_intersect(veh_rect, zone1) and v.vy < ego.vy)


        # исключение: стоит и не в полосе эго
        stationary_exception = (speed < 0.1 and abs(v.x - ego.x) >= LANE_WIDTH/2)

        triggered = (cond_a or cond_b or cond_c) and not stationary_exception

        if triggered:
            v.nvo = True
            v.timer = 30                      # 3 с при DT=0.05
        else:
            if v.nvo:
                if v.timer > 0:
                    v.timer -= 1
                else:
                    v.nvo = False

        # активное НВО?
        if v.nvo:
            active_nvo += 1

        # --- цвет прямоугольника ---
        if v.nvo:
            colour = "red"
        elif rects_intersect(veh_rect, zone1):
            colour = "lightgreen"
        else:
            colour = "lightgray"
        v.patch.set_facecolor(colour)
        v.text.set_color("black")

        # --- стрелка скорости ---
        max_arrow = 2 * EGO_LENGTH           # max 8 м
        arrow_len = max_arrow * min(speed, 60)/60
        if v.vy >= 0:
            start = (v.x, v.y - EGO_LENGTH/2)
            end   = (v.x, start[1] + arrow_len)
        else:
            start = (v.x, v.y + EGO_LENGTH/2)
            end   = (v.x, start[1] - arrow_len)
        v.arrow.set_positions(start, end)

    # стрелка эго-ТС (для равномерности)
    ego_speed = abs(ego.vy)
    ego_arrow_len = 2*EGO_LENGTH * min(ego_speed, 60)/60
    ego.arrow.set_positions((ego.x, ego.y - EGO_LENGTH/2),
                            (ego.x, ego.y - EGO_LENGTH/2 + ego_arrow_len))

    # 4. вывод счётчика НВО
    nvo_text.set_text(f"НВО зафиксировано: {active_nvo}")

    # 5. проверка столкновений
    if not collision_flag:
        for i in range(len(vehicles)):
            for j in range(i+1, len(vehicles)):
                if rects_intersect(vehicles[i].bounds(), vehicles[j].bounds()):
                    collision_flag = True
                    anim.event_source.stop()        # пауза
                    nvo_text.set_text("Столкновение!   " + nvo_text.get_text())
                    break
            if collision_flag:
                break

    # 6. камера следует за эго
    ax.set_ylim(ego.y - 49, ego.y + 91)
    return []

# ------------------- запуск ------------------- #
anim = FuncAnimation(fig, animate, frames=FRAMES, interval=DT*1000, blit=False)

fps = int(1 / DT)            # частота кадров анимации (DT = 0.05 → 20 fps)
writer = FFMpegWriter(fps=fps, bitrate=1800)

anim.save("nvo_demo.mp4", writer=writer)
print("Видео сохранено: nvo_demo.mp4")


plt.tight_layout()
plt.show()

