from pyomo.environ import *

m = ConcreteModel()
m.H = Set(initialize=['1', '2']) #Suppliers
m.I = Set(initialize=['1', '2','3']) #Processes
m.J = Set(initialize=['1', '2', '3']) #Demand markets
m.T = Set(initialize=['1', '2', '3']) #Time set

# Define parameters for cost, supply, and demand
#First set of distances (h,i)
distance1 = {('1','1'): 2.5,
            ('1','2'): 1.7,
            ('1','3'): 1.8,
            ('2','1'): 2.5,
            ('2','2'): 1.8,
            ('2','3'): 1.4,
            }
#Second set of distances (i,j)
distance2 = {('1','1'): 2.5,
            ('1','2'): 1.7,
            ('1','3'): 1.8,
            ('2','1'): 2.5,
            ('2','2'): 1.8,
            ('2','3'): 1.4,
            ('3','1'): 2.5,
            ('3','2'): 1.7,
            ('3','3'): 1.8,
            }
#Supply h,t
supply = {('1','1'): 350,
            ('1','2'): 355,
            ('1','3'): 345,
            ('2','1'): 605,
            ('2','2'): 600,
            ('2','3'): 610,
            }
#Demand j,t
demand = {('1','1'): 325,
            ('1','2'): 330,
            ('1','3'): 320,
            ('2','1'): 300,
            ('2','2'): 305,
            ('2','3'): 310,
            ('3','1'): 270,
            ('3','2'): 275,
            ('3','3'): 280,
            }
#Conversion factors of processes (i)
conversion= {('1'): 1,
            ('2'): 0.9,
            ('3'): 0.8,
            }
#Cost factors of processes (i)
price = {('1'): 100,
            ('2'): 85,
            ('3'): 80,
            }

m.x1 = Var(m.H, m.I, m.T, domain = NonNegativeReals)
m.x2 = Var(m.I, m.J , m.T, domain = NonNegativeReals)
m.a = Var(domain = NonNegativeReals)
m.b = Var(domain = NonNegativeReals)
m.c = Var(domain = NonNegativeReals)

m.p_inp = Var(m.I, m.T, domain = NonNegativeReals)
m.p_out = Var(m.I, m.T, domain = NonNegativeReals)

#Prices rules
def cost_1(m):
    return m.a == sum((90*distance1[h,i]/1000)* m.x1[h,i,t]   for h in m.H for i in m.I for t in m.T)
m.con1 = Constraint(rule = cost_1)

def cost_2(m):
    return m.b == sum((90*distance2[i,j]/1000)* m.x2[i,j,t] for i in m.I for j in m.J for t in m.T)
m.con2 = Constraint(rule = cost_2)
#
def cost_3(m):
    return m.c == sum(price[i]* m.p_inp[i,t] for i in m.I for t in m.T)    
m.con3 = Constraint(rule = cost_3)

def objective_rule(m):
    return m.a+m.b+m.c
m.total_cost = Objective(rule = objective_rule, sense=minimize)

def supply_const(m,h,t):
    return sum(m.x1[h, i, t] for i in m.I) <= supply[h,t]
m.con4 = Constraint(m.H, m.T, rule = supply_const)
#
def demand_const(m,j,t):
    return sum(m.x2[i, j, t] for i in m.I) >= demand[j,t]
m.con5 = Constraint(m.J, m.T, rule = demand_const)

def input_const(m,i,t):
    return sum(m.x1[h, i, t] for h in m.H) == m.p_inp[i,t]
m.con6 = Constraint(m.I, m.T, rule = input_const)

def output_const(m,i,t):
    return m.p_inp[i,t]*conversion[i] == m.p_out[i,t]
m.con7 = Constraint(m.I, m.T, rule = output_const)

def output_const(m,i,t):
    return m.p_out[i,t] == sum(m.x2[i, j, t] for j in m.J)
m.con8 = Constraint(m.I, m.T, rule = output_const)

opt = SolverFactory('gurobi')
results = opt.solve(m, tee = True)

print(results)


!cat results.yml