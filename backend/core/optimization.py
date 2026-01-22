
from pulp import *
#####################################
### TOOLS TO CREATE THE VARIABLES ###
#####################################



# Create an array representing K_g that is needed for the creation of the variables in Pulp
    
def defineK2(K_g):
    k_max = 0
    for i in range(len(K_g)):
        k = K_g[i]
        if k > k_max:
            k_max = k   
    K2 = []
    for i in range(k_max):
        K2.append(i)
    return K2



# Create an array representing A_{g,k} that is needed for the creation of the variables in Pulp

def defineA2(A_gk):
    a_max = 0
    for i in range(len(A_gk)):
        for j in range(len(A_gk[i])):
            a = A_gk[i][j]
            if a > a_max:
                a_max = a
    A2 = []
    for i in range(a_max):
        A2.append(i)
    return A2



#####################################
### DEFINE THE OBJECTIVE FUNCTION ###
#####################################



# Define the objective function for LP
    
def set_obj_fn(LP, P_gk, P, Delta_plus, Delta_minus, params_system):
    LP += (1 - params_system["alpha"][0]) * lpSum([params_system["c_gk"][i][j] * params_system["D"][0] * P_gk[i][j] 
                                for i in range(len(params_system["G"])) 
                                    for j in range(params_system["K_g"][i])]) + params_system["alpha"][0] * lpSum([params_system["D"][0] * P[g2][k2][r2][a2][h2] * params_system["w_rh"][r2][h2]  
                                        for g2 in range(len(params_system["G"])) for k2 in range(params_system["K_g"][g2]) 
                                            for r2 in params_system["R"] for a2 in range(params_system["A_gk"][g2][k2]) for h2 in range(len(params_system["H"]))]) 



###########################################
### DEFINE THE CONSTRAINTS OF THE MODEL ###
###########################################



# DEFINE THE CONSTRAINTS ON THE P_{g,k,r}

# Define \sum_h P_{g,k,r,a,h} = P_{g,k,r} as an lpSum

def const_P_gkr(P, g, k, r, a, H, P_gkr):
    return lpSum([P[g][k][r][a][h] for h in H]) == P_gkr[g][k][r]
    
# Define such constraint for every sub-type (g,k,r) and every activity a:
#    - For every g \in G, k \in K_g, r \in R, a \in A_{g,k}

def def_const_P_gkr(LP, G, K_g, R, A_gk, H, P_gkr, P):
    for g in G:
        for k in range(K_g[g]):
            for r in R:
                for a in range(A_gk[g][k]):
                    LP += const_P_gkr(P, g, k, r, a, H, P_gkr)



# DEFINE THE CONSTRAINTS ON THE P_{g,k}

# Define \sum_r P_{g,k,r} = P_{g,k} as an lpSum

def const_P_gk(P_gkr, P_gk, g, k, R):
    return lpSum([P_gkr[g][k][r] for r in R]) == P_gk[g][k]
    
# Define such constraint for every type (g,k):
#    - For every g \in G, k \in K_g

def def_const_P_gk(LP, G, K_g, R, P_gkr, P_gk):
    for g in G:
        for k in range(K_g[g]): 
            LP += const_P_gk(P_gkr, P_gk, g, k, R)



# DEFINE THE CONSTRAINTS ON THE DEMANDS d_{g,r}

# Define \sum_k P_{g,k,r} == d_{g,r} as an lpSum

def const_d_gr(P_gkr, g, K_g, r, d):
    return lpSum([P_gkr[g][k][r] for k in range(K_g[g])]) == d
    
# Define such constraint for every type-ish (g,r):
#    - For every g \in G, r \in R

def def_const_d_gr(LP, P_gkr, d_gr, G, K_g, R):
    for g in G:
        for r in R:
            LP += const_d_gr(P_gkr, g, K_g, r, d_gr[g][r])



# DEFINE THE RESOURCES CONSTRAINTS ON THE m_{h,l} USING THE t_{g,k,a,l}
# This is the constraint to use when the transfers of resources are not allowed
    
# Define \sum_g \sum_k \sum_r \sum_a (D \cdot P_{g,k,r,a,h}) \cdot t_{g,k,a,l} \leq m_{h,l} as an lpSum

def const_m_hl(P, G, K_g, R, A_gk, h, l, t_gkal, m, D):
    return lpSum([D[0] * P[g][k][r][a][h] * t_gkal[g][k][a][l] for g in G for k in range(K_g[g]) for r in R for a in range(A_gk[g][k])]) <= m

# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_m_hl(LP, P, G, K_g, R, A_gk, H, t_gkal, m_hl, L, D):
    for h in H:
        for l in L:
            LP += const_m_hl(P, G, K_g, R, A_gk, h, l, t_gkal, m_hl[h][l], D)



# DEFINE THE CONSTRAINTS ON THE \underline{q}_g

# Define \sum_k P_{g,k} \geq \underline{q}_g \cdot (\sum_{g'} \sum_{k'} P_{g',k'}) as an lpSum

def const_q_g(P_gk, g, K_g, under_q, G):
    return lpSum([P_gk[g][k] for k in range(K_g[g])]) >= under_q * lpSum([P_gk[g][k] for g in range(len(G)) for k in range(K_g[g])])
    
# Define such constraint for every g:
#    - For every g \in G

def def_const_q_g(LP, P_gk, G, K_g, Under_q_g):
    for g in G:
        LP += const_q_g(P_gk, g, K_g, Under_q_g[g], G)



# DEFINE THE CONSTRAINTS ON THE \overline{q}_g

# Define \sum_k P_{g,k} \leq \overline{q}_g \cdot (\sum_{g'} \sum_{k'} P_{g',k'}) as an lpSum

def const_Overq_g(P_gk, g, K_g, over_q, G):
    return lpSum([P_gk[g][k] for k in range(K_g[g])]) <= over_q * lpSum([P_gk[g][k] for g in range(len(G)) for k in range(K_g[g])])
    
# Define such constraint for every g:
#    - For every g

def def_const_Overq_g(LP, P_gk, G, K_g, Over_q_g):
    for g in G:
        LP += const_Overq_g(P_gk, g, K_g, Over_q_g[g], G)



# DEFINE THE CONSTRAINTS ON THE \underline{q}_{g,u}

# Define \sum_{k' \in M_{g,u} P_{g,k} \geq \underline{q}_{g,u} \cdot (\sum_{k} P_{g,k}) as an lpSum

def const_q_gk(P_gk, g_2, K_g, M2, q):
    return lpSum([P_gk[g][k] for [g,k] in M2]) >= q * lpSum([P_gk[g_2][k3] for k3 in range(K_g[g_2])])
    
# Define such constraint for every type (g,u):
#    - For every g \in G, u \in U
# (Note that U is not used)

def def_const_q_gk(LP, P_gk, G, K_g, U, I_gu, Under_q_gu):
    for g in G:
        for u in range(U[g]):
            M2 = []
            for c in I_gu[g][u]:
                M2.append([g, c])
            LP += const_q_gk(P_gk, g, K_g, M2, Under_q_gu[g][u])



# DEFINE THE CONSTRAINTS ON THE \overline{q}_{g,u}

# Define \sum_{k' \in M_{g,u} P_{g,k} \leq \overline{q}_{g,u} \cdot (\sum_{k} P_{g,k}) as an lpSum

def const_Overq_gk(P_gk, g_2, K_g, M2, over_q):
    return lpSum([P_gk[g][k] for [g,k] in M2]) <= over_q * lpSum([P_gk[g_2][k3] for k3 in range(K_g[g_2])])
    
# Define such constraint for every type (g,u):
#    - For every g \in G, u \in U
# (Note that U is not used)

def def_const_Overq_gk(LP, P_gk, G, K_g, U, I_gu, Over_q_gu):
    for g in G:
        for u in range(U[g]):
            M2 = []
            for c in I_gu[g][u]:
                M2.append([g, c])
            LP += const_Overq_gk(P_gk, g, K_g, M2, Over_q_gu[g][u])



# DEFINE THE CONSTRAINTS ON THE O_{g,k}

# Define \sum_a P_{g,k,r,a,h} = 0 as an lpSum

def const_O_gk(P, g, k, r, a, h):
    return P[g][k][r][a][h] == 0
    
# Define such constraint for every (g,k,r,h):
#    - For every g \in G, k \in K_g, r \in R, h \in H st. h \notin O_{g,k}

def def_const_O_gk(LP, P, G, K_g, R, A_gk, H, O_gk):
    for g in G:
        for k in range(K_g[g]):
            for r in R:
                for a in range(A_gk[g][k]):
                    for h in H:
                        if h not in O_gk[g][k]:
                            LP += const_O_gk(P, g, k, r, a, h)



# DEFINE THE CONSTRAINTS ON THE J_h

# Define P_{g,k,r,a,h} \leq \sum_{h' \in J_h} P_{g,k,r,a',h'} as an lpSum

def const_J_h(P, h, g, k, r, a1, a2, J2_h):
    return P[g][k][r][a1][h] <= lpSum([P[g][k][r][a2][h2] for h2 in J2_h])
    
# Define such constraint for every (g, k, r, a, a', h):
#    - For every g \in G, k \in K_g, r \in R, a, a' \in A_{g,k}, a \neq a', h \in H

def def_const_J_h(LP, P, H, G, K_g, A_gk, J_h, R):
    for g in G:
        for k in range(K_g[g]):
            for r in R:
                for a1 in range(A_gk[g][k] - 1):
                    a2 = a1 + 1
                    for h in H:
                        J2_h = J_h[h]
                        LP += const_J_h(P, h, g, k, r, a1, a2, J2_h)



# DEFINE THE CONSTRAINTS ON THE Q_{g,k,r,a,h}

# Define Q_{g,k,r,a,h} \geq P_{g,k,r,a,h} - P_{g,k,r,a+1,h} as an lpSum

def const_Q_gkrah(Q, g, k, r, a, a_prime, h, P):
    return Q[g][k][r][a][h] >= P[g][k][r][a][h] - P[g][k][r][a_prime][h]
    
# Define such constraint for every (g,k,r,a,h):
#    - For every g \in G, k \in K_g, r \in R, a \in [A_{g,k} - 1], h \in H

def def_const_Q_gkrah(LP, Q, G, K_g, R, A_gk, H, P, N_gka_1, N_gka_2):
    for g in G:
        for k in range(K_g[g]):
            for r in R:
                for a in N_gka_1[g][k]:
                    index_a = N_gka_1[g][k].index(a)
                    a_prime = N_gka_2[g][k][index_a]
                    for h in H:
                        LP += const_Q_gkrah(Q, g, k, r, a, a_prime, h, P)



# DEFINE THE CONSTRAINTS ON THE f_{g,k}

# Define \sum_r \sum_a \sum_h Q_{g,k,r,a,h} \leq (|A_{g,k}| - 1) \cdot a_{g,k} \cdot P_{g,k} as an lpSum

def const_f_gk(Q, g, k, K_g, R, A_gk, H, f_gk, P_gk, N_gka_1):
    return lpSum([Q[g][k][r][a][h] for r in R for a in N_gka_1[g][k] for h in H]) <= len(N_gka_1[g][k]) * f_gk[g][k] * P_gk[g][k]
    
# Define such constraint for every type (g,k):
#    - For every g \in G, k \in K_g

def def_const_f_gk(LP, Q, G, K_g, R, A_gk, H, f_gk, P_gk, N_gka_1):
    for g in G:
        for k in range(K_g[g]):
            LP += const_f_gk(Q, g, k, K_g, R, A_gk, H, f_gk, P_gk, N_gka_1)



# DEFINE THE CONSTRAINT ON THE $f$

# Define \sum_g \sum_k \sum_r \sum_a \sum_h Q_{g,k,r,a,h} \leq f \cdot (\sum_g \sum_k n_g \cdot P_{g,k}) as an lpSum

def const_f(Q, G, K_g, R, A_gk, H, f, P_gk, N_gka_1, n_g):
    return lpSum([Q[g][k][r][a][h] for g in G for k in range(K_g[g]) for r in R for a in N_gka_1[g][k] for h in H]) <= f[0] * lpSum([P_gk[g][k] * n_g[g] for g in G for k in range(K_g[g])])

# Define such constraint for only one $f$:

def def_const_f(LP, Q, G, K_g, R, A_gk, H, f, P_gk, N_gka_1):
    n_g = [0 for _ in G]
    for g in G:
        for k in range(K_g[g]):
            n_gk = len(N_gka_1[g][k])
            if n_gk > n_g[g]:
                n_g[g] = n_gk
    LP += const_f(Q, G, K_g, R, A_gk, H, f, P_gk, N_gka_1, n_g)
    



# DEFINE THE Q_{g,k,r,a,h} POSTIVE

# Define Q_{g,k,r,a,h} \geq 0

def const_Q(Q, g, k, r, a, h):
    return Q[g][k][r][a][h] >= 0
    
# Define such constraint for every (g,k,r,a,h):
#    - For every g \in G, k \in K_g, r \in R, a \in A_{g,k}, h \in H

def def_const_Q(LP, G, K_g, R, A_gk, H, Q):
    for g in G:
        for k in range(K_g[g]):
            for r in R:
                for a in range(A_gk[g][k]):
                    for h in H:
                        LP += const_Q(Q, g, k, r, a, h)



# DEFINE THE RESOURCES CONSTRAINTS ON THE m_{h,l} USING THE t_{g,k,a,l}
# This is the constraint to use when the transfers of resources are allowed
    
# Define \sum_g \sum_k \sum_r \sum_a X_{g,k,r,a,h} \cdot t_{g,k,a,l} \leq m_{h,l} + \Delta_{h,l}^{+} - \Delta_{h,l}^{-} as an lpSum

def const_m_hl_2(P, G, K_g, R, A_gk, h, l, t_gkal, m, D, Delta_plus, Delta_moins):
    return lpSum([D[0] * P[g][k][r][a][h] * t_gkal[g][k][a][l] for g in G for k in range(K_g[g]) for r in R for a in range(A_gk[g][k])]) <= m + Delta_plus[h][l] - Delta_moins[h][l]

# Define such constraint for every h and every l:
#    - For every h \in H, l \in L

def def_const_m_hl_2(LP, P, G, K_g, R, A_gk, H, t_gkal, m_hl, L, D, Delta_plus, Delta_moins):
    for h in H:
        for l in L:
            LP += const_m_hl_2(P, G, K_g, R, A_gk, h, l, t_gkal, m_hl[h][l], D, Delta_plus, Delta_moins)



# DEFINE THE ZERO-pulp.value OF DELTAS

# Define \sum_h \Delta_{h,l}^{+} = \sum_h \Delta_{h,l}^{-} as an lpSum

def const_delta_zero(Delta_plus, Delta_moins, H, l):
    return lpSum([Delta_plus[h][l] for h in H]) - lpSum([Delta_moins[h][l] for h in H]) == 0
    
# Define such constraint for every l:
#    - For every l \in L

def def_const_delta_zero(LP, Delta_plus, Delta_moins, H, L):
    for l in L:
        LP += const_delta_zero(Delta_plus, Delta_moins, H, l)



# DEFINE THE DELTA_PLUS pulp.value AS A MULTIPLICATOR OF P

# Define \Delta_{h,l}^{+} = P *z_{h,l}^{+} as an lpSum 

def const_delta_plus_delta(Delta_plus, z_hl_plus, h, l, delta):
    return Delta_plus[h][l] == delta * z_hl_plus[h][l]
    
# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_delta_plus_delta(LP, Delta_plus, z_hl_plus, H, L, delta_l):
    for h in H:
        for l in L:
            LP += const_delta_plus_delta(Delta_plus, z_hl_plus, h, l, delta_l[l])



# DEFINE THE DELTA_MOINS pulp.value AS A MULTIPLICATOR OF P

# Define \Delta_{h,l}^{-} = P *z_{h,l}^{-} as an lpSum 

def const_delta_moins_delta(Delta_moins, z_hl_moins, h, l, delta):
    return Delta_moins[h][l] == delta * z_hl_moins[h][l]

# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_delta_moins_delta(LP, Delta_moins, z_hl_moins, H, L, delta_l):
    for h in H:
        for l in L:
            LP += const_delta_moins_delta(Delta_moins, z_hl_moins, h, l, delta_l[l])



# DEFINE AN UPPER BOUND ON THE DELTA_PLUS

# Define \Delta_{h,l}^{+} \leq b_{h,l} * m_{h,l} as an lpSum

def const_delta_plus_b_hl_in(Delta_plus, m_hl, h, l, b_hl_in):
    return Delta_plus[h][l] <= b_hl_in[h][l] * m_hl[h][l]
    
# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_delta_plus_b_hl_in(LP, Delta_plus, m_hl, H, L, b_hl_in):
    for h in H:
        for l in L:
            LP += const_delta_plus_b_hl_in(Delta_plus, m_hl, h, l, b_hl_in)


#TOODO add another variable for the delta moins upper bound constraint

# DEFINE AN UPPER BOUND ON THE DELTA_MOINS

# Define \Delta_{h,l}^{-} \leq b_{h,l} * m_{h,l} as an lpSum

def const_delta_moins_b_hl_out(Delta_moins, m_hl, h, l, b_hl_out):
    return Delta_moins[h][l] <= b_hl_out[h][l] * m_hl[h][l]

# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_delta_moins_b_hl_out(LP, Delta_moins, m_hl, H, L, b_hl_out):
    for h in H:
        for l in L:
            LP += const_delta_moins_b_hl_out(Delta_moins, m_hl, h, l, b_hl_out)




#################################################
### SUPER FUNCTION TO CALL EVERYTHING AT ONCE ###
#################################################



def change_Under_Over(G, U, Under_q_gu, Over_q_gu):

    Under = [[0.0 for _ in range(U[g])] for g in range(len(G))]
    for g in range(len(G)):
        sum_u = 0.0
        for u in range(U[g]):
            if u < U[g] - 1:
                sum_u += Under_q_gu[g][u]
                Under[g][u] = Under_q_gu[g][u]
            else:
                Under[g][u] = 1.0 - sum_u
    return Under, Under


def declare_constraints(LP, P_gk, G, K_g, P_gkr, R, P, A_gk, H, Q, Delta_plus,
                        Delta_moins, L, z_hl_plus, z_hl_moins, d_gr, Under_q_g, Over_q_g,
                        U, I_gu, Under_q_gu, Over_q_gu, O_gk, J_h, N_gka_1, N_gka_2,
                        f, t_gkal, m_hl, D, delta_l, b_hl_in, b_hl_out):


    def_const_P_gkr(LP, G, K_g, R, A_gk, H, P_gkr, P)
    def_const_P_gk(LP, G, K_g, R, P_gkr, P_gk) 
    def_const_d_gr(LP, P_gkr, d_gr, G, K_g, R)
 
    
    # Line below to use when the resources' transfers are not allowed, otherwise (when the resources' transfers are allowed) use "def_const_m_hl_2(..."
    #def_const_m_hl(LP, P, G, K_g, R, A_gk, H, t_gkal, m_hl, L, D) 
    
    def_const_q_g(LP, P_gk, G, K_g, Under_q_g)
    def_const_Overq_g(LP, P_gk, G, K_g, Over_q_g)
    def_const_q_gk(LP, P_gk, G, K_g, U, I_gu, Under_q_gu)
    def_const_Overq_gk(LP, P_gk, G, K_g, U, I_gu, Over_q_gu)
    def_const_O_gk(LP, P, G, K_g, R, A_gk, H, O_gk)
    def_const_J_h(LP, P, H, G, K_g, A_gk, J_h, R)
    def_const_Q_gkrah(LP, Q, G, K_g, R, A_gk, H, P, N_gka_1, N_gka_2)
    
    
    # Line below was the old model (with f_{g,k} for every pathway (g,k)) instead of the new model (with the global f)
    #def_const_f_gk(LP, Q, G, K_g, R, A_gk, H, f_gk, P_gk, N_gka_1)
    
    def_const_f(LP, Q, G, K_g, R, A_gk, H, f, P_gk, N_gka_1)
    def_const_Q(LP, G, K_g, R, A_gk, H, Q)

    
    # Set the new constraints
    
    # Line below to use when the resources' transfers are allowed
    def_const_m_hl_2(LP, P, G, K_g, R, A_gk, H, t_gkal, m_hl, L, D, Delta_plus, Delta_moins) 
    def_const_delta_zero(LP, Delta_plus, Delta_moins, H, L)
    def_const_delta_plus_delta(LP, Delta_plus, z_hl_plus, H, L, delta_l)
    def_const_delta_moins_delta(LP, Delta_moins, z_hl_moins, H, L, delta_l)
    def_const_delta_plus_b_hl_in(LP, Delta_plus, m_hl, H, L, b_hl_in)
    def_const_delta_moins_b_hl_out(LP, Delta_moins, m_hl, H, L, b_hl_out)
