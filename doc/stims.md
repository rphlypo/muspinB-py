# stims.py

The plaid stimulus is created starting with a square patch with transparency values for the left and right gratings. The transparency is governed by de de Beer&ndash;Lambert law stating that the intensity at the output is given as a function fo the (energy) absorption distribution $\mu$ as
$$I(x,y) = I_0(x,y) \mathrm{e}^{-\int_0^\Delta\mu(x,y,z)\mathrm d z}$$
where $\Delta$ is the total thickness traversed by the ray of light (straight line) coming from the back(ground) to the front. We modulate the observed intensity by imaging different values of $\Delta$ and $\mu(x,y)$ for each of the gratings, which are resumed in their respective multiplicative constants $\alpha_L=\mathrm{e}^{-\int_0^{\Delta_L}\mu_L(x,y)\mathrm d z}=\mathrm{e}^{-\mu(x,y)\Delta_L}\in[0, 1]$, and $\alpha_L=\mathrm{e}^{-\int_0^{\Delta_L}\mu_L(x,y)\mathrm d z}=\mathrm{e}^{-\mu(x,y)\Delta_L}\in[0, 1]$. This results in
$$I(x,y) = I_0(x,y)\alpha_L(x,y)\alpha_R(x,y)\enspace.$$
Since multiplication is commutative, it does not matter which grating is up front or which is behind. Indeed, when either one of the gratings is completely opaque ($\alpha_L=0$ or $\alpha_R=0$) the resulting intensity will be zero. If both gratings are totally transparent ($\alpha_L=\alpha_R=1$) then the observed intensity will be the background intensity.

If the spatial frequency `sf` and $\theta$ the angle with respect to the vertical axis are both given, then we must compute the resulting horizontal and vertical spatial frequencies. To do so, we first observe that the target spatial frequency is related to both the horizontal and vertical spatial frequencies through $\text{sf} = \sqrt{\text{sf}_H^2 + \text{sf}_V^2}$ and the angle $\theta$ results in the ratio of both spatial frequencies to be given as $\tan(\theta) = \frac{\text{sf}_H}{\text{sf}_V}$. We thus find that
$$
\begin{cases}
\text{sf}_V = \text{sf}\cdot \cos(\theta) \\
\text{sf}_H = \text{sf}\cdot \sin(\theta)
\end{cases}
$$