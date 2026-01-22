##########################
### TOOLS TO READ DATA ###
##########################



# Output the maximum input from an array

def maxSize(A):
    max_s = A[0]
    for i in range(1, len(A)):
        if A[i] > max_s:
            max_s = A[i]
    Z = []
    for j in range(max_s):
        Z.append(j)
    return Z



# Output the maximum intput from a matrix of dimension 2

def maxSize2D(A):
    max_s = A[0][0]
    for i in range(len(A)):
        for j in range(len(A[i])):
            if A[i][j] > max_s:
                max_s = A[i][j]
    Z = []
    for j in range(max_s):
        Z.append(j)
    return Z



# Read a number (G, R, etc.) from a string

def readNumberFromData(s):
    Z = []
    s2 = ""
    j = 0
    while s[j] != '\n':
        s2 += s[j]
        j += 1
    number = int(s2)
    for i in range(number):
        Z.append(i)
    return Z



# Read an array of integers (K_g, etc.) from a string

def readArrayFromData(s):
    Z = []
    s = s.split('\n')
    for i in range(len(s) - 1):
        s1 = s[i].split(', ')
        Z.append(int(s1[1]))
    return Z



# Read a matrix of size g x k (c_gk, A_gk, etc.) from a string

def readMatrix2DFromData(s, A, B):
    Z = [[0 for _ in range(len(B))] for _ in range(len(A))]
    s = s.split('\n')
    for i in range(len(s) - 1):
        s2 = s[i].split(', ')
        Z[int(s2[0])][int(s2[1])] = int(s2[2])
    return Z



# Read a number (c, etc.) from a string

def readNumberFromData_2(s):
    Z = []
    s2 = ""
    j = 0
    while s[j] != '\n':
        s2 += s[j]
        j += 1
    number = float(s2)
    Z.append(number)
    return Z



# Read a matrix of dimension 3 (O_gk, etc.) from a string

def readMatrix3DFromData(s, A, B, C):
    Z = [[[0 for _ in range(len(C))] for _ in range(len(B))] for _ in range(len(A))]
    s = s.split('\n')
    for i in range(len(s) - 1):
        s2 = s[i].split(', ')
        Z[int(s2[0])][int(s2[1])][int(s2[2])] = float(s2[3])
    return Z



# Read a matrix of dimension 4 (t_gkal, etc.) from a string

def readMatrix4DFromData(s, A, B, C, D):
    Z = [[[[0 for _ in range(len(D))] for _ in range(len(C))] for _ in range(len(B))] for _ in range(len(A))]
    s = s.split('\n')
    for i in range(len(s) - 1):
        s2 = s[i].split(', ')
        Z[int(s2[0])][int(s2[1])][int(s2[2])][int(s2[3])] = float(s2[4])
    return Z



# Read an array of floats (Over_q_g, Under_q_g, etc.) from a string

def readArrayFromData_2(s):
    Z = []
    s = s.split('\n')
    for i in range(len(s) - 1):
        s1 = s[i].split(', ')
        Z.append(float(s1[1]))
    return Z



# Read a matrix of size g x k (c_gk, A_gk, etc.) from a string

def readMatrix2DFromData_2(s, A, B):
    Z = [[0 for _ in range(len(B))] for _ in range(len(A))]
    s = s.split('\n')
    for i in range(len(s) - 1):
        s2 = s[i].split(', ')
        Z[int(s2[0])][int(s2[1])] = float(s2[2])
    return Z
    


# Read a matrix where the last element is a list from a string
# For the set I_{g,u}

def readMatrixListFromData(s, A, B, C):
    Z = [[[0 for _ in range(C)] for _ in range(len(B))] for _ in range(len(A))]
    s = s.split('\n')
    for i in range(len(s) - 1):
        s2 = s[i].split(', ')
        z = []
        for i in range(2, len(s2)):
            z.append(int(s2[i]))
        Z[int(s2[0])][int(s2[1])] = z
    return Z



# Read a matrix where the last element is a list from a string
# For the set O_gk

def readMatrixListFromData_O_gk(s, A, B, C, H):
    Z = [[[0 for _ in range(C)] for _ in range(len(B))] for _ in range(len(A))]
    s = s.split('\n')
    z_H = [i for i in range(len(H))]
    for i in range(len(s) - 1):
        s2 = s[i].split(', ')
        for j in range(len(s2)):
            s2[j] = int(s2[j])
        z = [i for i in range(len(H))]
        for h in H:
            if h not in s2:
                z.remove(h)
        Z[int(s2[0])][int(s2[1])] = z
    return Z



# Read a matrix where the last element is a list from a string
# For the set J_h

def readMatrixListFromData_J_h(s, A, B, H):
    Z = [[0 for _ in range(B)] for _ in range(len(A))]
    s = s.split('\n')
    z_H = [i for i in range(len(H))]
    for i in range(len(s) - 1):
        s2 = s[i].split(', ')
        for j in range(len(s2)):
            s2[j] = int(s2[j])
        z = [i for i in range(len(H))]
        for h in H:
            if h not in s2:
                z.remove(h)
        Z[int(s2[0])] = z
    return Z



# Read a matrix where the last element is a list from a string
# For the set N_gka

def readMatrixListFromData_N_gka(s, A, B, C):
    Z_1 = [[0 for _ in range(len(B))] for _ in range(len(A))]
    Z_2 = [[0 for _ in range(len(B))] for _ in range(len(A))]
    s = s.split('\n')
    for i in range(len(s) - 1):
        s2 = s[i].split(', ')
        for j in range(len(s2)):
            s2[j] = int(s2[j])
        z1 = []
        z2 = []
        j = 2
        while j < len(s2):
            z1.append(s2[j])
            j += 1
            z2.append(s2[j])
            j += 1
        Z_1[int(s2[0])][int(s2[1])] = z1
        Z_2[int(s2[0])][int(s2[1])] = z2
    return Z_1, Z_2



#############################################
### READ DATA FROM THE COMPLETE DATA FILE ###
#############################################



# Define the function to read the complete data file

def readCompleteDataFile(stri):
    with open(stri, 'r') as file:
        
        al = file.readlines()
        sl = ""
        j = 0
        
        for i in range(25):
            s1 = al[j + 1]
            s2 = al[j + 2]
            while s1[0] != '\n' or s2[0] != '#':
                j += 1
                if al[j+1][0] != '\n' or al[j+2][0] != '#':
                    sl += s2
                s1 = al[j + 1]
                s2 = al[j + 2]
                
            if i == 0:
                G = readNumberFromData(sl)
            elif i == 1:
                K_g = readArrayFromData(sl)
            elif i == 2:
                R = readNumberFromData(sl)
            elif i == 3:
                A_gk = readMatrix2DFromData(sl, G, maxSize(K_g))
            elif i == 4: 
                H = readNumberFromData(sl)
            elif i == 5:
                L = readNumberFromData(sl)
            elif i == 6:
                c_gk = readMatrix2DFromData_2(sl, G, maxSize(K_g))
            elif i == 7:
                alpha = readNumberFromData_2(sl)
            elif i == 8:
                w_rh = readMatrix2DFromData_2(sl, R, H)
            elif i == 9:
                D = readNumberFromData_2(sl)
            elif i == 10:
                d_gr = readMatrix2DFromData_2(sl, G, R)
            elif i == 11:
                t_gkal = readMatrix4DFromData(sl, G, maxSize(K_g), maxSize2D(A_gk), L)
            elif i == 12:
                m_hl = readMatrix2DFromData_2(sl, H, L)
            elif i == 13:
                Under_q_g = readArrayFromData_2(sl)
            elif i == 14:
                Over_q_g = readArrayFromData_2(sl)
            elif i == 15:
                U = readArrayFromData(sl)
            elif i == 16:
                I_gu = readMatrixListFromData(sl, G, maxSize(U), 1)
            elif i == 17:
                Under_q_gu = readMatrix2DFromData_2(sl, G, maxSize(K_g))
            elif i == 18:
                Over_q_gu = readMatrix2DFromData_2(sl, G, maxSize(K_g))
            elif i == 19:
                O_gk = readMatrixListFromData_O_gk(sl, G, maxSize(K_g), 1, H)
            elif i == 20:
                J_h = readMatrixListFromData_J_h(sl, H, 1, H)
            elif i == 21:
                #f_gk = readMatrix2DFromData_2(sl, G, maxSize(K_g))
                f = readNumberFromData_2(sl)
            elif i == 22:
                b_hl = readMatrix2DFromData_2(sl, H, L)
            elif i == 23:
                delta_l = readArrayFromData_2(sl)
            elif i == 24:
                N_gka_1, N_gka_2 = readMatrixListFromData_N_gka(sl, G, maxSize(K_g), A_gk)
            
            if s2[0] == '#':
                j += 2
                sl = ""
        b_hl_in = b_hl
        b_hl_out = b_hl 
        return G, K_g, R, A_gk, H, L, c_gk, alpha, w_rh, D, d_gr, t_gkal, m_hl, Under_q_g, Over_q_g, U, I_gu, Under_q_gu, Over_q_gu, O_gk, J_h, f, b_hl_in, b_hl_out, delta_l, N_gka_1, N_gka_2
