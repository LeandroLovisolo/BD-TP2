import matplotlib.pyplot as plt

class Plot:
    def __init__(self, output_path=None):
        plt.rcParams['text.latex.preamble']=[r'\usepackage{lmodern}']
        plt.rcParams.update({'text.usetex':         True,
                             'text.latex.unicode':  True,
                             'font.family':         'lmodern',
                             'font.size':           10,
                             'axes.titlesize':      10,
                             'legend.fontsize':     10,
                             'legend.labelspacing': 0.2})

        fig = plt.figure()
        fig.set_size_inches(6, 4)

        self.do_plot(plt)

        plt.grid(True)
        plt.tight_layout()

        if output_path is None:
            plt.show()
        else:
            plt.savefig(output_path, dpi=1000, box_inches='tight')

    def do_plot(self, plt):
        raise NotImplementedError
