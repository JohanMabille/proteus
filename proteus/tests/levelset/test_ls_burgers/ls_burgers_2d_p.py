from proteus import *
from proteus.default_p import *
from math import *
from burgers2D import *
from proteus.mprans import NCLS
from symbol import except_clause
#import Profiling

LevelModelType = NCLS.LevelModel
logEvent = Profiling.logEvent
name = soname + "_ls"

nd = 2


class Burgers2D:

    def true_value(self, x, y, t):
        u = 0
        if y > x:
            x, y = y, x
        a = x - y
        a0 = 1 - 0.5 * t
        if a <= a0:
            if 0 <= y and y < t:
                u = y / (t + 1e-10)
            elif t <= y and y < 0.5 * t + 1 - a:
                u = 1
            else:
                u = 0
        elif a <= 1:
            if 0 <= y and y < math.sqrt(2 * t * (1 - a)):
                u = y / (t + 1e-10)
            else:
                u = 0
        else:
            u = 0

        return u

    def uOfXT(self, XY, t):

        try:
            L = len(XY[0])
            u = numpy.zeros((L,), 'd')
            for i in xrange(L):
                u[i] = self.true_value(XY[0][i], XY[0][i])

        except TypeError:  # when XY is a tuple of 3 numbers
            u = self.true_value(XY[0], XY[1], t)

        return u


analyticalSolution = {0: Burgers2D()}


class UnitSquareRotation(NCLS.Coefficients):

    def __init__(self, useHJ=False, epsFact=1.5, checkMass=False,
                 RD_model=None,
                 useMetrics=0.0, sc_uref=1.0, sc_beta=1.0):
        self.waterline_interval = -1
        self.epsFact = epsFact
        self.useHJ = useHJ
        self.RD_modelIndex = RD_model
        self.sc_uref = sc_uref
        self.sc_beta = sc_beta
        self.useMetrics = useMetrics
        mass = {0: {0: 'linear'}}
        advection = {0: {0: 'linear'}}
        diffusion = {}
        potential = {}
        reaction = {}
        if self.useHJ:
            hamiltonian = {0: {0: 'linear'}}
        else:
            hamiltonian = {}
        NCLS.Coefficients.__init__(self)
        self.checkMass = checkMass
        self.useMetrics = 0.0
        self.sc_uref = 1.0
        self.sc_beta = 1.0

    def attachModels(self, modelList):
        self.model = modelList[0]
        self.u_old_dof = numpy.copy(self.model.u[0].dof)
        self.q_v = numpy.zeros(self.model.q[('dH', 0, 0)].shape, 'd')
        self.ebqe_v = numpy.zeros(self.model.ebqe[('dH', 0, 0)].shape, 'd')

        self.q_v[:, :, 0] = self.model.q[('u', 0)]
        self.q_v[:, :, 1] = self.model.q[('u', 0)]

        self.model.q[('velocity', 0)] = self.q_v
        self.model.ebqe[('velocity', 0)] = self.ebqe_v
        if self.RD_modelIndex != None:
            # print self.RD_modelIndex,len(modelList)
            self.rdModel = modelList[self.RD_modelIndex]
        else:
            self.rdModel = self.model
        # if self.checkMass:
        #     self.m_pre = Norms.scalarSmoothedHeavisideDomainIntegral(self.epsFact,
        #                                                              self.model.mesh.elementDiametersArray,
        #                                                              self.model.q['dV'],
        #                                                              self.model.q[('m',0)],
        #                                                              self.model.mesh.nElements_owned)

        #     logEvent("Attach Models UnitSquareRotation: Phase  0 mass before NCLS step = %12.5e" % (self.m_pre,),level=2)
        #     self.totalFluxGlobal=0.0
        #     self.lsGlobalMassArray = [self.m_pre]
        #     self.lsGlobalMassErrorArray = [0.0]
        #     self.fluxArray = [0.0]
        #     self.timeArray = [self.model.timeIntegration.t]
    def preStep(self, t, firstStep=False):
        self.q_v[:, :, 0] = self.model.q[('u', 0)]
        self.q_v[:, :, 1] = self.model.q[('u', 0)]
        copyInstructions = {}
        return copyInstructions

    def postStep(self, t, firstStep=False):
        self.u_old_dof = numpy.copy(self.model.u[0].dof)
        copyInstructions = {}
        return copyInstructions

    def evaluate(self, t, c):
        pass


if applyRedistancing:
    RD_model = 1
else:
    RD_model = None
coefficients = UnitSquareRotation(useHJ=True, epsFact=epsFactHeaviside,
                                  checkMass=checkMass, RD_model=RD_model, useMetrics=useMetrics)

coefficients.variableNames = ['u']

# now define the Dirichlet boundary conditions


def getDBC(x, flag):
    pass


def zeroInflow(x):
    return lambda x, t: 0.0


dirichletConditions = {0: getDBC}


class initial_condition:
    def uOfXT(self, x, t=0):
        return (x[0] >= 0) * (x[0] <= 1) * (x[1] >= 0) * (x[1] <= 1)


initialConditions = {0: initial_condition()}

fluxBoundaryConditions = {0: 'outFlow'}


def zeroadv(x):
    return lambda x, t: 0.0


advectiveFluxBoundaryConditions = {}
#advectiveFluxBoundaryConditions =  {0:zeroadv}


diffusiveFluxBoundaryConditions = {0: {}}

# @}