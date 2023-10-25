import matplotlib.pyplot as plt
import gradio as gr
import numpy as np

def test_write_cvs():
    num_points = 1000
    x_range = (1, 29)
    y_range = (30, 50)
    points = generate_random_points(num_points, x_range, y_range)
    # print(points)
    with open("./point/point", 'a') as f:
        for point in points:
            print(point)

            f.write(f'{point[0]},{point[1]} ')


def generate_random_points(num_points, x_range, y_range):
    x = np.random.rand(num_points) * (x_range[1] - x_range[0]) + x_range[0]
    y = np.random.rand(num_points) * (y_range[1] - y_range[0]) + y_range[0]
    return np.stack([x, y], axis=1)


def test_read():
    with open("./point/point", 'r') as f:

        for line in f:
            chunks = line.split(" ")
            x = []
            y = []
            for chunk in chunks:
                if chunk == "":
                    break
                point = chunk.split(",")
                x.append(point[0])
                y.append(point[1])
            print(x)
            print(y)

def generate_scatterplot(points):
    x_values = []
    y_values = []

    # Split the input points into individual coordinates
    point_list = points.strip().split(" ")
    for point in point_list:
        if point == "":
            break
        x_coord, y_coord = map(float, point.split(","))
        x_values.append(x_coord)
        y_values.append(y_coord)

    # Create the scatterplot
    plt.scatter(x_values, y_values)
    plt.title("Scatterplot")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.tight_layout()

    plot_filename = "scatterplot.png"
    plt.savefig(plot_filename)
    plt.close()

    return plot_filename

# Create a Gradio interface
iface = gr.Interface(
    fn=generate_scatterplot,
    inputs="text",
    outputs="image",
    live=True,
    title="Scatterplot Generator",
    description="Enter points in the format 'x1,y1 x2,y2 x3,y3 ...'",
)
# Create a Gradio interface
if __name__ == "__main__":
    iface.launch()