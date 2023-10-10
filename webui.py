import io
import matplotlib.pyplot as plt
import gradio as gr
import numpy as np

# Define a function to generate the scatterplot
def generate_scatterplot(x, y, title="Scatterplot", x_label="X", y_label="Y"):
    N = 100
    _x = np.random.rand(N)
    _y = np.random.rand(N)
    plt.scatter(_x, _y)
    # plt.scatter(x,y)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    plt.tight_layout()

    # Save the plot as an image
    plot_filename = "scatterplot.png"
    plt.savefig(plot_filename)
    plt.close()

    # Return the filename of the generated plot
    return plot_filename

# Create a Gradio interface
if __name__ == '__main__':

    interface = gr.Interface(
        fn=generate_scatterplot,
        inputs=["text", "text", "text", "text"],  # x, y, title, x_label
        outputs="image",
        live=True
    )
    interface.launch()

