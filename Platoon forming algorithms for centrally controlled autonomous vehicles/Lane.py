#class to generate lanes and estimate their parameters for when new cars arrive
import numpy as np
import matplotlib.pyplot as plt


class Lane:

    def __init__(self, n, times, b):
        self.n = n
        self.times = times
        self.b = b
        self.len = np.alen(times)
        self.deltas = np.zeros(self.len)
        self.deltas[0] = times[0]
        self.deltas[1:] = times[1:] - times[:-1]
        self.offDeltas = self.deltas - b
        self.alpha = 1 - np.mean(self.offDeltas == 0)
        muSamples = 20
        muPoints = np.zeros(muSamples)
        for i in range(np.alen(muPoints)):
            t = (i + 1) * (np.amax(self.deltas) / 2) / np.alen(muPoints)
            muPoints[i] = np.log(-self.alpha / (np.mean(self.offDeltas <= t) - 1)) / t
        self.mu = np.mean(muPoints)
        self.muSTD = np.std(muPoints)
        self.muCI = 1.96 * self.muSTD / np.sqrt(muSamples)

    def testAlphaMu(self):
        plt_points = 100
        sim_input = np.linspace(0, np.amax(self.offDeltas), plt_points)
        sim_dist = 1 - self.alpha * np.exp(-self.mu * sim_input)
        plt.hist(self.offDeltas, bins=plt_points, label='samples', cumulative=True,
                 weights=[1 / self.len] * self.len)
        plt.plot(sim_input, sim_dist, alpha=0.8, label='simulated', linewidth=4)
        plt.title('Comparison of samples with simulated alpha and mu for lane ' + str(self.n))
        plt.legend()
        plt.show()

    def printAlphaMu(self):
        out = 'For lane ' + str(self.n) + ', alpha = ' + str(self.alpha) + ' and mu = ' + str(self.mu) + '±' + str(self.muCI)
        print(out)

