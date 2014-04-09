from random import random
from random import shuffle
import utility as u

HEADS=0
TAILS=1

MEM_ALL = -1
MEM_NONE = 0

verbose = True

class Game(object):

    def __init__(self):
        pass

    def play(self, actor1, actor2):
        (p1, p2) = self.payoffs[actor1.choose()][actor2.choose()]
        return (p1, p2)
    
    def playWithChoices(self, choice1, choice2):
        (p1, p2) = self.payoffs[choice1][choice2]
        return (p1, p2)
class CoordinationGame(Game):

    def __init__(self, h=2, t=1):
        '''
        'h' is the payoff for both players choosing heads
        't' is the payoff for both players choosing tails
        '''
        self.payoffs = [[(h,h), (0,0)], [(0,0), (t,t)]]

class Chicken(Game):

    def __init__(self, st=4, sw=1, st_st=0, sw_sw=2):
        self.payoffs = [[(st_st,st_st), (st,sw)], [(sw,st), (sw_sw, sw_sw)]]

class PrisonersDilemma(Game):

    def __init__(self, T=5, R=3, P=1, S=0):
        self.payoffs = [[(R,R), (S,T)], [(T,S), (P,P)]]

class Agent(object):

    def __init__(self, memory=MEM_ALL):
        self.weight = {}
        #initialize the 'memory' with half heads and half tails
        self.weight[HEADS] = max(1, memory)
        self.weight[TAILS] = max(1, memory)
        self.memory = memory
        self.choice = -1
        self.score = 0

    def choose(self):
        roll = random()*(self.weight[HEADS] + self.weight[TAILS])
        if roll < self.weight[HEADS]:
            self.choice = HEADS
        else:
            self.choice = TAILS
        return self.choice

    def payoff(self, amount):
        self.score += amount
        if self.memory==MEM_ALL:  #the choice lottery will use all of the past history
            self.weight[self.choice] += amount
        elif self.memory > 0:
            # a short memory means recent choices will carry more weight
            self.weight[self.choice] += amount
            total_weight = self.weight[HEADS] + self.weight[TAILS]
            self.weight[HEADS] *= self.memory/(total_weight)
            self.weight[TAILS] *= self.memory/(total_weight)
        #otherwise, choice lottery will remain uniformly random

    def getHFraction(self):
        return self.weight[HEADS]/(self.weight[HEADS] + self.weight[TAILS])


class Sim(object):

    def __init__(self, num_agents=100, memory=MEM_NONE, game = CoordinationGame(2,1)):
        self.agent_set = [Agent(memory=memory) for i in range(num_agents)]
        self.game = game
        self.time = 0
        self.mean = 0
        self.std = 0
        self.minscore = 0
        self.maxscore = 0
        self.minHfraction = 0
        self.maxHfraction = 0
        self.medHfraction = 0
        self.avgHfraction = 0
        self.minscoreHfraction = 0
        self.maxscoreHfraction = 0
        self.medscoreHfraction = 0
        self.sumHfractions = 0

    def step(self):
        shuffle(self.agent_set)
        self.oldHfractions = [agent.getHFraction() for agent in self.agent_set]
        i=0
        while i<len(self.agent_set):
            a1 = self.agent_set[i]
            i += 1
            a2  =self.agent_set[i]
            i += 1
            (p1, p2) = self.game.play(a1, a2)
            a1.payoff(p1)
            a2.payoff(p2)
        self.time += 1

    def computeMetrics(self):
        scores = [agent.score for agent in self.agent_set]
        self.mean = u.mean(scores)
        self.std = u.popStdDev(scores)
        self.minscore = min(scores)
        self.medscore = u.median(scores)
        self.maxscore =max(scores)
        agents_sorted = sorted(self.agent_set, key=lambda agent:agent.score)
        self.minscoreHfraction = agents_sorted[0].getHFraction()
        self.maxscoreHfraction = agents_sorted[-1].getHFraction()
        self.medscoreHfraction = agents_sorted[int(len(self.agent_set)/2)].getHFraction()
        hfractions = [agent.getHFraction() for agent in self.agent_set]
        self.medHfraction = u.median(hfractions)
        self.avgHfraction = u.mean(hfractions)
        self.minHfraction = min(hfractions)
        self.maxHfraction = max(hfractions)
        self.sumHfractions = sum(hfractions)
        dhfractions = [abs(hfractions[i] - self.oldHfractions[i]) for i in range(len(hfractions))]
        self.sumdH = sum(dhfractions)

    def getScoreStdDev(self):
        return self.std

    def getScoreMean(self):
        return self.mean

    def getMaxScore(self):
        return self.maxscore

    def getMinScore(self):
        return self.minscore

def doPart_A():
    sim = Sim(memory=5)
    stop = False
    steps = 0
    print("step, mean, std, min, max")
    convergence = 0.01
    while not stop:
        steps += 1
        sim.step()
        sim.computeMetrics()
        mean = sim.getScoreMean()/steps
        std  = sim.getScoreStdDev()/steps
        maxscore = sim.getMaxScore()/steps
        minscore = sim.getMinScore()/steps
        if steps%25==0:
            print("%d\t%5.2f\t%5.2f\t%2.2f\t%2.2f"%(steps, mean, std, minscore, maxscore ))
        stop = (std < convergence*mean and steps > 1) or steps > 10000
    print("***    FINAL RESULTS    ***")
    print("%d\t%5.2f\t%5.2f\t%2.2f\t%2.2f"%(steps, mean, std, minscore, maxscore ))

if __name__ == "__main__":
    doPart_A()
