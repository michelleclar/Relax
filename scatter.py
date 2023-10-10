import matplotlib.pyplot as plt
import numpy as np



if __name__ == '__main__':
    N = 100
    x = np.random.rand(N)
    y = np.random.rand(N)
    plt.scatter(x, y)
    plt.show()