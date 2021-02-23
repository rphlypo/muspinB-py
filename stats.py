from scipy.stats import lognorm
import numpy as np


def all_true(logical_list):
    try:
        logical_list[2]
        return logical_list[0] and all_true(logical_list[1:])
    except IndexError:
        return logical_list[0] and logical_list[1]


class MarkovRenewalProcess():
    """ Markov renewal process
    - the transition matrix has entries [j][i] which is the probablity of next=j given current=i
    - the waiting times are log-normal distributed
    """
    def __init__(self, states, tm=None, mu=None, sigma=None):
        self.states = states
        k = len(self.states)
        # init the parameters for training
        if tm is None:
            tm = np.zeros((k, k), dtype=np.uint)
        elif tm == 'uniform':
            tm = np.ones((k, k))
            tm.flat[::k+1] = 0
        self.__comx = tm
        if sigma is None:
            sigma = np.zeros((k, ))
        if mu is None:
            mu = np.zeros((k, ))
            self.__mu = np.zeros((k, ))
            self.__S2 = np.zeros((k, ))
        else:  # get the first two raw moments of the normal from the first two centred moments of the log-normal
            self.__mu = np.log(mu**2/np.sqrt(sigma**2 + mu**2))
            self.__S2 = np.log(1 + sigma**2/mu**2) + self.__mu**2
        
    @property
    def states(self):
        return self.__states

    @property
    def transition_matrix(self):
        return self.__comx / self.__comx.sum(axis=0, keepdims=True)

    @property
    def survival_times(self):
        # base the survival times upon the parameters mu and sigma
        return {state: lognorm(s=self.s[self._ix[state]], loc=0, scale=self.scale[self._ix[state]]) for state in self.states}

    @property
    def sigma(self):
        """ second moments for each of the states' survival times
        based on self.n samples
        """
        return [np.sqrt(rv.stats(moments='v')) for rv in self.survival_times.values()]

    @property
    def mu(self):
        """ first moments for each of the states' survival times
        """
        return [rv.stats(moments='m') for rv in self.survival_times.values()]

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
    def s(self):
        return np.sqrt(self.__S2 - self.__mu ** 2)

    @property
    def scale(self):
        return np.exp(self.__mu)

    @property
    def steady_state(self):
        w, v = np.linalg.eig(self.transition_matrix)
        ix = np.argmax(np.real(w))
        steady_state = np.real(v[:, ix])
        for ix, st in enumerate(self.survival_times.values()):
            steady_state[ix] = steady_state[ix] * st.stats(moments='m')  # steady_state[ix] = steady_state[ix] * self.mu[ix] 
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
        m = self.__comx.sum(axis=0)  # TODO: should this not be axis=0 ???

        # get the current and next states together as x and y
        for x, y in zip(X[:-1], X[1:]):  
            if x[1] is not None:
                # only if the current state has a duration will we look at
                # - current survival time
                # - transition to next state
                surv_t[x[0]].append(np.log(x[1]))
                self.__comx[self._ix[y[0]], self._ix[x[0]]] += 1

        # the number of observations after the update
        n = self.__comx.sum(axis=0)  # TODO: should this not be axis=0 ???

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

    def sample_time(self, state):
        return self.survival_times[state].rvs()

    def transition(self, state):
        return np.random.choice(self.states, p=self.transition_matrix[self._ix[state]])

    def sample(self, t):
        steady_state = self.steady_state

        t_ = 0
        s = np.random.choice(self.states, p=steady_state)

        samples = []
        tm = self.transition_matrix
        st = self.survival_times

        while t_ < t:
            tau = st[s].rvs()
            samples.append((s, t_, tau))
            t_ += tau
            s = np.random.choice(self.states, p=tm[:, self._ix[s]])

        samples.append((s, t_, None))
        return samples


if  __name__ == '__main__':
    states = ['coherent', 'transparent_left', 'transparent_right']
    mrp_model = MarkovRenewalProcess(states, tm='uniform', mu=np.full((len(states), ), 3.), sigma=np.full((len(states), ), 1.))

    for k, v in mrp_model.survival_times.items():
        print('{}: mean={}, std={}'.format(k, v.stats(moments='m'), np.sqrt(v.stats(moments='v'))))

    print('transition matrix = \n{}\n'.format(mrp_model.transition_matrix))
    print('steady state vector = {}\n\n'.format(mrp_model.steady_state))

    samples = [mrp_model.sample(1000) for _ in range(10)]
    # print(samples)

    mrp = MarkovRenewalProcess(['coherent', 'transparent_left', 'transparent_right'])
    for ix, sample in enumerate(samples):
        print('training phase {i} on {n} extra samples'.format(i=ix+1, n = len(sample)))
        mrp.train([(s[0], s[2]) for s in sample])

        for k, v in mrp.survival_times.items():
            print('{}: mean={}, std={}'.format(k, v.stats(moments='m'), np.sqrt(v.stats(moments='v'))))

        print('transition matrix = \n{}\n'.format(mrp.transition_matrix))
        print('steady state vector = {}\n\n'.format(mrp.steady_state))
