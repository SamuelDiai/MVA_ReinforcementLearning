import sys
sys.path.insert(0, './utils')
import numpy as np
import matplotlib.pyplot as plt
import math
from cliffwalk import CliffWalk
import time
import sys
import tracemalloc



def policy_evaluation(P, R, policy, gamma=0.9, tol=1e-2):
    """
    Args:
        P: np.array
            transition matrix (NsxNaxNs)
        R: np.array
            reward matrix (NsxNa)
        policy: np.array
            matrix mapping states to action (Ns)
        gamma: float
            discount factor
        tol: float
            precision of the solution
    Return:
        value_function: np.array
            The value function of the given policy
    """
    Ns, Na = R.shape
    # ====================================================
	# YOUR IMPLEMENTATION HERE
    ## Compute matrix P_pi with policy pi ie P_pi(s', s) = P(s, pi(s), s')
    P_pi = P[range(Ns), policy, :]
    R_pi = R[range(Ns), policy]
    ## We use solve to resolve the linear system instead of inverting the matrix
    value_function = np.linalg.solve(np.eye(Ns) - gamma*P_pi, R_pi)
    # ====================================================
    return value_function

def policy_iteration(P, R, gamma=0.9, tol=1e-3):
    """
    Args:
        P: np.array
            transition matrix (NsxNaxNs)
        R: np.array
            reward matrix (NsxNa)
        gamma: float
            discount factor
        tol: float
            precision of the solution
    Return:
        policy: np.array
            the final policy
        V: np.array
            the value function associated to the final policy
    """
    Ns, Na = R.shape
    V = np.zeros(Ns)
    policy = np.zeros(Ns, dtype=np.int)
    # ====================================================
	# YOUR IMPLEMENTATION HERE
    iterating = True
    while iterating :
        V = policy_evaluation(P, R, policy, gamma)
        before_max = R + gamma*P.dot(V) # Shape (NsxNa)
        new_policy = np.argmax(before_max, axis = 1)
        if np.allclose(new_policy, policy, atol = tol, rtol = 0):
            iterating = False
        else :
            policy = new_policy
    # ====================================================
    return policy, V

def value_iteration(P, R, gamma=0.9, tol=1e-3):
    """
    Args:
        P: np.array
            transition matrix (NsxNaxNs)
        R: np.array
            reward matrix (NsxNa)
        gamma: float
            discount factor
        tol: float
            precision of the solution
    Return:
        Q: final Q-function (at iteration n)
        greedy_policy: greedy policy wrt Qn
        Qfs: all Q-functions generated by the algorithm (for visualization)
    """
    Ns, Na = R.shape
    Q = np.zeros((Ns, Na))
    Qfs = [Q]
    # ====================================================
	# YOUR IMPLEMENTATION HERE
    iterating = True
    while iterating :
        V = np.max(Q, axis = 1)
        Q_new = R + gamma * P.dot(V)
        V_new =  np.max(Q_new, axis = 1)
        if np.linalg.norm(V_new - V, ord = np.inf) < tol :
            iterating = False
        else :
            Qfs.append(Q_new)
            Q = Q_new
    greedy_policy = np.argmax(Q_new, axis = 1)
    # ====================================================
    return Q, greedy_policy, Qfs



# Edit below to run policy and value iteration on different environments and
# visualize the resulting policies in action!
# You may change the parameters in the functions below
if __name__ == "__main__":
    tol =1e-5
    env = CliffWalk(proba_succ=0.6)
    env.render()

    # run value iteration to obtain Q-values
    t1 = time.time()
    VI_Q, VI_greedypol, all_qfunctions = value_iteration(env.P, env.R, gamma=env.gamma, tol=tol)
    # compute the value function of the greedy policy using matrix inversion
    greedy_V = np.zeros((env.Ns, env.Na))
    # ====================================================
	# YOUR IMPLEMENTATION HERE
    # compute value function of the greedy policy
    greedy_V = policy_evaluation(env.P, env.R, VI_greedypol, gamma=env.gamma)
    # ====================================================
    t2 = time.time()
    print("TIME TO DO THE VALUE ITERATION : ", t2 - t1)

    # render the policy
    #print("[VI]Greedy policy: ")
    #env.render_policy(VI_greedypol)


    # show the error between the computed V-functions and the final V-function
    # (that should be the optimal one, if correctly implemented)
    # as a function of time
    norms = [ np.linalg.norm(q.max(axis=1) - greedy_V) for q in all_qfunctions]
    plt.plot(norms)
    plt.xlabel('Iteration')
    plt.ylabel('Error')
    plt.title("Value iteration: convergence")

    #### POLICY ITERATION ####
    t3 = time.time()
    PI_policy, PI_V = policy_iteration(env.P, env.R, gamma=env.gamma, tol=tol)
    print("\n[PI]final policy: ")
    t4= time.time()
    print("TIME TO DO THE POLICY ITERATION : ", t4 - t3)
    env.render_policy(PI_policy)

    # control that everything is correct
    assert np.allclose(PI_policy, VI_greedypol),\
        "You should check the code, the greedy policy computed by VI is not equal to the solution of PI"
    assert np.allclose(PI_V, greedy_V),\
        "Since the policies are equal, even the value function should be"


    # for visualizing the execution of a policy, you can use the following code
    # state = env.reset()
    # env.render()
    # for i in range(15):
    #     action = VI_greedypol[state]
    #     state, reward, done, _ = env.step(action)
    #     env.render()
    plt.show()


### I used the following code to generate the plot with different prob_succ:

    # plt.show()
    # tol =1e-5
    # for prob_succ in [0.2, 0.4, 0.6, 0.8, 1]:
    #     env = CliffWalk(proba_succ=prob_succ)
    #     env.render()
    #
    #     # run value iteration to obtain Q-values
    #     VI_Q, VI_greedypol, all_qfunctions = value_iteration(env.P, env.R, gamma=env.gamma, tol=tol)
    #
    #     # render the policy
    #     print("[VI]Greedy policy: ")
    #     #env.render_policy(VI_greedypol)
    #
    #     # compute the value function of the greedy policy using matrix inversion
    #     greedy_V = np.zeros((env.Ns, env.Na))
    #     # ====================================================
    #     # YOUR IMPLEMENTATION HERE
    #     # compute value function of the greedy policy
    #     greedy_V = policy_evaluation(env.P, env.R, VI_greedypol, gamma=env.gamma)
    #     # ====================================================
    #
    #     # show the error between the computed V-functions and the final V-function
    #     # (that should be the optimal one, if correctly implemented)
    #     # as a function of time
    #     norms = [ np.linalg.norm(q.max(axis=1) - greedy_V) for q in all_qfunctions]
    #     plt.plot(norms, label='Prob success = %s' % prob_succ)
    #     plt.xlabel('Iteration')
    #     plt.ylabel('Error')
    #     plt.title("Value iteration: convergence")
    #
    #     #### POLICY ITERATION ####
    #     PI_policy, PI_V = policy_iteration(env.P, env.R, gamma=env.gamma, tol=tol)
    #     print("\n[PI]final policy: ")
    #     #env.render_policy(PI_policy)
    #
    #     # control that everything is correct
    #     assert np.allclose(PI_policy, VI_greedypol),\
    #         "You should check the code, the greedy policy computed by VI is not equal to the solution of PI"
    #     assert np.allclose(PI_V, greedy_V),\
    #         "Since the policies are equal, even the value function should be"
    #
    #
    #     # # for visualizing the execution of a policy, you can use the following code
    #     # state = env.reset()
    #     # env.render()
    #     # for i in range(15):
    #     #     action = VI_greedypol[state]
    #     #     state, reward, done, _ = env.step(action)
    #     #     env.render()
    #
    # plt.legend()
    # plt.show()
