from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import subgraph
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import matplotlib
import time
matplotlib.use('Agg')
plt.style.use('dark_background')

V_PRIME = 1.0005
D_MAX = 1000
D_B = 300

MAX_GRAVITY = 100

NROW = 3
NCOL = 2
NGRAPHS = NROW * NCOL

NROW2 = 3
NCOL2 = 1
NGRAPHS2 = NROW2 * NCOL2

ROTATION_PLOTS = [1,2,3] # note: start index = 1

def priceWithDebt(v, d) -> float:
    ## c ranges between -.5 and .5.
    c = -.5 + (1 * d/D_MAX)
    c = np.where(v <= V_PRIME, c,-c)
    return -(1+c) * MAX_GRAVITY * ((v-V_PRIME)**2) + MAX_GRAVITY

def debtLevelWithPrice(d: float, v: float) -> float:
    ## low p, D_B = 600,
    # optimal p, d_b = 300s
    ## high p, D_B = 600
    newD_B = D_B + D_B * abs((abs(v) - 1))
    x = newD_B/D_MAX
    d = d/D_MAX
    c = (1 - v) * .7
    # c ranges from -1 to 1
    c = np.where(d < x, -c, c)
    return -(1 + c) * MAX_GRAVITY * (d - x) ** 2 + MAX_GRAVITY

def debtLevelWithL2SR(d: float, l: float) -> float:
    newD_B = D_B
    x = newD_B/D_MAX
    d = d/D_MAX
    c = (1 - l) * .7
    # c ranges from -1 to 1
    c = np.where(d < x, -c, c)
    return -(1 + c) * MAX_GRAVITY * (d - x) ** 2 + MAX_GRAVITY

def L2SRAtDebtLevel(l: float, d: float) -> float:
    d = (-0.5+ (d/D_MAX))
    return (d) * (l)

def plotDebtXPrice(ax, d:float, v:float) -> plt.axes:
    NUM = 10
    v_values = np.linspace(0, 2, NUM)
    d_values = np.linspace(0, D_MAX, NUM)
    V, D = np.meshgrid(v_values, d_values)
    Z = priceWithDebt(V, D) + debtLevelWithPrice(D,V)
    ax.set_xlabel('V')
    ax.set_ylabel('D')
    ax.set_ylim(D_MAX,0)
    ax.grid(False)
    ax.axis('off')

    # title plot:
    ax.set_zlabel('Gravity')
    ax.set_title('Price x Pod Rate')
    ax.plot_wireframe(V, D, Z, edgecolor='blue')
    ax.scatter(v, d, priceWithDebt(v, d) + debtLevelWithPrice(d, v), color='red', s=50, label='Dot')
    V = None
    D = None
    Z = None

def plotPriceXL2SR(ax, v:float, l:float) -> plt.axes:
    NUM = 10
    v_values = np.linspace(0, 1, NUM)
    l_values = np.linspace(0, 1, NUM)
    V, L = np.meshgrid(v_values, l_values)
    Z = priceXL2SR(V, L)

    # Plot the dot
    ax.scatter(v, l, priceXL2SR(v, l), color='red', s=50, label='Dot')
    ax.set_xlabel('V')
    ax.set_ylabel('L')
    ax.set_zlim(0,0.8)

    # title plot:
    ax.set_title('Price x L2SR')
    ax.set_zlabel('Gravity')
    ax.grid(False)
    ax.axis('off')
    ax.plot_wireframe(V, L, Z, edgecolor='blue')
    V = None
    L = None
    Z = None

def priceXL2SR(V, L) -> plt.axes:
    return ((-V**2 + 0.5*V + 0.5) * L) + (-(V-0.5)**2 + 0.5*(V-0.5) + 0.5) * (1 - L)
        
def plotDebtLevelXL2SR(ax, d:float, l:float) -> plt.axes:
    NUM = 10
    d_values = np.linspace(0, D_MAX, NUM)
    l_values = np.linspace(0, 1, NUM)
    D, L = np.meshgrid(d_values, l_values)
    Z = normalize(debtLevelWithL2SR(D, L)) + normalize(L2SRAtDebtLevel(L,D))
    ax.set_xlabel('D')
    ax.set_ylabel('L')
    ax.set_ylim(1,0)
    ax.grid(False)
    ax.axis('off')

    # title plot:
    ax.set_zlabel('Gravity')
    ax.grid(False)
    ax.axis('off')
    ax.set_title('Debt x L2SR')
    ax.plot_wireframe(D, L, Z, edgecolor='blue')
    z = Z[10 - int(l * 10)][int((1000 - d)/100)]
    ax.scatter(d, l, z, color='red', s=50, label='Dot')
    D = None
    Z = None
    L = None

def plotPriceXTime(ax, v) -> plt.axes:
    x = np.linspace(len(v)/24, 0, len(v))
    # set y axis to be between 0.90 and 1.02:
    ax.set_ylim(min(v) * 0.99,max(v) * 1.01)
    # set x axis to be in days:
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.set_title('Price (1w)')
    ax.plot(x, v)
    x = None

def plotPodRateXTime(ax, d) -> plt.axes:
    x = np.linspace(len(d)/24, 0, len(d))
    ax.set_title('Pod Rate (1w)')
    # set y axis as %:
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals = 0))
    ax.yaxis.set_major_locator(mtick.MaxNLocator(nbins=4))

    # set x and y labels:
    ax.set_xlabel('Time')
    ax.set_ylabel('Pod Rate')
    ax.plot(x, d)
    x = None

def plotL2SRXTime(ax, l) -> plt.axes:
    x = np.linspace(len(l)/24, 0, len(l))
    ax.set_title('L2SR (1w)')
    ax.set_xlabel('Time')
    ax.set_ylabel('L2SR')
    ax.plot(x, l)
    x = None

def plotBeanSupplyXTime(ax, mcap) -> plt.axes:
    x = np.linspace(len(mcap)/24, 0, len(mcap))
    ax.set_title('Supply (1w)')
    ax.yaxis.set_major_locator(mtick.MaxNLocator(nbins=4))
    ax.set_xlabel('Time')
    ax.set_ylabel('Supply')
    ax.plot(x, mcap)
    x = None

def plotStalkFarmers(ax, stalk) -> plt.axes:
    # remove the first stalk in the array:
    stalk = stalk[1:]
    # rotate pie graph:
    ax.pie(stalk, startangle=90)
    ax.set_title('Stalk Distribution')

def plotDepositedBdv(ax, bdv, _labels) -> plt.axes:
    ax.pie(bdv, startangle=90, labels=None)
    ax.legend(labels=_labels)
    ax.set_title('BDV Distribution')

def normalize(x: np.array) -> np.array:
    return (x - np.min(x)) / (np.max(x) - np.min(x))

def rotate(angle):
    currentFig = plt.gcf()
    axList = currentFig.axes
    for axes in ROTATION_PLOTS:
        axList[axes - 1].view_init(30, angle)

def createPlots() -> plt.Figure:
    data, latestSeason = subgraph.getBeanstalkData()
    fig1 = plt.figure(figsize=(14, 15))

    ## static plots:
    axes = []
    for i in range(1, NGRAPHS + 1):
        ax = fig1.add_subplot(NROW, NCOL, i)
        axes.append(ax)
    plotPriceXTime(axes[0], data[3])
    plotPodRateXTime(axes[1], data[1] * 100)
    plotL2SRXTime(axes[2], np.linspace(1, 1, 100))
    plotBeanSupplyXTime(axes[3], data[2] / 1000000e6)
    plotDepositedBdv(axes[4], list(data[5].values()), list(data[5].keys()))
    plotStalkFarmers(axes[5], data[4])
    plt.tight_layout()
    plt.savefig('static/chart.png')

    ## dynamic plots:
    d = 800
    l = 1
    v = 1
    fig2 = plt.figure(figsize=(7, 20))
    axes = [] 
    for i in range(1, NGRAPHS2 + 1):
        ax = fig2.add_subplot(NROW2, NCOL2, i, projection='3d')
        axes.append(ax)
    plotPriceXL2SR(axes[0], 0.5, l)
    plotDebtLevelXL2SR(axes[1], d, l)
    plotDebtXPrice(axes[2], d, v)
    plt.tight_layout()
    rot_animation = FuncAnimation(fig2, rotate, frames=np.arange(0,361,2), interval=100)
    rot_animation.save('static/chart.gif', dpi = 100)
    
if __name__ == "__main__":
    createPlots()
    

