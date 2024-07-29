import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

#asscalar redefine(numpy version?)
def patch_asscalar(a):
    return a.item()
setattr(np, "asscalar", patch_asscalar)

# RGB convert to Cielab
def rgb_to_lab(r, g, b):
    rgb = sRGBColor(r/255, g/255, b/255)
    lab = convert_color(rgb, LabColor)
    return np.array([lab.lab_l, lab.lab_a, lab.lab_b])
#Cie convert to RGB
def lab_to_rgb(lab):
    lab_color = LabColor(*lab)
    rgb = convert_color(lab_color, sRGBColor)
    return np.array([rgb.rgb_r, rgb.rgb_g, rgb.rgb_b]) * 255

def generate_color_list():
    #initial_colors, seleted from R, G and B.
    initial_colors = [
        [255, 0, 0],  # Red
        [0, 255, 0],  # Green
        [0, 0, 255]   # Blue
    ]
    # target direction
    # for example: when initial color is Red, then the direction will be : Green, Blue and Cyan(R = 0)
    target_rgbs = {
        'R': [[0, 255, 0], [0, 0, 255], [0, 255, 255]],
        'G': [[255, 0, 0], [0, 0, 255], [255, 0, 255]],
        'B': [[255, 0, 0], [0, 255, 0], [255, 255, 0]]
    }
    # define min delta from start point to end point
    min_total_delta_e = float('inf')
    
    # select min delta from total 9 directions.
    for initial_rgb in initial_colors:
        initial_lab = rgb_to_lab(*initial_rgb)
        key = 'RGB'[initial_colors.index(initial_rgb)]
        for target_rgb in target_rgbs[key]:
            target_lab = rgb_to_lab(*target_rgb)
            total_delta_e = delta_e_cie2000(LabColor(*initial_lab), LabColor(*target_lab))
            min_total_delta_e = min(min_total_delta_e, total_delta_e)
    
    # if inital color is red
    initial_rgb = [255, 0, 0]  # Red
    initial_lab = rgb_to_lab(*initial_rgb)
    color_list = [initial_lab]
    
    for target_rgb in target_rgbs['R']:
        target_lab = rgb_to_lab(*target_rgb)
        direction = target_lab - initial_lab
        
        for i in range(1, 7):  # 1/7, 2/7, ..., 6/7. 6step except end point 
            target_delta_e = (i / 7) * min_total_delta_e
            
            # Binary Search
            low, high = 0, 1
            for _ in range(100):  #max_search time
                mid = (low + high) / 2
                new_lab = initial_lab + direction * mid
                new_delta_e = delta_e_cie2000(LabColor(*initial_lab), LabColor(*new_lab))
                
                if abs(new_delta_e - target_delta_e) < 0.05:  # allowable error 0.05
                    break
                elif new_delta_e < target_delta_e:
                    low = mid
                else:
                    high = mid
            
            new_lab = initial_lab + direction * mid
            
            # check same color
            if not any(np.allclose(new_lab, existing_color, atol=1e-3) for existing_color in color_list):
                color_list.append(new_lab)
    
    return np.array(color_list)

color_list_lab = generate_color_list()

print("Generated colors (LAB and RGB):")
#print generated color
for i, lab_color in enumerate(color_list_lab):
    rgb_color = lab_to_rgb(lab_color)
    print(f"Color {i}: LAB={lab_color}, RGB={rgb_color}")
    if np.any(rgb_color < 0) or np.any(rgb_color > 255):
        print(f"  Warning: RGB values out of range for color {i}")

# plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

for i, lab_color in enumerate(color_list_lab):
    rgb_color = lab_to_rgb(lab_color)
    rgb_normalized = rgb_color / 255.0  # normalized rgb to 0-1 (for plot)
    if i == 0:
        ax.scatter(lab_color[1], lab_color[2], lab_color[0], c=[rgb_normalized], s=100, label='Initial Color (Red)')
    else:
        ax.scatter(lab_color[1], lab_color[2], lab_color[0], c=[rgb_normalized], s=50)

# connect color points
for i in range(1, len(color_list_lab), 6):
    ax.plot([color_list_lab[0][1], *color_list_lab[i:i+6, 1]],
            [color_list_lab[0][2], *color_list_lab[i:i+6, 2]],
            [color_list_lab[0][0], *color_list_lab[i:i+6, 0]],
            c='gray', linestyle='--', alpha=0.5)

ax.set_xlabel('a*')
ax.set_ylabel('b*')
ax.set_zlabel('L*')
ax.set_xlim(-128, 128)
ax.set_ylim(-128, 128)
ax.set_zlim(0, 100)

plt.title('Color Points in CIELAB Space (From Red)')
plt.legend()
plt.show()