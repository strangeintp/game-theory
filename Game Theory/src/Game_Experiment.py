import experiment as exp
import games as game


class Game_Experiment(exp.Experiment):

    def __init__(self):
        super().__init__()
        self.num_agents = 0
        self.agent_memory = 100
        self.convergence = 0.0001
        self.lastsumHfractions = 0

    def setNumAgents(self, num_agents):
        self.num_agents = num_agents
        return num_agents

    def setMemory(self, agent_memory):
        self.agent_memory = agent_memory
        return agent_memory

    def initiateSim(self):
        self.sim = game.Sim(self.num_agents, self.agent_memory)
        self.steps = 0

    def stepSim(self):
        self.sim.step()
        self.steps += 1
        self.sim.computeMetrics()

    def getSteps(self):
        return self.steps

    def stopSim(self):
        stop = False
        if self.steps>1:         
            stop = self.sim.minHfraction==self.sim.maxHfraction
            stop = stop or self.sim.sumdH < self.convergence
        return stop

    def getMean(self):
        return self.sim.mean/self.steps

    def getStd(self):
        return self.sim.std/self.steps

    def getMin(self):
        return self.sim.minscore/self.steps

    def getMax(self):
        return self.sim.maxscore/self.steps

    def getMinscoreHFraction(self):
        return self.sim.minscoreHfraction

    def getMaxscoreHFraction(self):
        return self.sim.maxscoreHfraction

    def getMedscoreHFraction(self):
        return self.sim.medscoreHfraction

    def getAvgHFraction(self):
        return self.sim.avgHfraction

    def getMedHFraction(self):
        return self.sim.medHfraction

    def getMinHFraction(self):
        return self.sim.minHfraction

    def getMaxHFraction(self):
        return self.sim.maxHfraction

    def setupOutputs(self):
        #######################################################################
        """
        Section 4 - Add getter methods, names, and string formats so the automater
        can retrieve and record metrics from your simulation.

        #template
        self.addOutput(getterFunction, output_name, output_format)

        #Example:
        self.addOutput(getAveragePopulation, "Avg Pop.", "%8.4f")
        # getAveragePopulation() returns the average population of the sim run,
        # and the header "Avg Pop." will be written to the file
        """
        self.addOutput(self.getSteps, "runtime", "%5d")
        self.addOutput(self.getMean, "mean score", "%1.4f")
        self.addOutput(self.getStd, "sdv score", "%1.4f")
        self.addOutput(self.getMin, "min score", "%2.2f")
        self.addOutput(self.getMax, "max score", "%2.2f")
        self.addOutput(self.getMinscoreHFraction, "min score H", "%1.4f")
        self.addOutput(self.getMaxscoreHFraction, "max score H", "%1.4f")
        self.addOutput(self.getMedscoreHFraction, "med score H", "%1.4f")
        self.addOutput(self.getAvgHFraction, "avg H", "%1.4f")
        self.addOutput(self.getMedHFraction, "med H", "%1.4f")
        self.addOutput(self.getMinHFraction, "min H", "%1.4f")
        self.addOutput(self.getMaxHFraction, "max H", "%1.4f")

class CoordGameExperiment(Game_Experiment):

    def __init__(self):
        super(CoordGameExperiment, self).__init__()

    def setupExperiment(self):
        self.Name = "Coordination Game Experiment, Part D"
        self.comments = "1000 agents; all learning methods.  Higher resolution between [2,4]."
        self.setupParameters()
        self.job_repetitions = 10

    def setupParameters(self):
        self.addParameter(self.setNumAgents, [1000])
        self.addParameter(self.setMemory, [0.5*i for i in range(21)] + [game.MEM_ALL])

class PD(Game_Experiment):

    def __init__(self):
        super(PD, self).__init__()
        self.simgame = game.PrisonersDilemma()

    def initiateSim(self):
        self.sim = game.Sim(self.num_agents, self.agent_memory, self.simgame)
        self.steps = 0

    def setupExperiment(self):
        self.Name = "Prisoners Dilemma Game Experiment"
        self.comments = "With adaptive agents"
        self.setupParameters()
        self.job_repetitions = 10

    def setupParameters(self):
        self.addParameter(self.setNumAgents, [100])
        self.addParameter(self.setMemory, [0, 1, 3, 5, 10, 20, 100, 1000, game.MEM_ALL])

        
if __name__ == '__main__':
    CoordGameExperiment().run()
