# to run this script >>>from ptbTestProject import ptbTestKoresh
#>>>ptbTestKoresh.main()

from agentMET4FOF.agents import AgentMET4FOF, AgentNetwork, MonitorAgent
from ptbTestProject import testsignals
import numpy as np
#Here we define a new agent SineGeneratorAgent, and override the functions : init_parameters & agent_loop
#init_parameters() is used to setup the data stream and necessary parameters
#agent_loop() is an infinite loop, and will read from the stream continuously,
#then it sends the data to its output channel via send_output
#Each agent has internal current_state which can be used as a switch by the AgentNetwork






def next_sample_data(signalOwner):
    if signalOwner.sample<len(signalOwner.signal):
        signal_data =signalOwner.signal[signalOwner.sample] #dictionary
        signalOwner.sample=signalOwner.sample+1
    else:
        signal_data=None
    return signal_data
    


# The Generators below fed their outputs based on sample signals in testsignals, the samples are fed to the output one by one
class ShockGeneratorAgent(AgentMET4FOF):
    def init_parameters(self, num_cycles=400):
        self.sample=0
        self.signal=testsignals.shocklikeGaussian(time=np.arange(0,num_cycles,.5), t0=80, m0=1.5, sigma=15, noise=0.01)
    def agent_loop(self):
        if self.current_state == "Running":
            self.send_output(next_sample_data(self))

class RectGeneratorAgent(AgentMET4FOF):
    def init_parameters(self, num_cycles=400):
        self.sample=0
        self.signal=testsignals.rect(np.arange(0,num_cycles,.5), 10, 50, height=2, noise=0.1)
    def agent_loop(self):
        if self.current_state == "Running":
            self.send_output(next_sample_data(self))

class SineGeneratorAgent(AgentMET4FOF):
    def init_parameters(self,  num_cycles=400):
        self.sample=0
        self.signal=testsignals.sine(time=np.arange(0,num_cycles,.5), amp=1, freq=10*2** np.pi, noise=0.05)
    def agent_loop(self):
        if self.current_state == "Running":
            self.send_output(next_sample_data(self))


# To apply a filter with transfer function H(Z)=(b[0]+b[1]Z^-1+...+b[N]Z^-N)/(1+a[0]Z^-1+...+a[N]Z^-N)
# lastInput and state are to resemble delays in the transfer function new elements are added to th begining 
# the list and the last element is poped out
class iiR:
    def __init__(self,a,b):
        self.a=a
        self.b=b
        self.state = [0] * len(a)
        self.lastInputs=[0] * len(b)
    def Filter(self,newInp):
        self.lastInputs=[newInp]+self.lastInputs
        self.lastInputs.pop()
        y=np.inner(np.array(self.a),np.array(self.state))+np.inner(np.array(self.b),np.array(self.lastInputs))
        self.state=[y]+self.state
        self.state.pop()
        return y



class iiRAgent(AgentMET4FOF):
#iiRAgent uses a low pass filter with transfer function H(Z)=(0.2)/(1+0.8Z^-1)
    myIiR=iiR(a=[.8],b=[.2]) 
    def on_received_message(self, message):
        data_filter = self.myIiR.Filter(message['data'])
        self.send_output(data_filter)




def main():
    #start agent network server
    agentNetwork = AgentNetwork()
    
    #init agents by adding into the agent network
    monitor_agent = agentNetwork.add_agent(agentType= MonitorAgent)
    iiR_agent = agentNetwork.add_agent(agentType=iiRAgent)
    agentNetwork.bind_agents(iiR_agent, monitor_agent)
    iiR_agent.bind_output(monitor_agent)

    # there will be len(genTypes) generator agents with the specified type in genTypes
    # the first geerator agent (i.e., genAgents[0]) with signal type genTypes[0] will be connected to the filter 

    genTypes=[SineGeneratorAgent,RectGeneratorAgent,ShockGeneratorAgent]
    genAgents=[]
    for i in range(len(genTypes)):
        genAgents.append(agentNetwork.add_agent(agentType= genTypes[i]))
        agentNetwork.bind_agents(genAgents[i], monitor_agent)
        genAgents[i].bind_output(monitor_agent)


    agentNetwork.bind_agents(genAgents[0], iiR_agent)
    genAgents[0].bind_output(iiR_agent)
    
    

    # set all agents states to "Running"
    agentNetwork.set_running_state()

    # allow for shutting down the network after execution
    return agentNetwork


if __name__ == '__main__':
    main()

