import gurobipy as gp
from gurobipy import GRB

# Initialize the model
model = gp.Model("Glambia")

# Parameters (example values)
M = [0,1]  # Number of manufacturers
W = [0,1,2]  # Number of warehouses
D = [0,1,2,3]  # Number of distribution centers
B = [0,1]  # Number of bonded warehouses
O = [0,1]  # Number of cross-docking facilities
K = [0,1]  # Number of truck types
S = [0,1,2]  # Number of suppliers

# Example parameter values (these should be replaced with actual data)
capacity_warehouse = [3000, 3000, 3000]
capacity_bonded_warehouse=[3000, 3000, 3000]
capacity_crossdocking = [2000, 2000]
quantity_inventory = [50, 100, 150]
fixed_emission_cm = [10, 20]
emission_cost_per_unit_distance = 5
holding_cost = [5, 10]
production_limit = [12000, 12000]
fixed_cost_op = [1000, 2000]
carbon_credits = 1000
fraction_defective = 0.05
carbon_tax = 50
finished_goods_import = 500
raw_material_import = 300
fixed_cost_import_fg = 100
fixed_cost_import_rm = 50
packaging_goods_supplied = 400
fixed_cost_packaging = 20
demand_distributor = [10, 20,15,20]
demand_manufacturer=[1000,2000]
quantity_product = [100, 200]
emission_storage = [0.1, 0.2]
cost_transport_per_unit_distance = {
    'large_truck': 10,
    'small_truck': 8
}
distance = [
    [10, 2000, 30], 
    [4000, 50, 60]
]

distance1 = [
    [10,2000], 
    [6000,70],
    [80,10]
]

distance2 = [
    [10, 2000], 
    [2000, 70]
]



# Decision Variables
Bm = model.addVars(M, vtype=GRB.BINARY, name="Bm")
Bo = model.addVars(O, vtype=GRB.BINARY, name="Bo")
Bb = model.addVars(B, vtype=GRB.BINARY, name="Bb")
Asb = model.addVars(S, B, vtype=GRB.BINARY, name="Asb")
Asm = model.addVars(S, M, vtype=GRB.BINARY, name="Asm")
Abw = model.addVars(B, W, vtype=GRB.BINARY, name="Abw")
Abm = model.addVars(B, M, vtype=GRB.BINARY, name="Abm")
Amw = model.addVars(M, W, vtype=GRB.BINARY, name="Amw")
Awd = model.addVars(W, D, vtype=GRB.BINARY, name="Awd")
Awo = model.addVars(W, O, vtype=GRB.BINARY, name="Awo")
Aow = model.addVars(O, W, vtype=GRB.BINARY, name="Aow")

zeta_mw=model.addVars(M,W, vtype=GRB.CONTINUOUS,lb=0,name='zeta_mw')
zeta_wd=model.addVars(W,D, vtype=GRB.CONTINUOUS,lb=0,name='zeta_wd')
zeta_sb=model.addVars(S,B, vtype=GRB.CONTINUOUS,lb=0,name='zeta_sb')
zeta_sm=model.addVars(S,M, vtype=GRB.CONTINUOUS,lb=0,name='zeta_sm')
zeta_wo=model.addVars(W,O, vtype=GRB.CONTINUOUS,lb=0,name='zeta_wo')
zeta_ow=model.addVars(O,W, vtype=GRB.CONTINUOUS,lb=0,name='zeta_ow')
zeta_bw=model.addVars(B,W, vtype=GRB.CONTINUOUS,lb=0,name='zeta_bw')
omega_w=model.addVars(W, vtype=GRB.CONTINUOUS,lb=0,name='omega_w')
omega_b=model.addVars(B, vtype=GRB.CONTINUOUS,lb=0,name='omega_b')

# Objective Function
model.setObjective(

    # Fixed cost
    (fixed_cost_import_fg * finished_goods_import) +
    (fixed_cost_import_rm * raw_material_import) +
    (fixed_cost_packaging * packaging_goods_supplied) +
    

    # Cost of transportation  from supplier to bonded warehouse
    gp.quicksum(
        cost_transport_per_unit_distance["large_truck"] * distance1[s][b] * Asb[s][b]
        for s in S for b in B
    ) +
    gp.quicksum(
        emission_cost_per_unit_distance *carbon_tax* distance[s][b] * Asb[s][b]
        for s in S for b in B
    ) +
    
    # Cost of transportation  from supplier to maufacturer
    gp.quicksum(
        cost_transport_per_unit_distance["large_truck"] * distance1[s][m] * Asm[s][m]
        for s in range(S) for m in range(M) 
    ) +
    gp.quicksum(
        emission_cost_per_unit_distance *carbon_tax* distance1[s][m] * Asm[s][m]
        for s in range(S) for m in range(M)
    )+
    
    #Holding Cost in bonded warehouse along with storage emissions in bonded warehouses to warehouses 
    gp.quicksum(
        holding_cost[b] *(1-fraction_defective)* (quantity_product[b]-zeta_bw[b][w])*Bb[b]
        for b in range(B) for w in range(W)
    ) +
    gp.quicksum(
        emission_storage[b] *(1-fraction_defective)*(quantity_product[b]-zeta_bw[b][w])* Bb[b]
        for b in range(B) for w in range(W)
    ) +
    
    #Holding Cost in bonded warehouse along with storage emissions in bonded warehouses to warehouses 
    gp.quicksum(
        holding_cost[b] *(1-fraction_defective)* (quantity_product[b]-zeta_bw[b][m])* Bb[b]
        for b in range(B) for m in range(M)
    ) +
    gp.quicksum(
        emission_storage[b] *(1-fraction_defective)*(quantity_product[b]-zeta_bw[b][m])* Bb[b]
        for b in range(B) for m in range(M)
    ) +

    # Cost of transportation  from bonded warehouse to warehouse
    gp.quicksum(
        cost_transport_per_unit_distance["large_truck"] * distance[b][w] * Abw[b,w]
        for b in range(B) for w in range(W) 
    ) +
    gp.quicksum(
        emission_cost_per_unit_distance *carbon_tax* distance[b][w] * Abw[b,w]
        for b in range(B) for w in range(W)
    )+
    
     # Cost of transportation  from bonded warehouse to maufacturer
    gp.quicksum(
        cost_transport_per_unit_distance["large_truck"] * distance2[b][m] * Abm[b,m]
        for b in range(B) for m in range(M)
    ) +
    gp.quicksum(
        emission_cost_per_unit_distance *carbon_tax* distance2[b][m] * Abm[b,m]
        for b in range(B) for m in range(M)
    ) +
    
    # Fixed cost of maufacturer 
    gp.quicksum(
        fixed_emission_cm[m]*carbon_tax*Bm[m]
        for m in range(M) 
    ) +
    gp.quicksum(
    fixed_cost_op[m]*Bm[m]   for m in range(M) 
    )+

    #Holding Cost in maufacturer along with storage emissions in maufacturer to warehouses 
    gp.quicksum(
        holding_cost[m] *(quantity_product[m]-zeta_mw)* Amw[m,w]
        for m in range(M) for w in range(W)
    ) +
    gp.quicksum(
        emission_storage[m] *carbon_tax*(quantity_product[m]-zeta_mw)* Amw[m,w]
        for m in range(M) for w in range(W)
    ) +

    # Cost of transportation  from maufacturer to warehouse
    gp.quicksum(
        cost_transport_per_unit_distance["large_truck"] * distance[m][w] * Amw[m,w]
        for m in range(M) for w in range(W) 
    ) +
    gp.quicksum(
        emission_cost_per_unit_distance *carbon_tax* distance[m][w] * Amw[m,w]
        for m in range(M) for w in range(W) 
    ) +

    # Cost of transportation  from maufacturer to warehouse
    gp.quicksum(
        cost_transport_per_unit_distance["large_truck"] * distance[w][d] * Awd[w,d]
        for w in range(W) for d in range(D) 
    ) +
    gp.quicksum(
        emission_cost_per_unit_distance *carbon_tax* distance[w][d] * Awd[w,d]
        for w in range(W) for d in range(D)  
    ) +
    
    # Cost of transportation  from warehouse to crossdocking
    gp.quicksum(
        cost_transport_per_unit_distance["large_truck"] * distance[w][o] * Awo[w,o]
        for w in range(W) for o in range(O) 
    ) +
    gp.quicksum(
        emission_cost_per_unit_distance *carbon_tax* distance[w][o] * Awo[w,o]
        for w in range(W) for o in range(O) 
    ) +
    
    # Cost of transportation  from crossdocking to warehouse 
    gp.quicksum(
        cost_transport_per_unit_distance["small_truck"] * distance[o][w] * Aow[o,w]
         for o in range(O) for w in range(W) 
    ) +
    gp.quicksum(
        emission_cost_per_unit_distance *carbon_tax* distance[o][w] * Aow[o,w]
        for o in range(O) for w in range(W) 
    ) +
    
    #Holding cost at cross docking
    gp.quicksum(
        holding_cost[o] *(1-fraction_defective)* (quantity_product[o]-zeta_ow)* Bo[o]
        for o in range(O) for w in range(W)
    ),
    GRB.MINIMIZE,
)



# Constraints

# Carbon constraints 
model.addConstr(
    gp.quicksum(fixed_emission_cm[m] for m in range(M)) +
    gp.quicksum(emission_cost_per_unit_distance  * distance[m][w]  for m in range(M) for w in range(W)) +
    gp.quicksum(emission_cost_per_unit_distance  * distance[s][b]  for s in range(S) for b in range(B)) +
    gp.quicksum(emission_cost_per_unit_distance  * distance1[s][m] for s in range(S) for m in range(M)) +
    gp.quicksum(emission_cost_per_unit_distance  * distance[b][w]  for b in range(B) for w in range(W)) +
    gp.quicksum(emission_cost_per_unit_distance  * distance[w][o]  for w in range(W) for o in range(O)) +
    gp.quicksum(emission_cost_per_unit_distance  * distance[o][w] for o in range(O) for w in range(W)) +
    gp.quicksum(emission_cost_per_unit_distance  * distance[w][d] for w in range(W) for d in range(D)) +

    gp.quicksum(emission_storage[m] for m in range(M))+
    gp.quicksum(emission_storage[w] for w in range(W))+
    gp.quicksum(emission_storage[b] for b in range(B))+
    gp.quicksum(emission_storage[o] for o in range(O))
    <= carbon_credits
)


# Capacity Constraints 
model.addConstrs(zeta_sb[s][b] <= capacity_bonded_warehouse[b] for s in range(S) for b in range(B))
model.addConstrs(zeta_sm[s][m] >= demand_manufacturer[m] for s in range(S) for m in range(M))
model.addConstrs(zeta_mw[m][w] <= capacity_warehouse[w] for m in range(M) for w in range(W))
model.addConstrs(zeta_wo[w][o] <= capacity_crossdocking[o] for w in range(W) for o in range(O))
model.addConstrs(zeta_wd[w][d] <= demand_distributor[d] for w in range(W) for d in range(D))


# Ensure amount transferred is non-negative
model.addConstrs((capacity_warehouse[w] >= 0 for w in range(W)))
model.addConstrs((capacity_bonded_warehouse[b] >= 0 for b in range(B)))
model.addConstrs((zeta_bw[b][w] >= 0 for b in range(B) for w in range(W)))
model.addConstrs((zeta_mw[m][w] >= 0 for m in range(M) for w in range(W)))
model.addConstrs((zeta_wd[w][d] >= 0 for w in range(W) for d in range(D)))
model.addConstrs((zeta_sm[s][m] >= 0 for s in range(S) for m in range(M)))
model.addConstrs((zeta_wo[w][o] >= 0 for w in range(W) for o in range(O)))
model.addConstrs((zeta_sb[s][b] >= 0 for s in range(S) for b in range(B)))
model.addConstrs((zeta_ow[o][w] >= 0 for o in range(O) for w in range(W)))


# Production Limit Constraint
model.addConstrs((zeta_mw[m][w] <= production_limit[m] for m in range(M) for w in range(W)), name='production_limit')


# Persibility Constraint
model.addConstr(fraction_defective <= 1)     


# Ensure quantity product constraint
model.addConstrs(quantity_product[b] >= zeta_bw[b][w] for b in range(B) for w in range(W))



# Optimize the model
model.optimize()



# Check model status
status = model.Status
if status == GRB.Status.OPTIMAL:
    print("Optimal solution found")
elif status == GRB.Status.INFEASIBLE:
    print("Model is infeasible")
    model.computeIIS()
    model.write("infeasible_model.ilp")
else:
    print(f"Optimization was stopped with status {status}")
