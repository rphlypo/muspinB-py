from scipy.stats import lognorm
import numpy as np


def all_true(logical_list):
    try:
        logical_list[2]
        return logical_list[0] and all_true(logical_list[1:])
    except IndexError:
        return logical_list[0] and logical_list[1]


class MarkovRenewalProcess():
    def __init__(self, states):
        self.states = states
        k = len(self.states)
        tm = np.full((k, k), 1/(k-1))
        tm.flat[::k+1] = 0  # put diagonal to zero
        self.__transition_matrix = tm
        self.__survival_times = {
            state: lognorm(s=np.sqrt(np.log(1+2/3**2)), loc=0, scale=np.log(3)-np.log(1+2/3**2)/2) for state in self.states 
        }
        # init the parameters for training
        self.__comx = np.zeros((k, k), dtype=np.uint)
        self.__mu = np.zeros((k, ))
        self.__S2 = np.zeros((k, ))
        
    @property
    def states(self):
        return self.__states

    @property
    def transition_matrix(self):
        return self.__transition_matrix

    @property
    def survival_times(self):
        return self.__survival_times

    @property
    def S2(self):
        """ second moments for each of the states' survival times
        based on self.n samples
        """
        return self.__S2

    @property
    def mu(self):
        """ first moments for each of the states' survival times
        """
        return self.__mu

    @property
    def comx(self):
        """ co-occurrence matrix
        """
        return self.__comx

    @states.setter
    def states(self, states):
        self.__states = list(states)

    @property
    def _ix(self):
        return {s: ix for ix, s in enumerate(self.states)}

    @property
    def steady_state(self):
        w, v = np.linalg.eig(self.transition_matrix)
        ix = np.argmax(np.real(w))
        steady_state = np.real(v[:, ix])
        for ix, st in enumerate(self.survival_times.values()):
            steady_state[ix] = steady_state[ix] * st.stats(moments='m')
        return steady_state / steady_state.sum()

    def train(self, X):
        """ X comes as a list of tuples (state, duration)
        for a specific element that has no duration, it is not used to update the estimate 
        of the survival_times, but is used as an "end-state" (previous transition is taken
        into account, not the next one)
        """
        # survival times
        surv_t = {
            s: [] for s in self.states
        }

        # the number of observations we already had
        m = self.__comx.sum(axis=1)

        for x, y in zip(X[:-1], X[1:]):
            if x[1] is not None:
                # only if the current state has a duration will we look at
                # - current survival time
                # - transition to next state
                surv_t[x[0]].append(np.log(x[1]))
                self.__comx[self._ix[y[0]], self._ix[x[0]]] += 1

        n = self.__comx.sum(axis=1)

        # update estimators of first two moments: mu and S2
        for k, v in surv_t.items():
            ix = self._ix[k]
            # do not update if no samples are observed
            # alternative, we may multiply
            #  the current estimator by alpha 
            # and the newly obtained estimator by (1 - alpha)
            # this would allow to forget the past trials at a "constant" rate
            # (not taking into account variance of the estimators)
            if n[ix] - m[ix] > 0:
                self.__mu[ix] = (self.__mu[ix] * m[ix] + np.array(v).sum()) / n[ix]
                self.__S2[ix] = (self.__S2[ix] * m[ix] + (np.array(v) ** 2).sum()) / n[ix]

                self.__survival_times[k] = lognorm(
                    scale=np.exp(self.__mu[ix]),
                    s = np.sqrt(self.__S2[ix] - self.__mu[ix] ** 2))

        comx_state_sum = self.__comx.sum(axis=0, keepdims=True)
        self.__transition_matrix = self.__comx / comx_state_sum 

    def sample_time(self, state):
        return self.surival_times[state].rvs()

    def transition(self, state):
        return np.random.choice(self.states, p=self.__transition[self._ix[state]])

    def sample(self, t):
        steady_state = self.steady_state

        t_ = 0
        s = np.random.choice(self.states, p=steady_state)

        samples = []

        while t_ < t:
            tau = self.survival_times[s].rvs()
            samples.append((s, t_, tau))
            t_ += tau
            s = np.random.choice(self.states, p=self.__transition_matrix[:, self._ix[s]])

        samples.append((s, t_, None))
        return samples


if  __name__ == '__main__':
    mrp = MarkovRenewalProcess(['coherent', 'transparent_left', 'transparent_right'])

    for k, v in mrp.survival_times.items():
        print('{}: params s={}, scale={}'.format(k, v.kwds['s'], v.kwds['scale']))

    print('transition matrix = \n{}\n'.format(mrp.transition_matrix))
    print('steady state vector = {}'.format(mrp.steady_state))

    samples = [mrp.sample(45) for _ in range(10)]
    # print(samples)
    for ix, sample in enumerate(samples):
        print('training phase {i} on {n} extra samples'.format(i=ix+1, n = len(sample)))
        mrp.train([(s[0], s[2]) for s in sample])

        for k, v in mrp.survival_times.items():
            print('{}: params s={}, scale={}'.format(k, v.kwds['s'], v.kwds['scale']))

        print('transition matrix = \n{}\n'.format(mrp.transition_matrix))
        print('steady state vector = {}'.format(mrp.steady_state))





        


