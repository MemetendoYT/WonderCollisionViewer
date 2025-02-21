import re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import tkinter as tk
from tkinter import filedialog
import yaml
import os

def open_file():
    global content, file_name
    file_path = filedialog.askopenfilename(
        title="Select a Text File", 
        filetypes=[("Text files", "*.txt")]
    )
    if file_path:
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, 'r') as file:
            content = yaml.safe_load(file)
        parse_file_content(content)

def parse_file_content(content):
    shape_names = ["Capsule", "Sphere", "Box", "Cylinder"]
    detected_shapes = []
    if "Capsule" in content["root"]:
        detected_shapes.append("Capsule")
    if "Box" in content["root"]:
        detected_shapes.append("Box")
    if "Sphere" in content["root"]:
        detected_shapes.append("Sphere")
    if "Cylinder" in content["root"]:
        detected_shapes.append("Cylinder")

    capsules = []
    if "Capsule" in detected_shapes:
        capsules = create_capsule(content["root"]["Capsule"])
    
    boxes = []
    if "Box" in detected_shapes:
        boxes = create_box(content["root"]["Box"])
    
    spheres = []
    if "Sphere" in detected_shapes:
        spheres = create_sphere(content["root"]["Sphere"])
    
    cylinders = []
    if "Cylinder" in detected_shapes:
        cylinders = create_cylinder(content["root"]["Cylinder"])

    print(f"Detected shapes: {detected_shapes}")
    print(f"Capsules: {capsules}")
    print(f"Boxes: {boxes}")
    print(f"Spheres: {spheres}")
    print(f"Cylinders: {cylinders}")

    plot_shapes(capsules, boxes, spheres, cylinders)

def create_capsule(capsules_data):
    capsules = []
    for capsule_data in capsules_data:
        capsule = {
            "CenterA": (capsule_data["CenterA"]["X"], capsule_data["CenterA"]["Y"]),
            "CenterB": (capsule_data["CenterB"]["X"], capsule_data["CenterB"]["Y"]),
            "OffsetRotation": (0, 0, capsule_data["OffsetRotation"]["Z"]),
            "OffsetTranslation": (capsule_data["OffsetTranslation"]["X"], capsule_data["OffsetTranslation"]["Y"]),
            "Radius": capsule_data["Radius"],
        }
        capsules.append(capsule)
    return capsules

def create_box(boxes_data):
    boxes = []
    for box_data in boxes_data:
        center_x, center_y = box_data["Center"]["X"], box_data["Center"]["Y"]
        half_extents_x = box_data["HalfExtents"]["X"] if "HalfExtents" in box_data else 1.0
        half_extents_y = box_data["HalfExtents"]["Y"] if "HalfExtents" in box_data else 1.0
        rotation = (0, 0, box_data["OffsetRotation"]["Z"] if "OffsetRotation" in box_data else 0)
        translation = (box_data["OffsetTranslation"]["X"] if "OffsetTranslation" in box_data else 0,
                       box_data["OffsetTranslation"]["Y"] if "OffsetTranslation" in box_data else 0)

        corners = [
            (center_x - half_extents_x, center_y - half_extents_y),
            (center_x + half_extents_x, center_y - half_extents_x),
            (center_x + half_extents_x, center_y + half_extents_y),
            (center_x - half_extents_x, center_y + half_extents_y)
        ]

        transformed_corners = [apply_transformations(x, y, rotation, translation) for x, y in corners]

        min_x = min(x for x, y in transformed_corners)
        max_x = max(x for x, y in transformed_corners)
        min_y = min(y for x, y in transformed_corners)
        max_y = max(y for x, y in transformed_corners)

        box = {
            "Min": (min_x, min_y),
            "Max": (max_x, max_y),
        }
        boxes.append(box)

        print(f"Box created: Min=({min_x}, {min_y}), Max=({max_x}, {max_y})")

    return boxes

def create_sphere(spheres_data):
    spheres = []
    for sphere_data in spheres_data:
        sphere = {
            "Center": (0, 0),  # Default center
            "Radius": sphere_data["Radius"],
            "OffsetTranslation": (sphere_data["OffsetTranslation"]["X"] if "OffsetTranslation" in sphere_data else 0,
                                  sphere_data["OffsetTranslation"]["Y"] if "OffsetTranslation" in sphere_data else 0)
        }
        spheres.append(sphere)

    print(f"Sphere matches: {spheres_data}")
    for sphere in spheres:
        print(f"Parsed sphere: Center={sphere['Center']}, Radius={sphere['Radius']}, OffsetTranslation={sphere['OffsetTranslation']}")
    return spheres
def create_cylinder(cylinders_data):
    cylinders = []
    for cylinder_data in cylinders_data:
        cylinder = {
            "CenterA": (cylinder_data["CenterA"]["X"], cylinder_data["CenterA"]["Y"]),
            "CenterB": (cylinder_data["CenterB"]["X"], cylinder_data["CenterB"]["Y"]),
            "OffsetRotation": (cylinder_data["OffsetRotation"]["X"], cylinder_data["OffsetRotation"]["Y"], cylinder_data["OffsetRotation"]["Z"]),
            "OffsetTranslation": (cylinder_data["OffsetTranslation"]["X"], cylinder_data["OffsetTranslation"]["Y"]),
            "Radius": cylinder_data["Radius"],
        }
        cylinders.append(cylinder)
        print(f"Created cylinder: {cylinder}")
    return cylinders

def rotate_point(x, y, angle):
    radians = np.radians(angle)
    x_rot = x * np.cos(radians) - y * np.sin(radians)
    y_rot = x * np.sin(radians) + y * np.cos(radians)
    return x_rot, y_rot

def translate_point(x, y, dx, dy):
    return x + dx, y + dy

def apply_transformations(x, y, rotation, translation):
    print(f"Original point: ({x}, {y})")
    x, y = rotate_point(x, y, rotation[2])
    print(f"After rotation: ({x}, {y})")
    x, y = translate_point(x, y, translation[0], translation[1])
    print(f"After translation: ({x}, {y})")
    return x, y

def plot_half_sphere(ax, center, radius, angle, orientation):
    if orientation == 'left':
        wedge = patches.Wedge(center, radius, np.degrees(angle) + 90, np.degrees(angle) - 90, color='b', alpha=0.5)
    elif orientation == 'right':
        wedge = patches.Wedge(center, radius, np.degrees(angle) - 90, np.degrees(angle) + 90, color='b', alpha=0.5)
    ax.add_patch(wedge)

def plot_capsule(ax, capsule):
    x1, y1 = capsule["CenterA"]
    x2, y2 = capsule["CenterB"]
    radius = capsule["Radius"]
    rotation = capsule["OffsetRotation"]
    translation = capsule["OffsetTranslation"]

    x1, y1 = apply_transformations(x1, y1, rotation, translation)
    x2, y2 = apply_transformations(x2, y2, rotation, translation)

    angle = np.arctan2(y2 - y1, x2 - x1)
    
    perp_angle = angle + np.pi / 2
    dx = radius * np.cos(perp_angle)
    dy = radius * np.sin(perp_angle)
    
    rect_points_x = [x1 - dx, x2 - dx, x2 + dx, x1 + dx]
    rect_points_y = [y1 - dy, y2 - dy, y2 + dy, y1 + dy]
    
    ax.fill(rect_points_x, rect_points_y, 'b', alpha=0.5)
    
    plot_half_sphere(ax, (x1, y1), radius, angle, 'left')
    plot_half_sphere(ax, (x2, y2), radius, angle, 'right')

def plot_box(ax, box):
    min_x, min_y = box["Min"]
    max_x, max_y = box["Max"]
    rect = patches.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, linewidth=1, color='b', alpha=0.5)
    ax.add_patch(rect)

    print(f"Plotting box: Min=({min_x}, {min_y}), Max=({max_x}, {max_y})")
def plot_sphere(ax, sphere):
    center = sphere["Center"]
    radius = sphere["Radius"]
    translation = sphere["OffsetTranslation"]

    print(f"Sphere translation: {translation}")

    transformed_center = translate_point(center[0], center[1], translation[0], translation[1])

    print(f"Original center: {center}, Transformed center: {transformed_center}")

    circle = patches.Circle(transformed_center, radius, linewidth=1, color='b', alpha=0.5)
    ax.add_patch(circle)

def plot_cylinder(ax, cylinder):
    x1, y1 = cylinder["CenterA"]
    x2, y2 = cylinder["CenterB"]
    radius = cylinder["Radius"]
    rotation = cylinder["OffsetRotation"]
    translation = cylinder["OffsetTranslation"]

    x1, y1 = apply_transformations(x1, y1, rotation, translation)
    x2, y2 = apply_transformations(x2, y2, rotation, translation)

    if rotation[0] == 90 or rotation[0] == -90:
        # Plotting the circular face of the cylinder
        circle = patches.Circle((x1, y1), radius, linewidth=1, color='r', alpha=0.5)
        ax.add_patch(circle)
    else:
        # Plotting the rectangular side view of the cylinder
        angle = np.arctan2(y2 - y1, x2 - x1)
        perp_angle = angle + np.pi / 2
        dx = radius * np.cos(perp_angle)
        dy = radius * np.sin(perp_angle)
        rect_points_x = [x1 - dx, x2 - dx, x2 + dx, x1 + dx]
        rect_points_y = [y1 - dy, y2 - dy, y2 + dy, y1 + dy]
        ax.fill(rect_points_x, rect_points_y, 'r', alpha=0.5)

def plot_shapes(capsules, boxes, spheres, cylinders):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)

    for capsule in capsules:
        plot_capsule(ax, capsule)
    
    for box in boxes:
        plot_box(ax, box)
    
    for sphere in spheres:
        plot_sphere(ax, sphere)
    
    for cylinder in cylinders:
        plot_cylinder(ax, cylinder)

    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title(f'Wonder Collision Viewer - {file_name}')
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.show()

root = tk.Tk()
root.title("Text File Reader")

text_widget = tk.Text(root, wrap="word", width=40, height=10)
text_widget.pack(pady=10)

open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack(pady=10)

root.mainloop()
