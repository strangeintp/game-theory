'''
Created on Mar 4, 2014

@author: stran_000
'''

NUM_OF_AGENTS = 1000
Initial_D_Fraction = 0.5  # number of agents who play a 'D' strategy instead of a 'C'
Edge_Density = 0.01

from random import random
from random import choice
import experiment

# Graph types
ER = 0 #Erdos-Renyi

C = 0
D = 1

#game payoffs
CC = (10,10)
CD = (2,6)  # CD, DC values revised for 3rd experiment
DC = (6,2)
DD = (4,4)

class Game(object):

    def __init__(self):
        pass

    def play(self, actor1, actor2):
        (p1, p2) = self.payoffs[actor1.choose()][actor2.choose()]
        return (p1, p2)
    
    def playWithChoices(self, choice1, choice2):
        (p1, p2) = self.payoffs[choice1][choice2]
        return (p1, p2)
    
class GraphGameAgent(object):
    
    def __init__(self, strategy=C):
        self.strategy = strategy
        self.strategy_memory = {} # a dictionary, indexed by connected agent, of previous strategies played by others
        self.score = 0
    
    def __copy__(self):
        agent = GraphGameAgent(self.strategy)
        agent.strategy_memory = self.strategy_memory
        return agent
        
    def getAgentsInNetwork(self):
        return self.strategy_memory.keys()
    
    def connectTo(self, other):
        self.strategy_memory[other] = C
        
    def updateMemory(self, other):
        self.strategy_memory[other] = other.strategy
        
    def award(self, amount):
        self.score += amount
        
    def choose(self):
        return self.strategy
    
    def updateStrategy(self, game):
        # virtually play 'C' against others, based on memory
        payoff_sum_C = 0
        for other in self.strategy_memory.keys():
            (p1, p2) = game.playWithChoices(C,self.strategy_memory[other])
            payoff_sum_C += p1
        # virtually play 'D' against others, based on memory
        payoff_sum_D = 0
        for other in self.strategy_memory.keys():
            (p1, p2) = game.playWithChoices(D,self.strategy_memory[other])
            payoff_sum_D += p1
        # compare the two virtual payoffs and revise strategy
        if payoff_sum_C > payoff_sum_D:
            self.strategy = C
        elif payoff_sum_C < payoff_sum_D:
            self.strategy = D
        else:
            pass  # do nothing in case of tie
        
class StagHunt(Game):
    
    def __init__(self, CC, CD, DC, DD): # pass in 2-tuples of payoffs for playing strategy combinations
        self.payoffs = [[CC, CD], [DC, DD]] 

class GraphGameSim(object):
    '''
    classdocs
    '''

    @staticmethod
    def generateNewAgentNetwork(d_fraction):
        agents = []
        for i in range(NUM_OF_AGENTS):
            if random() < d_fraction:
                strategy = D
            else:
                strategy = C
            agents.append(GraphGameAgent(strategy))
        
        # generate the graph
        for ego in agents:
            for other in agents:
                if not other==ego: # no self-loops
                    if random() < Edge_Density:
                        ego.connectTo(other)
        
        return agents

    def __init__(self, agents, graph_type = ER):
        '''
        Constructor
        '''        
        self.game = StagHunt(CC, CD, DC, DD)
        
        # initialize the agent set
        self.agents = agents
        self.steps = 0
        
    def step(self):  # returns a stop condition
        # choose an agent for random activation
        ego = choice(self.agents)
        
        # play all agents in network
        alters = ego.getAgentsInNetwork()
        for other in alters:
            (p1, p2) = self.game.play(ego, other)
            ego.award(p1)
            other.award(p2)
        # update memories of strategies played
        for other in alters:
            ego.updateMemory(other)
            other.updateMemory(ego)
        
        # choose 'best reply' based on most recent memory
        ego.updateStrategy(self.game)
        
        self.steps += 1
        f = self.getCFraction()
        if f==0.0 or f==1.0:
            return True
        else:
            return False
        
    def getCFraction(self):
        D_count = 0
        for agent in self.agents:
            D_count += agent.strategy
        return (1 - (D_count/NUM_OF_AGENTS))

class GGSExperiment(experiment.Experiment):
    
    def __init__(self):
        super().__init__()
        self.agents = None
        self.original_agents = None
        self.b_reuse_agents = False
        self.d_fracton = Initial_D_Fraction
        
    def reuseAgents(self, value = False):
        self.b_reuse_agents = value
        return value
    
    def setInitialDFraction(self, value=Initial_D_Fraction):
        self.d_fraction = value
        return value

    def initiateSim(self):
        if (not self.b_reuse_agents):
            self.agents = GraphGameSim.generateNewAgentNetwork(self.d_fraction)
        else:
            if not self.original_agents:
                self.original_agents = GraphGameSim.generateNewAgentNetwork(self.d_fraction)
            self.agents = []
            for agent in self.original_agents:
                self.agents.append(agent.__copy__())
            
        self.sim = GraphGameSim(self.agents)
        self.steps = 0
        self.stop_condition = False

    def stepSim(self):
        self.stop_condition = self.sim.step()
        self.steps += 1

    def getSteps(self):
        return self.steps
    
    def getCFraction(self):
        return self.sim.getCFraction()

    def stopSim(self):
        return self.stop_condition

    def setupOutputs(self):
        self.addOutput(self.getSteps, "runtime", "%5d")
        self.addOutput(self.getCFraction, "f_c", "%1.1f")

    def setupExperiment(self):
        self.Name = "Graph Game Experiment"
        self.comments = "Vary initial d_fraction between [0,1]"
        self.setupParameters()
        self.job_repetitions = 20

    def setupParameters(self):
        self.addParameter(self.reuseAgents, [False])
        self.addParameter(self.setInitialDFraction, [0.05*i for i in range(21)])
        
class GGSExperiment2(GGSExperiment):
    
    def __init__(self):
        super().__init__()
        
    def setupExperiment(self):
        self.Name = "Graph Game Experiment 2"
        self.comments = "Vary initial d_fraction between [0.2,0.3]"
        self.setupParameters()
        self.job_repetitions = 20

    def setupParameters(self):
        self.addParameter(self.reuseAgents, [False])
        self.addParameter(self.setInitialDFraction, [0.2 + 0.01*i for i in range(11)])
        
class GGSTest(GGSExperiment):
    
    def __init__(self):
        super().__init__()
        
    def setupExperiment(self):
        self.Name = "Graph Game Sim test"
        self.comments = "Test robustness of the model by rerunning with the same initial agent set and network"
        self.setupParameters()
        self.job_repetitions = 20

    def setupParameters(self):
        self.addParameter(self.reuseAgents, [True, False])
        self.addParameter(self.setInitialDFraction, 0.25)

if __name__ == "__main__":
    GGSExperiment().run()