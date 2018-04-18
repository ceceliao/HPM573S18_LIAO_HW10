import scr.RandomVariantGenerators as rndClasses
import scr.StatisticalClasses as Stat
from enum import Enum
import scr.EconEvalClasses as EconCls
import scr.FormatFunctions as Format
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
    def __init__(self, id, therapies):
        """ initiates a patient
        :param id: ID of the patient
        :param parameters: parameter object
        """
        self._healthstat=0
        self._id = id
        # random number generator for this patient
        self._rng = None
        self._therapies = therapies
        self._stroke=0
        self._totalDiscountUtility=0
        self._totalDiscountCost=0


    def simulate(self, sim_length):
        """ simulate the patient over the specified simulation length """

        # random number generator for this patient
        self._rng = rndClasses.RNG(self._id)

        k = 0  # current time step

        # while the patient is alive and simulation length is not yet reached
        while self._healthstat!=3 and k  < sim_length:
            # find the transition probabilities of the future states
            trans_probs = data.TRANS[self._therapies][self._healthstat]
            # create an empirical distribution
            empirical_dist = rndClasses.Empirical(trans_probs)
            # sample from the empirical distribution to get a new state
            # (returns an integer from {0, 1, 2, ...})
            new_state_index = empirical_dist.sample(self._rng)
            if  self ._healthstat == 1 :
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
    def __init__(self,id,therapies):
        self._initial_pop_size=data.POP_SIZE
        self._id=id
        self._therapies=therapies
        self._stroke=[]
        self._totaldiscountedcost=[]
        self._totaldiscountedutility=[]

    def simulate(self):
        for a in range(self._initial_pop_size):
            patient=Patient(self._id*self._initial_pop_size+a,self._therapies)
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


def print_comparative_cost(sim_yes, sim_no):

    increase = Stat.DifferenceStatIndp(
        name='change in cost',
        x=sim_yes,
        y_ref=sim_no
    )
    # estimate and CI
    estimate_CI = Format.format_estimate_interval (
        estimate=increase.get_mean(),
        interval=increase.get_t_CI(alpha=0.05), deci=2
    )
    print("Average change in the expected discounted cost and {:.{prec}%} confidence interval:".format(1 - 0.05, prec=0),
          estimate_CI)

def print_comparative_utility(sim_yes, sim_no):

    increase = Stat.DifferenceStatIndp(
        name='change in utility',
        x=sim_yes,
        y_ref=sim_no
    )
    # estimate and CI
    estimate_CI = Format.format_estimate_interval (
        estimate=increase.get_mean(),
        interval=increase.get_t_CI(alpha=0.05),deci=2

    )
    print("Average change in the expected discounted utility and {:.{prec}%} confidence interval:".format(1 - 0.05, prec=0),
          estimate_CI)

def print_comparative_stroke(sim_yes, sim_no):

    increase = Stat.DifferenceStatIndp(
        name='change in stroke',
        x=sim_no,
        y_ref=sim_yes
    )
    # estimate and CI
    estimate_CI = Format.format_estimate_interval (
        estimate=increase.get_mean(),
        interval=increase.get_t_CI(alpha=0.05), deci=2
    )
    print("Average change in the expected number of stroke and {:.{prec}%} confidence interval:".format(1 - 0.05, prec=0),
          estimate_CI)


cohort_ONE=Cohort(1,Therapies.No.value)
cohort_ONE.simulate()

cohort_TWO=Cohort(2,Therapies.Yes.value)
cohort_TWO.simulate()

cohort_ONE.get_total_utility()
cohort_ONE.get_total_cost()

cohort_TWO.get_total_utility()
cohort_TWO.get_total_cost()


print_comparative_cost(cohort_ONE.get_total_cost(),cohort_TWO.get_total_cost())
print_comparative_utility(cohort_ONE.get_total_utility(),cohort_TWO.get_total_utility())
print_comparative_stroke(cohort_ONE.get_stroke_time(),cohort_TWO.get_stroke_time())
