
from pulp import *



#####################################
### DEFINE THE OBJECTIVE FUNCTION ###
#####################################



# Define the objective function for LP
    
def set_obj_fn(LP, P_gk, P, Delta_plus, Delta_minus, s_hl, params_system):
    w_rh = params_system["w_rh"]

    indices_a = (
    (g, k, r, a, h)
    for g in params_system["G"]
    for k in params_system["K_idx"][g]
    for r in params_system["R"]
    for a in params_system["A_idx"][g][k]
    for h in params_system["H"]
    )

    coeff_rh = {(r,h): params_system["D"] * w_rh[r][h] for r in params_system["R"] for h in params_system["H"]}

    match params_system["mode"]:
        case "slack":
            LP += lpSum(-s_hl[h][l] for h in params_system["H"] for l in params_system["L"])
        case "maternities":
          
            LP +=  lpSum( P[g][k][r][a][h] * coeff_rh[(r,h)]
                                                   for (g,k,r,a,h) in indices_a)\
                                                    -  1e-8*lpSum(Delta_plus[h][l]
                                                                   for h in params_system["H"]
                                                                   for l in params_system["L"])\
                                                    -  1e-8*lpSum(Delta_minus[h][l]
                                                                   for h in params_system["H"]
                                                                   for l in params_system["L"])
        case _:
            LP += (1 - params_system["alpha"]) * lpSum(params_system["c_gk"][g][k] * params_system["D"] * P_gk[g][k] 
                                                        for g in params_system["G"]
                                                        for k in params_system["K_idx"][g]) \
                + params_system["alpha"] * lpSum(P[g][k][r][a][h] * coeff_rh[(r,h)]
                                                 for (g,k,r,a,h) in indices_a)\
                -  1e-6*lpSum(Delta_plus[h][l]
                               for h in params_system["H"]
                               for l in params_system["L"])\
                -  1e-6*lpSum(Delta_minus[h][l]
                               for h in params_system["H"]
                               for l in params_system["L"])




###########################################
### DEFINE THE CONSTRAINTS OF THE MODEL ###
###########################################



# DEFINE THE CONSTRAINTS ON THE P_{g,k,r}

# Define \sum_h P_{g,k,r,a,h} = P_{g,k,r} as an lpSum

def const_P_gkr(P, P_gkr, H, g, k, r, a):
    return lpSum(P[g][k][r][a][h] for h in H) == P_gkr[g][k][r]
    
# Define such constraint for every sub-type (g,k,r) and every activity a:
#    - For every g \in G, k \in K_g, r \in R, a \in A_{g,k}

def def_const_P_gkr(LP, vars_system, params_system):
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            for r in params_system["R"]:
                for a in params_system["A_idx"][g][k]:
                    fast_add(LP, const_P_gkr(vars_system.P, vars_system.P_gkr, params_system["H"], g, k, r, a))



# DEFINE THE CONSTRAINTS ON THE P_{g,k}

# Define \sum_r P_{g,k,r} = P_{g,k} as an lpSum

def const_P_gk(P_gkr, P_gk, g, k, R):
    return lpSum(P_gkr[g][k][r] for r in R) == P_gk[g][k]
    
# Define such constraint for every type (g,k):
#    - For every g \in G, k \in K_g

def def_const_P_gk(LP, vars_system, params_system) :
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]: 
            LP += const_P_gk(vars_system.P_gkr, vars_system.P_gk, g, k, params_system["R"])



# DEFINE THE CONSTRAINTS ON THE DEMANDS d_{g,r}

# Define \sum_k P_{g,k,r} >= d_{g,r} as an lpSum

def const_d_gr(P_gkr, g, K_idx, r, d):
    return lpSum(P_gkr[g][k][r] for k in K_idx[g]) >= d
    
# Define such constraint for every type-ish (g,r):
#    - For every g \in G, r \in R

def def_const_d_gr(LP, vars_system, params_system):
    for g in params_system["G"]:
        for r in params_system["R"]:
            LP += const_d_gr(vars_system.P_gkr, g, params_system["K_idx"], r, params_system["d_gr"][g][r])



# DEFINE THE CONSTRAINTS ON THE DEMANDS d_{g,r} for maternity data

# Define \sum_k P_{g,k,r} == d_{g,r} as an lpSum

def const_d_gr_maternity(P_gkr, g, K_idx, r, d):
    return lpSum(P_gkr[g][k][r] for k in K_idx[g]) == d
    
# Define such constraint for every type-ish (g,r):
#    - For every g \in G, r \in R

def def_const_d_gr_maternity(LP, vars_system, params_system):
    for g in params_system["G"]:
        for r in params_system["R"]:
            LP += const_d_gr_maternity(vars_system.P_gkr, g, params_system["K_idx"], r, params_system["d_gr"][g][r])





# DEFINE THE CONSTRAINTS ON THE \underline{q}_g

# Define \sum_k P_{g,k} \geq \underline{q}_g \cdot (\sum_{g'} \sum_{k'} P_{g',k'}) as an lpSum

def const_q_g(P_gk, g, K_idx, under_q, G):
    return lpSum(P_gk[g][k] for k in K_idx[g]) >= under_q * lpSum(P_gk[g][k] for g in G for k in K_idx[g])
    
# Define such constraint for every g:
#    - For every g \in G

def def_const_q_g(LP, vars_system, params_system):
    for g in params_system["G"]:
        LP += const_q_g(vars_system.P_gk, g, params_system["K_idx"], params_system["Under_q_g"][g], params_system["G"])



# DEFINE THE CONSTRAINTS ON THE \overline{q}_g

# Define \sum_k P_{g,k} \leq \overline{q}_g \cdot (\sum_{g'} \sum_{k'} P_{g',k'}) as an lpSum

def const_Overq_g(P_gk, g, K_idx, over_q, G):
    return lpSum(P_gk[g][k] for k in K_idx[g]) <= over_q * lpSum(P_gk[g][k] for g in G for k in K_idx[g])
    
# Define such constraint for every g:
#    - For every g

def def_const_Overq_g(LP, vars_system, params_system):
    for g in params_system["G"]:
        LP += const_Overq_g(vars_system.P_gk, g, params_system["K_idx"], params_system["Over_q_g"][g], params_system["G"])



# DEFINE THE CONSTRAINTS ON THE \underline{q}_{g,u}

# Define \sum_{k' \in M_{g,u} P_{g,k} \geq \underline{q}_{g,u} \cdot (\sum_{k} P_{g,k}) as an lpSum

def const_q_gk(P_gk, g_2, K_idx, M2, q):
    return lpSum(P_gk[g][k] for [g,k] in M2) >= q * lpSum(P_gk[g_2][k3] for k3 in K_idx[g_2])
    
# Define such constraint for every type (g,u):
#    - For every g \in G, u \in U

def def_const_q_gk(LP, vars_system, params_system):
    for g in params_system["G"]:
        for u in params_system["U_idx"][g]:
            M2 = []
            for k in params_system["I_gu"][g][u]:
                M2.append([g, k])
            LP += const_q_gk(vars_system.P_gk, g, params_system["K_idx"], M2, params_system["Under_q_gu"][g][u])



# DEFINE THE CONSTRAINTS ON THE \overline{q}_{g,u}

# Define \sum_{k' \in M_{g,u} P_{g,k} \leq \overline{q}_{g,u} \cdot (\sum_{k} P_{g,k}) as an lpSum

def const_Overq_gk(P_gk, g_2, K_idx, M2, over_q):
    return lpSum(P_gk[g][k] for [g,k] in M2) <= over_q * lpSum(P_gk[g_2][k3] for k3 in K_idx[g_2])
    
# Define such constraint for every type (g,u):
#    - For every g \in G, u \in U

def def_const_Overq_gk(LP, vars_system, params_system):
    for g in params_system["G"]:
        for u in params_system["U_idx"][g]:
            M2 = []
            for k in params_system["I_gu"][g][u]:
                M2.append([g, k])
            LP += const_Overq_gk(vars_system.P_gk, g, params_system["K_idx"], M2, params_system["Over_q_gu"][g][u])



# DEFINE THE CONSTRAINTS ON THE O_{g,k}

# Define \sum_a P_{g,k,r,a,h} = 0 as an lpSum

def const_O_gk(P, g, k, r, a, h):
    return P[g][k][r][a][h] == 0
    
# Define such constraint for every (g,k,r,h):
#    - For every g \in G, k \in K_g, r \in R, h \in H st. h \notin O_{g,k}

def def_const_O_gk(LP, vars_system, params_system):
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            for r in params_system["R"]:
                for a in params_system["A_idx"][g][k]:
                    for h in params_system["H"]:
                        if h not in params_system["O_gk"][g][k]:
                            LP += const_O_gk(vars_system.P, g, k, r, a, h)



# DEFINE THE CONSTRAINTS ON THE J_h

# Define P_{g,k,r,a,h} \leq \sum_{h' \in J_h} P_{g,k,r,a',h'} as an lpSum

def const_J_h(P, h, g, k, r, a1, a2, J2_h):
    return P[g][k][r][a1][h] <= lpSum([P[g][k][r][a2][h2] for h2 in J2_h])
    
# Define such constraint for every (g, k, r, a, a', h):
#    - For every g \in G, k \in K_g, r \in R, a, a' \in A_{g,k}, a \neq a', h \in H

def def_const_J_h(LP, vars_system, params_system):
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            for r in params_system["R"]:
                for a1 in params_system["A_idx"][g][k]:
                    if a1 in params_system["N_gka_1"][g][k]:
                        a2 = params_system["N_gka_2"][g][k][a1]
                        for h in params_system["H"]:
                            J2_h = params_system["J_h"][h]
                            fast_add(LP, const_J_h(vars_system.P, h, g, k, r, a1, a2, J2_h))


# DEFINE THE CONSTRAINTS ON THE Q_{g,k,r,a,h}

# Define Q_{g,k,r,a,h} \geq P_{g,k,r,a,h} - P_{g,k,r,a+1,h} as an lpSum

def def_const_Q_gkrah(LP, vars_system, params_system):
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            N1 = params_system["N_gka_1"][g][k]
            N2 = params_system["N_gka_2"][g][k]
            for r in params_system["R"]:
                P_gkr = vars_system.P[g][k][r]
                Q_gkr = vars_system.Q[g][k][r]
                for a in N1:
                    ap = N2[a]
                    P_a  = P_gkr[a]
                    P_ap = P_gkr[ap]
                    Q_a  = Q_gkr[a]
                    for h in params_system["H"]:
                        # Q >= P_a - P_ap  →  Q - P_a + P_ap >= 0
                        e = LpAffineExpression(
                            [(Q_a[h], 1.0), (P_a[h], -1.0), (P_ap[h], 1.0)],
                            constant=0
                        )
                        fast_add(LP, LpConstraint(e, LpConstraintGE, rhs=0))


# DEFINE THE CONSTRAINT ON THE $f$

# Define \sum_g \sum_k \sum_r \sum_a \sum_h Q_{g,k,r,a,h} \leq f \cdot (\sum_g \sum_k n_g \cdot P_{g,k}) as an lpSum

def const_f(Q, P_gk, n_g, params_system):
    return lpSum(Q[g][k][r][a][h] for g in params_system["G"] for k in params_system["K_idx"][g] \
                  for r in params_system["R"] for a in params_system["N_gka_1"][g][k] for h in params_system["H"]) \
                    <= params_system["p_transf"] * lpSum(P_gk[g][k] * n_g[g] for g in params_system["G"] for k in params_system["K_idx"][g])

# Define such constraint for only one $f$:

def def_const_f(LP, vars_system, params_system):
    n_g = {k: max(len(x) for x in v.values()) for k, v in params_system["N_gka_1"].items()}
    fast_add(LP,const_f(vars_system.Q, vars_system.P_gk, n_g, params_system))
    



# DEFINE THE Q_{g,k,r,a,h} POSTIVE

# Define Q_{g,k,r,a,h} \geq 0

def const_Q(Q, g, k, r, a, h):
    return Q[g][k][r][a][h] >= 0
    
# Define such constraint for every (g,k,r,a,h):
#    - For every g \in G, k \in K_g, r \in R, a \in A_{g,k}, h \in H

def def_const_Q(LP, vars_system, params_system):
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            for r in params_system["R"]:
                for a in params_system["A_idx"][g][k]:
                    for h in params_system["H"]:
                        LP += const_Q(vars_system.Q, g, k, r, a, h)



# DEFINE THE RESOURCES CONSTRAINTS ON THE m_{h,l} USING THE t_{g,k,a,l}
# This is the constraint to use when the transfers of resources are allowed
    
def def_const_m_hl(LP, vars_system, params_system):
    D = params_system["D"]
    t = params_system["t_gkal"]
    H = params_system["H"]
    L = params_system["L"]

    # build usage once
    usage = {(h, l): [] for h in H for l in L}
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            for r in params_system["R"]:
                for a in params_system["A_idx"][g][k]:
                    for h in H:
                        var = vars_system.P[g][k][r][a][h]
                        for l in L:
                            c = D * t[g][k][a][l]
                            if c != 0:
                                usage[(h, l)].append((var, c))

    for h in H:
        for l in L:
            terms = usage[(h, l)][:]
            terms.append((vars_system.Delta_plus[h][l],  -1.0))
            terms.append((vars_system.Delta_moins[h][l],  1.0))
            e = LpAffineExpression(terms)
            fast_add(LP, LpConstraint(e, LpConstraintLE, rhs=params_system["m_hl"][h][l]))


# With slack    

def const_s_hl(P, G, K_idx, R, A_idx, h, l, t_gkal, m, D, Delta_plus, Delta_moins, s_hl):
    return lpSum([D * P[g][k][r][a][h] * t_gkal[g][k][a][l] 
                  for g in G for k in K_idx[g] for r in R for a in A_idx[g][k]]) \
                    <= m + s_hl + Delta_plus[h][l] - Delta_moins[h][l]


def def_const_s_hl(LP, vars_system, params_system) :
    for h in params_system["H"]:
        for l in params_system["L"]:
            LP += const_s_hl(vars_system.P, params_system["G"], params_system["K_idx"], params_system["R"], params_system["A_idx"],\
                                h, l, params_system["t_gkal"], params_system["m_hl"][h][l], params_system["D"], vars_system.Delta_plus, vars_system.Delta_moins, vars_system.s_hl[h][l])



# DEFINE THE ZERO-pulp.value OF DELTAS

# Define \sum_h \Delta_{h,l}^{+} = \sum_h \Delta_{h,l}^{-} as an lpSum

def const_delta_zero(Delta_plus, Delta_moins, H, l):
    return lpSum([Delta_plus[h][l] for h in H]) - lpSum([Delta_moins[h][l] for h in H]) == 0
    
# Define such constraint for every l:
#    - For every l \in L

def def_const_delta_zero(LP, vars_system, params_system):
    for l in params_system["L"]:
        LP += const_delta_zero(vars_system.Delta_plus, vars_system.Delta_moins, params_system["H"], l)



# DEFINE THE DELTA_PLUS pulp.value AS A MULTIPLICATOR OF P

# Define \Delta_{h,l}^{+} = P *z_{h,l}^{+} as an lpSum 

def const_delta_plus_delta(Delta_plus, z_hl_plus, h, l, delta):
    return Delta_plus[h][l] == delta * z_hl_plus[h][l]
    
# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_delta_plus_delta(LP, vars_system, params_system):
    for h in params_system["H"]:
        for l in params_system["L"]:
            LP += const_delta_plus_delta(vars_system.Delta_plus, vars_system.z_hl_plus, h, l, params_system["delta_l"][l])



# DEFINE THE DELTA_MOINS pulp.value AS A MULTIPLICATOR OF P

# Define \Delta_{h,l}^{-} = P *z_{h,l}^{-} as an lpSum 

def const_delta_moins_delta(Delta_moins, z_hl_moins, h, l, delta):
    return Delta_moins[h][l] == delta * z_hl_moins[h][l]

# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_delta_moins_delta(LP, vars_system, params_system):
    for h in params_system["H"]:
        for l in params_system["L"]:
            LP += const_delta_moins_delta(vars_system.Delta_moins, vars_system.z_hl_moins, h, l, params_system["delta_l"][l])



# DEFINE AN UPPER BOUND ON THE DELTA_PLUS

# Define \Delta_{h,l}^{+} \leq b_{h,l} * m_{h,l} as an lpSum

def const_delta_plus_b_hl_in(Delta_plus, m_hl, h, l, b_hl_in):
    return Delta_plus[h][l] <= b_hl_in[h][l] * m_hl[h][l]
    
# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_delta_plus_b_hl_in(LP, vars_system, params_system):
    for h in params_system["H"]:
        for l in params_system["L"]:
            LP += const_delta_plus_b_hl_in(vars_system.Delta_plus, params_system["m_hl"], h, l, params_system["b_hl_in"])


#TOODO add another variable for the delta moins upper bound constraint

# DEFINE AN UPPER BOUND ON THE DELTA_MOINS

# Define \Delta_{h,l}^{-} \leq b_{h,l} * m_{h,l} as an lpSum

def const_delta_moins_b_hl_out(Delta_moins, m_hl, h, l, b_hl_out):
    return Delta_moins[h][l] <= b_hl_out[h][l] * m_hl[h][l]

# Define such constraint for every couple (h,l):
#    - For every h \in H, l \in L

def def_const_delta_moins_b_hl_out(LP, vars_system, params_system):
    for h in params_system["H"]:
        for l in params_system["L"]:
            LP += const_delta_moins_b_hl_out(vars_system.Delta_moins, params_system["m_hl"], h, l, params_system["b_hl_out"])



# Impose an exact number of patients

def def_const_demand(LP, vars_system, params_system):
            LP += lpSum(vars_system.P_gk[g][k]
                        for g in params_system["G"]
                        for k in params_system["K_idx"][g]) * params_system["D"] ==  params_system["D"]*1.115




#################################################
###    CHOOSE SET OF CONSTRAINTS TO INCLUDE   ###
#################################################



def declare_constraints(LP, vars_system, params_system):

    CONSTRAINTS_DEFAULT=[def_const_P_gkr, def_const_P_gk, def_const_d_gr, def_const_q_g, def_const_Overq_g, def_const_q_gk, def_const_Overq_gk,
                           def_const_J_h, def_const_Q_gkrah, def_const_f, def_const_m_hl, def_const_delta_zero,
                           def_const_delta_plus_delta, def_const_delta_moins_delta, def_const_delta_plus_b_hl_in, def_const_delta_moins_b_hl_out]
    
    CONSTRAINTS_SLACK=[def_const_P_gkr, def_const_P_gk, def_const_d_gr, def_const_q_g, def_const_Overq_g, def_const_q_gk, def_const_Overq_gk,
                           def_const_J_h, def_const_Q_gkrah, def_const_f,  def_const_s_hl, def_const_delta_zero,
                           def_const_delta_plus_delta, def_const_delta_moins_delta, def_const_delta_plus_b_hl_in, def_const_delta_moins_b_hl_out, def_const_demand]

    CONSTRAINTS_MATERNITY=[def_const_P_gkr, def_const_P_gk, def_const_d_gr_maternity, def_const_q_g, def_const_q_gk,
                           def_const_J_h, def_const_m_hl, def_const_delta_zero, def_const_delta_plus_delta, def_const_delta_moins_delta,
                           def_const_delta_plus_b_hl_in, def_const_delta_moins_b_hl_out]

    match params_system["mode"]:
        case "slack":
            print("Defining set of constraints with slack capacity.")
            for fn in CONSTRAINTS_SLACK:
                fn(LP, vars_system, params_system)
        case "maternities":
            print("Defining constraints for maternity instance.")
            for fn in CONSTRAINTS_MATERNITY:
                fn(LP, vars_system, params_system)
        case _:
            print("Defining default set of constraints.")
            for fn in CONSTRAINTS_DEFAULT:
                fn(LP, vars_system, params_system)



def preregister_variables(LP, vars_system, params_system):
    """Register all variables into LP once, upfront"""
    all_vars = []

    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            all_vars.append(vars_system.P_gk[g][k])
            for r in params_system["R"]:
                all_vars.append(vars_system.P_gkr[g][k][r])
                for a in params_system["A_idx"][g][k]:
                    for h in params_system["H"]:
                        all_vars.append(vars_system.P[g][k][r][a][h])
                        all_vars.append(vars_system.Q[g][k][r][a][h])
    for h in params_system["H"]:
        for l in params_system["L"]:
            all_vars.append(vars_system.Delta_plus[h][l])
            all_vars.append(vars_system.Delta_moins[h][l])
            all_vars.append(vars_system.z_hl_plus[h][l])
            all_vars.append(vars_system.z_hl_moins[h][l])

    LP.addVariables(all_vars)

def fast_add(LP, constraint):
    """Bypass addConstraint's addVariables call — variables pre-registered."""
    name = LP.unusedConstraintName()
    LP.constraints[name] = constraint