import gradio
from gradio import Interface

def square(x):
    return x * x

iface = Interface(square,
                   inputs=gradio.inputs.Slider(0, 100),
                   outputs=gradio.outputs.Textbox())
iface.launch()