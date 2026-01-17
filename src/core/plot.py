import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")




class PlotLanchester:
    def plot(self, data):
        plt.figure()

        for unit_type, results in data.items():
            xs = []
            ys = []

            for N in sorted(results.keys()):
                values = results[N]
                if not values:
                    continue

                xs.append(N)
                ys.append(sum(values) / len(values))

            if xs:
                plt.plot(xs, ys, label=unit_type.name)

        plt.xlabel("Nombre initial d'unités (N)")
        plt.ylabel("Pertes moyennes du vainqueur")
        plt.title("Expérience de Lanchester")
        plt.legend()
        plt.grid(True)
        plt.show()


# ============================================================
# REGISTRY
# ============================================================

PLOTTERS = {
    "lanchester": PlotLanchester,
    "plotlanchester": PlotLanchester,
}


def get_plotter(name: str):
    try:
        return PLOTTERS[name.lower()]()
    except KeyError:
        raise ValueError(f"Plotter inconnu : {name}")
