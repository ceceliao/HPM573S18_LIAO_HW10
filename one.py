import scr.RandomVariantGenerators as rndClasses
from enum import Enum
import scr.EconEvalClasses as EconCls
import datainput as data

class HealthStats(Enum):
    """ health states of patients with risk of stroke """
    WELL = 0
    STROKE = 1
    POST_STROKE = 2
    DEATH = 3

class Therapies (Enum):
    No=0
    Yes=1


class Patient:
    def __init__(self, id, Therapies):
        self._healthstat=0
        self._id = id
        self._rng = None
        self._therapies = Therapies
        self._stroke=0
        self._totalDiscountCost=0
        self._totalDiscountUtility=0



    def simulate(self, sim_length):
        """ simulate the patient over the specified simulation length """

        # random number generator for this patient
        self._rng = rndClasses.RNG(self._id)

        k = 0  # current time step

        # while the patient is alive and simulation length is not yet reached
        while self._healthstat !=3 and k  < sim_length:
            # find the transition probabilities of the future states
            trans_probs = data.TRANS[self._therapies][self._healthstat]
            # create an empirical distribution
            empirical_dist = rndClasses.Empirical(trans_probs)
            # sample from the empirical distribution to get a new state
            # (returns an integer from {0, 1, 2, ...})
            new_state_index = empirical_dist.sample(self._rng)
            if self._healthstat==1:
                self._stroke+=1
            #caculate cost and utality
            cost=data.TRANS_COST[self._therapies][self._healthstat]
            utility=data.TRANS_UTILITY[self._therapies][self._healthstat]
            # update total discounted cost and utility (corrected for the half-cycle effect)
            self._totalDiscountCost += \
                EconCls.pv(cost, data.Discount_Rate, k + 1)
            self._totalDiscountUtility += \
                EconCls.pv(utility, data.Discount_Rate, k + 1)
            # update health state
            self._healthstat =new_state_index[0]
            # increment time step
            k += 1


    def get_stroke_time(self):

        return self._stroke

    def get_total_utility(self):
        return self._totalDiscountUtility

    def get_total_cost(self):
        return self._totalDiscountCost

class Cohort:
    def __init__(self,id,therapy):
        self._initial_pop_size=data.POP_SIZE
        self._id=id
        self._therapy=therapy
        self._stroke=[]
        self._totaldiscountedcost=[]
        self._totaldiscountedutility=[]

    def simulate(self):
        for patient in range(self._initial_pop_size):
            patient=Patient(self._id*self._initial_pop_size+i,self._therapy)
            patient.simulate(data.SIM_LENGTH)
            self._stroke.append(patient.get_stroke_time())
            self._totaldiscountedcost.append(patient.get_total_cost())
            self._totaldiscountedutility.append(patient.get_total_utility())


    def get_stroke_time(self):
        return self._stroke

    def get_total_utility(self):
        return self._totaldiscountedutility

    def get_total_cost(self):
        return self._totaldiscountedcost


cohort_ONE=Cohort(1,Therapies.No.value)
cohort_ONE.simulate()

cohort_TWO=Cohort(2,Therapies.Yes.value)
cohort_TWO.simulate()

cohort_ONE.get_total_cost()
cohort_ONE.get_total_utility()

cohort_TWO.get_total_cost()
cohort_TWO.get_total_utility()


print('the discounted total cost in patients with drug',cohort_ONE.get_total_cost())
print('the discounted utility in patients with drug', cohort_ONE.get_total_utility())

print('the discounted total cost in patients without drug',cohort_TWO.get_total_cost())
print('the discounted total cost in patients without drug', cohort_TWO.get_total_utility())
