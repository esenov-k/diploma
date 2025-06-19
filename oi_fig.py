import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np

# ---------- constants ---------- #
LANE_WIDTH = 3.5
NUM_LANES = 6
LANE_CENTERS = [(i - (NUM_LANES - 1) / 2) * LANE_WIDTH for i in range(NUM_LANES)]
ROAD_HALF = NUM_LANES/2 * LANE_WIDTH

EGO_W, EGO_L = 2.0, 4.0
PRIMARY_W, PRIMARY_L = 8*EGO_W, 10*EGO_L
SECOND_W, SECOND_L = 2*EGO_W, 2*EGO_L
MAX_ARROW_LEN = 2*EGO_L
MAX_SPEED = 60

ego_x = LANE_CENTERS[3]

def add_road(ax, y0, y1):
    # road background
    ax.add_patch(Rectangle((-ROAD_HALF, y0), 2*ROAD_HALF, y1-y0,
                           facecolor="lightgray", zorder=0))
    # double yellow center
    for dx in (-0.05, 0.05):
        ax.plot([dx, dx], [y0, y1], color="yellow", linewidth=4, zorder=1)
    # dashed white between lanes
    for idx in (0,1,3,4):
        xc = (LANE_CENTERS[idx] + LANE_CENTERS[idx+1])/2
        ax.plot([xc, xc], [y0, y1], color="white", linewidth=3,
                linestyle=(0,(12,12)), zorder=1)
    # direction arrows on pavement
    for lane in range(NUM_LANES):
        xc = LANE_CENTERS[lane]
        for y in np.arange(y0+5, y1, 15):
            if lane >= 3:
                ax.text(xc, y, "↑", ha='center', va='center', fontsize=16, color='white', zorder=1)
            else:
                ax.text(xc, y, "↓", ha='center', va='center', fontsize=16, color='white', zorder=1)

def draw_scene(ax, ego_y, vehicles, title):
    ax.set_aspect('equal')
    ax.set_xlim(-ROAD_HALF-0.5, ROAD_HALF+0.5)
    ax.set_ylim(ego_y-20, ego_y+40)
    ax.set_xticks([])
    ax.set_yticks([])
    add_road(ax, ego_y-20, ego_y+40)
    ax.set_title(title, fontsize=14, pad=12)

    # zones
    prim = Rectangle((ego_x - PRIMARY_W/2, ego_y - PRIMARY_L/2),
                     PRIMARY_W, PRIMARY_L, facecolor='none',
                     edgecolor='turquoise', linestyle='--', linewidth=3, zorder=2, label="Zone 1")
    sec  = Rectangle((ego_x - SECOND_W/2, ego_y - SECOND_L/2),
                     SECOND_W, SECOND_L, facecolor='none',
                     edgecolor='magenta', linestyle='dashdot', linewidth=3, zorder=2, label="Zone 2")
    ax.add_patch(prim); ax.add_patch(sec)
    # ego
    ego_rect = Rectangle((ego_x-EGO_W/2, ego_y-EGO_L/2),
                         EGO_W, EGO_L, facecolor='cyan', edgecolor='black', zorder=4)
    ax.add_patch(ego_rect)
    ax.text(ego_x, ego_y, "EGO", ha='center', va='center', fontsize=9, color='black', zorder=5)

    # draw vehicles list items: (lane_idx, rel_y, vy, color, label)
    for lane_idx, rel_y, vy, color, lbl in vehicles:
        x = LANE_CENTERS[lane_idx]
        y = ego_y + rel_y
        rect = Rectangle((x-EGO_W/2, y-EGO_L/2),
                         EGO_W, EGO_L, facecolor=color, edgecolor='black', zorder=4)
        ax.add_patch(rect)
        ax.text(x, y, lbl, fontsize=8, ha='center', va='center', zorder=5)
        speed = abs(vy)
        arrow_len = MAX_ARROW_LEN * min(speed, MAX_SPEED)/MAX_SPEED
        if vy>=0:
            start = (x, y - EGO_L/2)
            end   = (x, start[1]+arrow_len)
        else:
            start = (x, y + EGO_L/2)
            end   = (x, start[1]-arrow_len)
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle='->',
                                     mutation_scale=15, color='black', linewidth=1.8, zorder=5))

# create figure
fig, axs = plt.subplots(1,3, figsize=(22,7))

# Scene 1
scene1 = [
    (5, 30, 55, 'lightgray', 'Fast'),   # fast not yet NVO
]
draw_scene(axs[0], 0, scene1, "1. Быстрое ТС ещё вне зон")

# Scene 2
scene2 = [
    (3, -5, 30, 'red', 'Close→NVO'),      # entering zone2
    (5, 7, 60, 'red', 'Fast→NVO')
]
draw_scene(axs[1], 0, scene2, "2. Пересекает зону 2 → НВО")

# Scene 3
scene3 = [
    (3, 14, 15, 'red', 'Slow NVO'),     # same lane slow ahead
    (5, 19, 35, 'lightgreen', 'In 1st Zone')
]
draw_scene(axs[2], 0, scene3, "3. Медленный впереди – НВО")

plt.tight_layout()

fig.savefig("nvo_algorithm_scenes.png", dpi=400)
