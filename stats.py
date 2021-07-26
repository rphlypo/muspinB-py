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
    - the residence times are log-normal distributed
    """
    def __init__(self, states, tm=None, mu=None, sigma=None, m=None):
        self.states = states
        k = len(self.states)
        # init the parameters for training
        if tm == 'uniform' or tm is None:
            tm = np.ones((k, k))
            tm.flat[::k+1] = 0
        self.__comx = tm    
        if sigma is None:
            sigma = np.full((k, ), 10)
        if mu is None:
            mu = np.full((k, ), 1)
        self.__mu = np.log(mu**2/np.sqrt(sigma**2 + mu**2))
        self.__S2 = np.log(1 + sigma**2/mu**2) + self.__mu**2
        self.__train_samples = {s: [] for s in states}
        
    @property
    def states(self):
        return self.__states

    @property
    def transition_matrix(self):
        return self.__comx / self.__comx.sum(axis=0, keepdims=True)

    @property
    def residence_times(self):
        # base the residence times upon the parameters mu and sigma
        return {state: lognorm(s=self.s[self._ix[state]], loc=0, scale=self.scale[self._ix[state]]) for state in self.states}

    @property
    def sigma(self):
        """ second moments for each of the states' residence times
        based on self.n samples
        """
        return [np.sqrt(rv.stats(moments='v')) for rv in self.residence_times.values()]

    @property
    def mu(self):
        """ first moments for each of the states' residence times
        """
        return [rv.stats(moments='m') for rv in self.residence_times.values()]

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
        for ix, st in enumerate(self.residence_times.values()):
            steady_state[ix] = steady_state[ix] * st.stats(moments='m')  # steady_state[ix] = steady_state[ix] * self.mu[ix] 
        return steady_state / steady_state.sum()

    def train(self, X):
        """ X comes as a list of tuples (state, duration)
        for a specific element that has no duration, it is not used to update the estimate 
        of the residence_times, but is used as an "end-state" (previous transition is taken
        into account, not the next one)
        """
        # residence times
        surv_t = {
            s: [] for s in self.states
        }

        # the number of observations we already had
        m = self.__comx.sum(axis=0)  # TODO: should this not be axis=0 ???

        self.__update_tm(X)
        for x in X:
            if x[1] is not None:
                surv_t[x[0]].append(np.log(x[1]))

        # the number of observations after the update
        n = self.__comx.sum(axis=0)

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


    def train_with_censored_data(self, X):
        """ X comes as a list of tuples of (state, duration) or (state, duration, flag)
        all observations are considered to be contingent in time unless flag is set to False
        where
            state: the current state
            duration: the current residence time in the state
            flag: True means the state is valid and the duration is a true residence time,
                  False means that the state is interrupted and the reported time is right-censored
        right-censored data allows for trials interrupting reporting, but still using the observation time in the estimator
        """
        for s in self.states:
            self.__train_samples[s].extend([x for x in X if x[0]==s])
        self.__update_estimators()
        self.__update_tm(X)
        

    def __update_tm(self, X):
        # get the current and next states together as x and y
        for x, y in zip(X[:-1], X[1:]):  
            if x[1] is not None:
                # only if the current state has a duration will we look at
                # - current residence time
                # - transition to next state
                self.__comx[self._ix[y[0]], self._ix[x[0]]] += 1

    def __update_estimators(self):
        for s in self.states:
            ix = self._ix[s]
            x = np.array([rt[1] for rt in self.__train_samples[s] if len(rt)==2 or rt[2]])
            y = np.array([rt[1] for rt in self.__train_samples[s] if len(rt)==3 and not rt[2]])
            p = x.size
            converged = False
            mu, sigma = 100, 1  # np.exp(self.__mu[ix]), np.sqrt(self.__S2[ix] - self.__mu[ix]**2)  # initialise mu and sigma
            while not converged and p>0:  # do not update if p is zero
                Z = lognorm(s=sigma, scale=mu)
                w = Z.pdf(y) / Z.sf(y)  # weights for the updates
                mu_ = np.exp(np.mean(np.log(x))+sigma**2/p*np.sum(y*w))
                sigma_ = np.sqrt(np.sum(np.log(x/mu)**2)/(p-np.sum(np.log(y/mu)*y*w)))
                if ((mu_ - mu)**2 + (sigma_ - sigma) ** 2)/2 < 1e-3:
                    converged = True
                mu, sigma = mu_, sigma_

            self.__mu[ix] = np.log(mu)
            self.__S2[ix] = sigma**2 + np.log(mu)**2


    def log_likelihood(self, X, normalise=True):
        """ compute log_likelihood for a list of (state, residence_time)

        the last percept is particular
        * if the next state is None, then the time of the one-to-last percept
            is considered "interrupted" (censored)
        * if only the residence time of the last percept is None,
            only the transition is taken into consideration
        * if both state and residence time are given, it is considered a fully valid 
            percept with veritable residence time
        """
        L = 0
        for x, y in zip(X[:-1], X[1:]):  
            if y[0] is not None:
                L += np.log(self.residence_times[x[0]].pdf(x[1]))
                ix = self._ix[x[0]], self._ix[y[0]]
                L += np.log(self.transition_matrix[ix[1], ix[0]])
            else:  # censored data
                L += np.log(1 - self.residence_times[x[0]].cdf(x[1]))
        if X[-1][1] is not None:
            L += np.log(self.residence_times[X[-1][0]].pdf(X[-1][1]))

        if normalise:
            observation_time = sum([x[1] for x in X if not x[1] is None])
            L /= observation_time
        
        return L
        

    def sample_time(self, state):
        return self.residence_times[state].rvs()

    def transition(self, state):
        return np.random.choice(self.states, p=self.transition_matrix[self._ix[state]])

    def sample(self, t, initial_state=None):
        steady_state = self.steady_state

        t_ = 0
        if initial_state is not None:
            if initial_state in self.states:
                s = initial_state
            else:
                raise ValueError('No state "{}"'.format(initial_state))
        else:
            s = np.random.choice(self.states, p=steady_state)

        samples = []
        tm = self.transition_matrix
        st = self.residence_times

        while t_ < t:
            tau = st[s].rvs()
            samples.append((s, t_, tau))
            t_ += tau
            s = np.random.choice(self.states, p=tm[:, self._ix[s]])

        last_sample = samples[-1]
        samples[-1] = (last_sample[0], last_sample[1], t - last_sample[1], False)
        return samples


if  __name__ == '__main__':
    from scipy.stats import uniform
    states = ['coherent', 'transparent_left', 'transparent_right']
    mrp_model = MarkovRenewalProcess(states, tm='uniform', mu=np.full((len(states), ), 3.), sigma=np.full((len(states), ), 1.))
    
    for k, v in mrp_model.residence_times.items():
        print('{}: mean={}, std={}'.format(k, v.stats(moments='m'), np.sqrt(v.stats(moments='v'))))

    print('transition matrix = \n{}\n'.format(mrp_model.transition_matrix))
    print('steady state vector = {}\n\n'.format(mrp_model.steady_state))

    for case in ['uncensored', 'censored']:

        samples = [mrp_model.sample(100) for _ in range(10)]
        # print(samples)

        mrp = MarkovRenewalProcess(states)
        mrp_prior = MarkovRenewalProcess(states)
        for ix, sample in enumerate(samples):
            print('training phase {i} on {n} extra samples'.format(i=ix+1, n = len(sample)))
            
            if case == 'uncensored':
                mrp.train([(s[0], s[2]) for s in sample])
            elif case == 'censored':
                mrp.train_with_censored_data([(s[0], s[2]) if len(s)<4 else (s[0], s[2], s[3]) for s in sample])

            print('log_likelihood(true model) = {}'.format(
                mrp_model.log_likelihood([(s[0], s[2]) for s in sample])))
            print('log_likelihood(trained model) = {}'.format(
                mrp.log_likelihood([(s[0], s[2]) for s in sample])))
            print('log_likelihood(prior) = {}'.format(
                mrp_prior.log_likelihood([(s[0], s[2]) for s in sample])))
            
            for k, v in mrp.residence_times.items():
                print('{}: mean={}, std={}'.format(k, v.stats(moments='m'), np.sqrt(v.stats(moments='v'))))

            print('transition matrix = \n{}\n'.format(mrp.transition_matrix))
            print('steady state vector = {}\n\n'.format(mrp.steady_state))
