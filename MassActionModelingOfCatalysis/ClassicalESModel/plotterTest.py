import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import random
import cobra.io

myModel = cobra.io.read_sbml_model('ClassicalESModel.xml')
myModel.solver = 'gurobi'

sol = myModel.optimize()

fvaSol = cobra.flux_analysis.flux_variability_analysis(myModel,loopless=True)
print fvaSol
#print sol.fluxes
for x in myModel.reactions:
    print str(x.id) + ' : ' + str(x.reaction) + ' : '  + str(sol[x.id])


def func(y,t,k1,kO1,k2,inletS):
    E,S,ES,P = y
    dydt = [-k1*E*S + k2*ES + kO1*ES ,
            inletS - k1*E*S + kO1*ES ,
            k1*E*S - k2*ES - kO1*ES,
            k2*ES]
    return dydt

def params(Eo,So,v,sigma):
    k1 = sigma
    Ces = Eo - v[0]/So/k1
    kneg1 =v[1] / Ces
    k2 = v[2] / Ces
    return (k1,kneg1,k2)

sol2 = [sol[x.id] for x in myModel.reactions]
fig,ax1 = plt.subplots(2,2)
fig2,ax2 = plt.subplots(2,2)

t = np.linspace(0, 1000, 1000)
file = open('RandK1Testing.txt','w')
meanError = []

p = [random.uniform(.0000001,10) for _ in range(1000) ]
p = [10**x for x in range(10)]
p = [10]
for z in p:

    sol3 = [x * 1. for x in sol2]

    y0 = [5.0, 1000., 0.0 , 0.0]


    file.write(str(z)+ '\n')
    k1,k01,k2 = params(y0[0],y0[1],sol3,z)
    #print type(sol)
    file.write(str(k1)+' ')
    file.write(str(k01)+ ' ')
    file.write(str(k2)+ '\n')

    inletS = sol3[3]
    sol = odeint(func, y0, t, args=(k1,k01,k2,sol3[3]))

    #fig.add_subplot(221)
    ax1[0][0].plot(t, sol[:, 0])
    ax1[0][0].set_xlabel('t')
    ax1[0][0].set_ylabel('E')
    ax1[0][0].set_title('           Reaction Network Dynamics with k1 1-10e')


   # fig2.add_subplot(221)
    ax2[0][0].scatter(z, sol[-1, 0])
   # fig2.xlabel('k1')
   # fig2.ylabel('E')
   # fig2.title('           Final Concentration Phase Plot')
   # ax2.set




    finalConc = sol[-1,:]
    finalFlux = [k1*finalConc[0]*finalConc[1]]
    finalFlux.append(k01*finalConc[2])
    finalFlux.append(k2*finalConc[2])
    print('k1 = '+str(z))
    print finalFlux
    print '\n\n'

    [file.write(str(x) + ' ') for x in finalFlux]
    file.write('\n'+str(np.mean(np.subtract(sol3[:-2],finalFlux)**2))+ '\n')
    meanError.append(np.sqrt(np.mean(np.subtract(sol3[:-2],finalFlux)**2)))

fig.tight_layout()
pp = PdfPages('ClassicalESModelRandomK1Dynamic.pdf')
#pp.savefig(fig)
#pp.savefig(fig2)
fig = plt.figure(3)
plt.scatter(p,meanError)
plt.title('Root Mean Squared Error')
plt.xlabel('Percentage of Required Inflow')
plt.ylabel('Error')
fig.tight_layout()
pp.savefig(fig)
plt.show()

pp.close()