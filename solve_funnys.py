import pandas as pd
import pulp as pl
import math 

TRY_WRITE_CSV = True

#  CONJUNTOS  

I = ["Antofagasta", "Valparaíso", "Santiago", "Concepción", "Puerto Montt", "Rancagua"]
J = ["pequena", "grande"]
K = ["r1", "r2", "r3", "r4", "r5", "r6"]
F = ["AT1", "AT2", "AT3"]
T = [1, 2, 3]

# PARÁMETROS  

# Demanda base y tasas de crecimiento
demanda_actual = {
    "r1": 951_776, "r2": 967_364, "r3": 512_051,
    "r4": 386_248, "r5": 946_174, "r6": 303_445,
}
tasa_crec = {"r1": 0.16, "r2": 0.22, "r3": 0.26, "r4": 0.15, "r5": 0.39, "r6": 0.30}

# Construir D[(k,t)]
D = {}
for k in K:
    base = demanda_actual[k]; r = tasa_crec[k]
    for t in T:
        D[(k, t)] = int(math.ceil(base * ((1.0 + r) ** (t - 1))))

# Capacidades por tipo de planta (constantes por año)
cap_peq = 4_636_446
cap_gra = 14_966_773
P_cap = {}
for t in T:
    P_cap[("pequena", t)] = cap_peq
    P_cap[("grande",  t)] = cap_gra

# Costos por ciudad × tipo de planta
C_open, C_fixed, C_var = {}, {}, {}
datos_peq = {
    "Antofagasta": {"fixed": 18_236_639, "var": 28.20, "open": 86_626_147},
    "Valparaíso":  {"fixed":  8_838_286, "var": 41.68, "open":115_721_215},
    "Santiago":    {"fixed":  6_840_758, "var": 18.57, "open":172_235_977},
    "Rancagua":    {"fixed": 13_378_246, "var": 17.68, "open":         0},
    "Concepción":  {"fixed": 26_394_217, "var": 50.11, "open": 57_494_934},
    "Puerto Montt":{"fixed":  3_678_737, "var": 43.55, "open":175_561_277},
}
datos_gra = {
    "Antofagasta": {"fixed": 60_788_796, "var": 28.20, "open":201_456_157},
    "Valparaíso":  {"fixed": 32_734_393, "var": 41.68, "open":199_519_337},
    "Santiago":    {"fixed": 32_575_039, "var": 18.57, "open":291_925_385},
    "Rancagua":    {"fixed": 53_512_984, "var": 17.68, "open":299_031_830},
    "Concepción":  {"fixed": 65_985_543, "var": 50.11, "open":179_671_671},
    "Puerto Montt":{"fixed": 26_276_695, "var": 43.55, "open":337_617_842},
}
for i in I:
    C_fixed[(i,"pequena")] = float(datos_peq[i]["fixed"])
    C_var[(i,"pequena")]   = float(datos_peq[i]["var"])
    C_open[(i,"pequena")]  = float(datos_peq[i]["open"])
    C_fixed[(i,"grande")]  = float(datos_gra[i]["fixed"])
    C_var[(i,"grande")]    = float(datos_gra[i]["var"])
    C_open[(i,"grande")]   = float(datos_gra[i]["open"])

# Costos de transporte C_trans[(i,k,f)]
AT1 = {
    "Antofagasta":[1.06,2.80,10.29,4.87,6.41,10.35],
    "Valparaíso":[3.49,6.19,3.39,6.77,3.07,6.61],
    "Santiago":[6.38,5.88,5.63,1.01,3.15,5.67],
    "Rancagua":[3.44,1.48,2.79,2.80,5.30,1.29],
    "Concepción":[5.94,7.33,1.80,9.48,2.82,8.25],
    "Puerto Montt":[2.57,9.63,4.84,6.64,6.48,8.54],
}
AT2 = {
    "Antofagasta":[10.03,4.09,4.55,7.84,5.33,10.63],
    "Valparaíso":[10.52,1.82,3.91,8.20,5.88,2.33],
    "Santiago":[1.90,8.89,6.55,9.71,7.03,10.23],
    "Rancagua":[2.06,10.17,2.12,6.11,3.79,6.19],
    "Concepción":[2.54,6.95,8.57,10.50,4.85,5.31],
    "Puerto Montt":[7.92,10.32,1.41,4.94,2.74,8.08],
}
AT3 = {
    "Antofagasta":[9.86,4.30,8.10,9.63,7.40,6.47],
    "Valparaíso":[1.58,2.71,3.08,5.91,7.99,5.11],
    "Santiago":[9.13,10.03,6.77,5.70,3.62,8.58],
    "Rancagua":[8.95,7.37,10.29,3.34,2.21,4.58],
    "Concepción":[9.62,3.78,5.19,2.61,3.19,1.78],
    "Puerto Montt":[10.32,8.88,10.87,10.38,5.83,1.54],
}
C_trans = {}
reg_ix = {r:i for i,r in enumerate(K)}  # r1->0,...
for i in I:
    for k in K:
        C_trans[(i,k,"AT1")] = float(AT1[i][reg_ix[k]])
        C_trans[(i,k,"AT2")] = float(AT2[i][reg_ix[k]])
        C_trans[(i,k,"AT3")] = float(AT3[i][reg_ix[k]])


def ensure_all_keys_exist():
    for i in I:
        for j in J:
            assert (i,j) in C_open  ; assert (i,j) in C_fixed ; assert (i,j) in C_var
    for j in J:
        for t in T:
            assert (j,t) in P_cap
    for i in I:
        for k in K:
            for f in F:
                assert (i,k,f) in C_trans
    for k in K:
        for t in T:
            assert (k,t) in D
ensure_all_keys_exist()

# MODELO MATEMÁTICO  


m = pl.LpProblem("Funnys_Facility_Distribution", pl.LpMinimize)

# Variables
x = pl.LpVariable.dicts("x", (I,J), lowBound=0, upBound=1, cat="Binary")
y = pl.LpVariable.dicts("y", (I,K,F,T), lowBound=0, cat="Integer")


# q[i,t] = flujo total que sale de ciudad i en año t
q   = pl.LpVariable.dicts("q", (I,T), lowBound=0, cat="Continuous")
# qjt[i,j,t] = parte de q[i,t] atribuida a planta de tipo j en i, año t
qjt = pl.LpVariable.dicts("qjt", (I,J,T), lowBound=0, cat="Continuous")

# Función objetivo

open_fixed_cost = pl.lpSum((C_open[(i,j)] + C_fixed[(i,j)]) * x[i][j] for i in I for j in J)
prod_var_cost  = pl.lpSum(C_var[(i,j)] * qjt[i][j][t] for i in I for j in J for t in T)
trans_cost     = pl.lpSum(C_trans[(i,k,f)] * y[i][k][f][t] for i in I for k in K for f in F for t in T)
m += open_fixed_cost + prod_var_cost + trans_cost

# Enlaces de q con y, y reparto q -> qjt
for i in I:
    for t in T:
        m += q[i][t] == pl.lpSum(y[i][k][f][t] for k in K for f in F), f"def_q_{i}_{t}"
        m += pl.lpSum(qjt[i][j][t] for j in J) == q[i][t], f"split_q_to_qjt_{i}_{t}"

# Activación qjt por tipo con Big-M apretado (Mjt = capacidad del tipo)
for i in I:
    for j in J:
        for t in T:
            m += qjt[i][j][t] <= P_cap[(j,t)] * x[i][j], f"activate_qjt_{i}_{j}_{t}"



#  RESTRICCIONES 


# (1) Satisfacción de demanda por región y año
for k in K:
    for t in T:
        m += pl.lpSum(y[i][k][f][t] for i in I for f in F) >= D[(k,t)], f"demand_{k}_{t}"

# (2) Capacidad por ciudad y año
for i in I:
    for t in T:
        m += pl.lpSum(y[i][k][f][t] for k in K for f in F) <= \
             pl.lpSum(P_cap[(j,t)] * x[i][j] for j in J), f"city_capacity_{i}_{t}"

# (3) Exactamente una planta por ciudad *
for i in I:
    m += pl.lpSum(x[i][j] for j in J) <= 1, f"at_most_one_plant_{i}"

# (4) Planta existente en Rancagua
if "Rancagua" in I and "pequena" in J and "grande" in J:
    m += x["Rancagua"]["pequena"] == 1, "rancagua_pequena_1"
    m += x["Rancagua"]["grande"]  == 0, "rancagua_grande_0"


#  SOLVER  
m.solve(pl.PULP_CBC_CMD(msg=False))
print("Status:", pl.LpStatus[m.status])
print("Objective value:", pl.value(m.objective))

# RESULTADOS 
x_rows, y_rows = [], []
for i in I:
    for j in J:
        val = x[i][j].value() or 0.0
        x_rows.append({"city": i, "plant_type": j, "open": val})

for i in I:
    for k in K:
        for f in F:
            for t in T:
                val = y[i][k][f][t].value() or 0.0
                if abs(val) > 1e-6:
                    y_rows.append({"city": i, "region": k, "transport": f, "year": t, "flow": val})

print("\n=== Variables x (apertura de plantas) ===")
for i in I:
    for j in J:
        print(f"x[{i},{j}] = {x[i][j].value()}")

print("\n=== Variables y (flujos) ===")
for i in I:
    for k in K:
        for f in F:
            for t in T:
                print(f"y[{i},{k},{f},{t}] = {y[i][k][f][t].value()}")

if TRY_WRITE_CSV:
    pd.DataFrame(x_rows).to_csv("solution_plants.csv", index=False)
    pd.DataFrame(y_rows).to_csv("solution_flows.csv", index=False)
    print("\nWrote solution_plants.csv and solution_flows.csv")
