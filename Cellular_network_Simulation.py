# -*- coding: utf-8 -*-
"""
Created on Wed May  1 01:41:20 2019

@author: asmet
"""
#Python application simulating the downlink behaviour of the two basestations covering a stretch of the road between them.
#The simulation explores effects of latency and capacity.
#Program simulates the users as they make calls, hand off between Base stations and terminate calls.
#Most of the functions defined are general and work for both the Base Station calculations based on the aurguements passed.
import numpy as np 
#Numpy used for mathematical distributions, random generation and vectorised computations


#*********************************Okumura Hata Model Fuction Defination**************************************************
#The following fuction implements Okumura Hata Model to compute the Propagation loss in a small city due to various environmental factors causing scattering, noise, destructive and constructive interferences.
#Parameters considered for Loss computation is
#   f=Frequency of the signal in Mega Hertz
#   HeightMobileUser=Height of the Mobile User in meters
#   heightbasestation=Height of the Base station in meters
#   dkm=Distance of the Mobile user from the Basestation
#We call this fuction from the main function with changing values of "dkm" distance based on which Base station the user is
#latched to and at how much distance from the base station. We are considering user is moving in a specific direction either
#towards the base station or away during its call duration
#This function is kept general and can be used for the loss calculation from both Base station1 and Base Station2 based on the "dkm" distance arguement passed.
def PropagationLoss(f,HeightMobileUser,heightbasestation,dkm):
    a=0.8-1.56*np.log10(f)+(1.1*np.log10(f)-0.7)*HeightMobileUser
    loss=69.55+26.16*np.log10(f)-13.82*np.log10(heightbasestation)+(44.9-6.55*np.log10(heightbasestation))*np.log10(dkm)-a
    return(loss)


#Fuction to determine new location of the user as user is moving with a speed defined by variable "speed". The direction of motion is either away from the BS or towards the BS
#The fuction is called with an arguement. The arguement value is the previous location of the user
#The previous location means the distance of the user from the Base Station in the previous second
#The value distance is in kilometers
#   dis=distance tranvelled by the user in 1sec with the given speed
#the function returns the current location of the user.
#This function is kept general and can be used for the distance calculation from both Base station1 and Base Station2 based on the distance arguement passed.
def new_distance(distance):#distance in Kilometers
    currentdistance=distance*1000-dis #in Meters
    return(currentdistance/1000)# in Kms


#Function generates an array of tuple values where first value of each tuple is the "distance from the BaseStation" and
#the second value gives the Shadowing loss at the distance.
#Two 2-Dimensional arrays are created for shadowing values for both Base Stations
def shadowing(roadlength):#roadlength is the distance between two base stations on the road
    mean=0
    sigma=2
    size=int(roadlength*1000/SHAD_RES)
    shadowbs=np.random.normal(mean,sigma,size)
    shadowing_values=[]
    m=10
    for i in shadowbs:
        shadowing_values.append((m,i))
        m=m+10
    return(shadowing_values)
    
#Function is used to compute the exact shadowing loss at the location of the user respective to the Base Station
#This loss is added while computing for the Recieved Signal Strength at the location of the user.
# distance = distance of the user from the base station in meters
# shadowBS, the shadowing array generated using the previous function for the specific Base Station is pass into it.
def shadowing_loss(distance,shadowBS):
    svalue=0#initialized/intermediate shadowing loss value
    for i in shadowBS:
        if distance<i[0]:
            break
        svalue=i[1]
    return(svalue)   
    
#Function used to compute the rayleigh fading value at the location of the user.
#Random Normal distribution is used to generate an array of rayleigh fading values. 
#The function returns the second deepest fade value which is considered for the RSL computation
def rayleighfading():
    mean=0
    variance=1
    std=np.sqrt(variance)
    #Two numpy arrays with gaussian random values
    size=10
    x=np.random.normal(mean,std,size)#real part
    y=np.random.normal(mean,std,size)#imaginary part
    #Complex distribution
    z=x+y*(1j)
    #absolute value of the complex number. All are vectorised computations
    zmag=np.abs(z)
    zg=-np.sort(-zmag)
    fading_value=20*np.log10(zg[1])
    return(fading_value)



#Function is used to allocate the available channels on the base station to the active users based on the availability.
#This function keeps track of call attempts, active calls, channels used, calls blocked 
#due to capacity, successfull call connections and calls which are picked by the 
#other Base Station when available channels are exhausted on one base station.
def channel_check(channel,RSLbs1,RSLbs2,activeuser):
    if channel["basestation"]==1:
        channel["bs1"]["Call Attempts"]=channel["bs1"]["Call Attempts"]+1
        if channel["bs1"]["Active Calls"]< channel["bs1"]["Available channels"]:
            channel["bs1"]["Active Calls"]=channel["bs1"]["Active Calls"]+1
            channel["bs1"]["Available channels"]=channel["bs1"]["Available channels"]-1
            channel["bs1"]["Successful call connections"]=channel["bs1"]["Successful call connections"]+1
            channels[0]=channel
            return(1)#BS1 took the call
        else:#active call equal to Available channels
            channel["bs1"]["Blocked Calls Capacity"]=channel["bs1"]["Blocked Calls Capacity"]+1
            blocked_user_capacity_bs1.append(activeuser)
            channels[0]=channel
            if RSLbs2>=Rx_threshold:
                if channels[1]["bs2"]["Active Calls"]< channels[1]["bs2"]["Available channels"]:
                    channels[1]["bs2"]["Active Calls"]=channels[1]["bs2"]["Active Calls"]+1
                    channels[1]["bs2"]["Available channels"]=channels[1]["bs2"]["Available channels"]-1
                    channels[1]["bs2"]["Successful connections of calls Picked up from other BS"]=channels[1]["bs2"]["Successful connections of calls Picked up from other BS"]+1
                    channels[1]["bs2"]["Other BS Calls Picked up"]=channels[1]["bs2"]["Other BS Calls Picked up"]+1
                    return("bs2 used")#BS2 took the call and call blocked for BS1
                else:#bs2 no free channels
                    channel["bs1"]["Dropped Calls"]=channel["bs1"]["Dropped Calls"]+1
                    channel["bs1"]["Dropped Calls no free channels on both BS"]=channel["bs1"]["Dropped Calls no free channels on both BS"]+1

                    dropped_users_bs1.append(activeuser)
                    channels[0]=channel
                    print("dropped as no free channels on bs2", activeuser)
                    return("dropped")#call dropped and blocked
            else:#bs2 power is less than threshold
                channel["bs1"]["Dropped Calls"]=channel["bs1"]["Dropped Calls"]+1
                channel["bs1"]["Dropped Calls Other Base Station Power below Thres."]=channel["bs1"]["Dropped Calls Other Base Station Power below Thres."]+1
                dropped_users_bs1.append(activeuser)
                channels[0]=channel
                print("dropped as power on bs2 not above threshold", activeuser)
                return("dropped")#call dropped and blocked
    elif channel["basestation"]==2:
        channel["bs2"]["Call Attempts"]=channel["bs2"]["Call Attempts"]+1
        if channel["bs2"]["Active Calls"]< channel["bs2"]["Available channels"]:
            channel["bs2"]["Active Calls"]=channel["bs2"]["Active Calls"]+1
            channel["bs2"]["Available channels"]=channel["bs2"]["Available channels"]-1
            channel["bs2"]["Successful call connections"]=channel["bs2"]["Successful call connections"]+1
            print("channel check", activeuser)
            channels[1]=channel
            return(2)#BS1 took the call
        else:
            channel["bs2"]["Blocked Calls Capacity"]=channel["bs2"]["Blocked Calls Capacity"]+1
            blocked_user_capacity_bs2.append(activeuser)
            channels[1]=channel
            if RSLbs1>=Rx_threshold:
                if channels[0]["bs1"]["Active Calls"]< channels[0]["bs1"]["Available channels"]:
                    channels[0]["bs1"]["Active Calls"]=channels[0]["bs1"]["Active Calls"]+1
                    channels[0]["bs1"]["Available channels"]=channels[0]["bs1"]["Available channels"]-1
                    channels[0]["bs1"]["Successful connections of calls Picked up from other BS"]=channels[0]["bs1"]["Successful connections of calls Picked up from other BS"]+1
                    channels[0]["bs1"]["Other BS Calls Picked up"]=channels[0]["bs1"]["Other BS Calls Picked up"]+1#Call Attempts are only for its own Basestation calls
                    return("bs1 used")#BS1 took the call and call blocked for BS2
                else:#bs1 no free channels
                    channel["bs2"]["Dropped Calls"]=channel["bs2"]["Dropped Calls"]+1
                    channel["bs2"]["Dropped Calls no free channels on both BS"]=channel["bs2"]["Dropped Calls no free channels on both BS"]+1
                    dropped_users_bs2.append(activeuser)
                    channels[1]=channel
                    print("dropped as channels on bs1 not available", activeuser)
                    return("dropped")#call dropped and blocked
            else:#bs1 power is less than threshold
                channel["bs2"]["Dropped Calls"]=channel["bs2"]["Dropped Calls"]+1
                channel["bs2"]["Dropped Calls Other Base Station Power below Thres."]=channel["bs2"]["Dropped Calls Other Base Station Power below Thres."]+1
                dropped_users_bs2.append(activeuser)
                channels[1]=channel
                print("dropped as power on bs1 not above threshold", activeuser)
                return("dropped")#call dropped and blocked


#Function is used to identify which user does the call from the pool of inactive users.
#If some users are already on the call from the previous second, then in the current second
#such users are saved as old users and the new user which can start a call this second is
#selected from the remaining pool of inactive users
def define_user(user,oldusers,simulationtime):
    if len(oldusers)==0:
        print("no old users found")
    else:
        for u in oldusers:#u is an iterator and u is used to identify already active users from the previous second
            if user.count(u)!=0:# this is done to modify the total users list, the user who is already on call wont initiate another call again
                user.remove(u)
    for i in user:
        probability=np.random.random_sample()# a random probability value is generated
        if probability<=prob:#"Prob" is the probability of the user to do a call in one second calculated using call rate parameter
            #If the random probability is less than the given user probability to call then user is made active on a call.
            #Active user is given the following parameters, 
            #distance from the bases stations 1 and 2
            #the call duration the user is expected to continue on call
            #the direction of motion of the user during the call, its moving away from which BS and its moving towards which BS.
            distancefrombs1=np.random.rand()*roadlength+0
            distancefrombs2=roadlength-distancefrombs1
            call_duration=np.random.exponential(5)#############################Call time changed
            call_timer_counter=0
            #Below code to identify the direction of motion of the active user
            #Determine Users Direction using moving West as moving towards Base Station1 and moving East as moving towards Base Station 2
            if distancefrombs1>=roadlength/2:#If user is far from BS1 in the far half of the road, then User comes towards the BS1
                MotionDirection="West"#towards BS1
            else:
                MotionDirection="East"#towards BS2#If user is near to BS1 in the near half of the road, then User moves away towards the BS2
            #Defining user with the mandatory parameters describing each active user on the road. Each parameter changes and takes new values as the simulation builds up
            user={"user":i,"distancefrombs1":distancefrombs1,"distancefrombs2":distancefrombs2,"call_duration":call_duration,"call_timer_counter":call_timer_counter,"MotionDirection":MotionDirection, "Hand Off Status":0, "Serving Base Station":"bs", "HO_TIMER":3, "Hand Off Ongoing":0,"Latest Call Initiation Time":simulationtime}
            #Active user = List of all the users active on call currently, describing most of the User detail parameters. The user details are saved as dictionary key value pairs for easy accessibility when needed.
            Active_User.append(user)
    return(Active_User)
        
#Function is used to implement handoffs of the users to other base station based on conditions like:
#Recieved signal strength from the other base station is stronger
#Function keeps track of the HO_TIMER, the handover time and iterates through it and keeps
#the user active on both the base stations during the handover time
#The function keeps logs of the handover attempts, calls and failures.
def hand_off(bs,ho_timer,channel,user):
    if user["user"] in old_handoff_users:#if user is already in the handoff process, waiting for the HO_timer to expire
        if ho_timer==0:
            if bs=="bs1":
                channels[0]["bs1"]["Active Calls"]=channels[0]["bs1"]["Active Calls"]-1
                channels[0]["bs1"]["Available channels"]=channels[0]["bs1"]["Available channels"]+1
                handoff[0]["bs1 to bs2"]["Successful Handoffs"]=handoff[0]["bs1 to bs2"]["Successful Handoffs"]+1
                return("completed handover to bs2")
            elif bs=="bs2":
                channels[1]["bs2"]["Active Calls"]=channels[1]["bs2"]["Active Calls"]-1
                channels[1]["bs2"]["Available channels"]=channels[1]["bs2"]["Available channels"]+1
                handoff[1]["bs2 to bs1"]["Successful Handoffs"]=handoff[1]["bs2 to bs1"]["Successful Handoffs"]+1
                return("completed handover to bs1")
        else:
            print("check if power and channel is still available is sufficient")
            return("HO ongoing")
    else:
        if bs=="bs1":#bs1 handoff to bs2
            handoff[0]["bs1 to bs2"]["Handoff Attempts"]=handoff[0]["bs1 to bs2"]["Handoff Attempts"]+1
            if channel["bs2"]["Active Calls"]< channel["bs2"]["Available channels"]:
                channel["bs2"]["Active Calls"]=channel["bs2"]["Active Calls"]+1
                channel["bs2"]["Available channels"]=channel["bs2"]["Available channels"]-1
                channel["bs2"]["Handover Calls"]=channel["bs2"]["Handover Calls"]+1
                channels[1]=channel
                #Populating already handoff user list
                if user["user"] in old_handoff_users:
                    print("already present")
                else:
                    old_handoff_users.append(user["user"])#old handoff users list
                return("started handoff to bs2")
            else:
                handoff[0]["bs1 to bs2"]["Handoff Failures"]=handoff[0]["bs1 to bs2"]["Handoff Failures"]+1
                handoff[0]["bs1 to bs2"]["Handoff Failures due to no free channels"]=handoff[0]["bs1 to bs2"]["Handoff Failures due to no free channels"]+1
                channel["bs2"]["Blocked Calls Capacity"]=channel["bs2"]["Blocked Calls Capacity"]+1
                #The handoff failure is recorded as the blocked call due to unavailable capacity on BS2 and it is marked as the handoff failure
        elif bs=="bs2":
            handoff[1]["bs2 to bs1"]["Handoff Attempts"]=handoff[1]["bs2 to bs1"]["Handoff Attempts"]+1
            if channel["bs1"]["Active Calls"]< channel["bs1"]["Available channels"]:
                channel["bs1"]["Active Calls"]=channel["bs1"]["Active Calls"]+1
                channel["bs1"]["Available channels"]=channel["bs1"]["Available channels"]-1
                channel["bs1"]["Handover Calls"]=channel["bs1"]["Handover Calls"]+1
                channels[0]=channel
                #Populating already handoff user list
                if user["user"] in old_handoff_users:
                    print("already present")
                else:
                    old_handoff_users.append(user["user"])#old handoff users list
                return("started handoff to bs1")
            else:
                handoff[1]["bs2 to bs1"]["Handoff Failures"]=handoff[1]["bs2 to bs1"]["Handoff Failures"]+1
                handoff[1]["bs2 to bs1"]["Handoff Failures due to no free channels"]=handoff[1]["bs2 to bs1"]["Handoff Failures due to no free channels"]+1
                channel["bs1"]["Blocked Calls Capacity"]=channel["bs1"]["Blocked Calls Capacity"]+1
                #The handoff failure is recorded as the blocked call due to unavailable capacity on BS1 and it is marked as the handoff failure
            
            
#Fuction used to compute the Recieved Signal Strength from both the Base Stations BS1 and BS2
#at the location of the user
#distance = distance of the user from the base station
#BaseStation = Base station whose RSL needs to be computed at the location of the user
def RSL_Computation(distance,BaseStation):
    #Propagation loss computation
    PathLoss=PropagationLoss(f,HeightMobileUser,heightbasestation,distance)
    #Shadowing Computation
    shadowdistance=int((distance*1000))
    #distance from basestation for shadowing computation, shadowdistance)
    if BaseStation==1:
        shadowloss=shadowing_loss(shadowdistance,shadowbs1)
    else:
        print("Shadowing for BS2")
        shadowloss=shadowing_loss(shadowdistance,shadowbs2)
    #Rayleigh fading computation
    #Rayleigh Fading loss computated each time an active user is analyzed
    rayleigh=rayleighfading()
    #Received Signal Power Computation
    RSLbasestation=EIRP-PathLoss-shadowloss-rayleigh
    #"this RSL is", RSLbasestation)
    return(RSLbasestation)
    

#******************************simulation parameters********************************######################
users=int(input("Enter number of users "))
user=list(range(users))#list of all active and non-active users on the road
roadlength=int(input("Enter length of the road, distance between two Base Stations in Kilo meters ")) #in Kms
t_delta=1 #in seconds, Delta Time is 1 Sec. We are observing user behaviour each delta time means each second
call_rate=1 #in call per hour, call rate is given as user does 1 call per hour
lamda=call_rate/3600 #rate in calls per sec 
prob=lamda*t_delta#probability of each user to make a call


#***********************************simulation time***************************################################
#s_time = is the simulation time of the model in seconds. How long the simulation runs
time=int(input("Enter simulation time of the model in hours "))
s_time=time*3600#in seconds


#***************************Basestation Parameters*****************************########################
heightbasestation=50 #in meters basestation height
EIRP= 55 #in DBm 
channels=30 #Total available channels on each base station
f=1000 #Frequency of the signal in Mega Hertz

#************************user properties***************************************#########################
HeightMobileUser=1.7 #mobile Height in meters
Rx_threshold=-102 #in DBm, Threshold/min power required by the user to be latched to the base station
avgcall_duration=3 #Given that call duration of the user will be on an average 3 mins
H=3*60 #call duration in seconds
speed=int(input("Enter Mobile user speed of moving in meter/sec "))
HO_TIMER=3# handover time is given as 3 seconds

#********************shadowing resolution*******************************************#############
SHAD_RES=10 #in meters, It means new shadowing value is computed each 10 meters
#Distance travelled with given speed in delta time period
dis=speed*t_delta #in meters
#Note direction parameters "West" is towards BaseStation1 and "East" is towards BaseStation2#################################

#Shadowing values over the road every 10m from both BaseStation1 and BaseStation2#####################################
shadowbs1=shadowing(roadlength)
#"shadowbs1",for Base station1
shadowbs2=shadowing(roadlength)
#"shadowbs2",for Base Station2)
#************************Channels, Base station and Other User Details****************************
#A combination of list and list of dictionaries are used to make data readily available for analysis
#Channel and other statistics of both the BaseStations
channels=[{"basestation":1, "bs1":{"Available channels":10,"Active Calls":0,"Blocked Calls Power":0,"Blocked Calls Capacity":0,"Dropped Calls":0, "Successful call connections":0, "Call Attempts":0, "Successfully Completed Calls":0, "Handover Calls":0,"Other BS Calls Picked up":0, "Successful connections of calls Picked up from other BS":0,"Dropped Calls no free channels on both BS":0,"Dropped Calls Other Base Station Power below Thres.":0, "Dropped Active Call due to Low RSL now":0, "Dropped New User RSL below Thres":0 }},{"basestation":2, "bs2":{"Available channels":10,"Active Calls":0,"Blocked Calls Power":0,"Blocked Calls Capacity":0,"Dropped Calls":0, "Successful call connections":0, "Call Attempts":0, "Successfully Completed Calls":0, "Handover Calls":0, "Other BS Calls Picked up":0, "Successful connections of calls Picked up from other BS":0, "Dropped Calls no free channels on both BS":0,"Dropped Calls Other Base Station Power below Thres.":0, "Dropped Active Call due to Low RSL now":0, "Dropped New User RSL below Thres":0}}]
#Handoff Statistics of both the BaseStations
handoff=[{"basestation":1, "bs1 to bs2":{"Handoff Attempts":0, "Handoff Failures":0, "Successful Handoffs":0, "HO_TIMER":3,"Handoff Failures due to no free channels":0,"handoff fails distance too close":0,"handoff fails call timer over":0,"handoff fails bs1 power below threshold":0}},{"basestation":2, "bs2 to bs1":{"Handoff Attempts":0, "Handoff Failures":0, "Successful Handoffs":0, "HO_TIMER":3,"Handoff Failures due to no free channels":0,"handoff fails distance too close":0,"handoff fails call timer over":0,"handoff fails bs2 power below threshold":0}}]
#Distance of a user from BaseStation1
distancefrombs1=0
#Distance of a user from BaseStation2
distancefrombs2=0


#User Data of all the users active on a call currently
Active_User=[]
#User Data of all the users who were active on a call the previous second
old_users=[]
#All the data regarding the active calls ongoing currently
active_call_list=[]
#All the data of the previously completed and non-completed calls
archive_call_list=[]
#The users who have handover ongoing with the other base stations.
old_handoff_users=[]
#The Users who have handed off to the other base station successfully
handoffuser=[]
#The users who were blocked due to insufficient recieved signal strength from the BS1
blocked_user_power_bs1=[]
#The users who were blocked due to insufficient recieved signal strength from the BS2
blocked_user_power_bs2=[]
#Call completing when the user gets within 1meter distance of the base station(we consider user handed over to the different sector so we mark the call as successfully completing)
#For Base Station1
successfullcalls_bs1=[]
#Call completing when the user gets within 1meter distance of the base station(we consider user handed over to the different sector so we mark the call as successfully completing)
#for Base station2
successfullcalls_bs2=[]
#Users Blocked from BS1 due to no free available channels
blocked_user_capacity_bs1=[]
#Users Blocked from BS2 due to no free available channels
blocked_user_capacity_bs2=[]
#Users dropped by the base station due to insufficient power or unavailable channels. 
#BS drops only if the user cant be picked up from the other Base station
#Dropped users for bs1
dropped_users_bs1=[]
#Dropped users for bs2
dropped_users_bs2=[]
power1=[]
power2=[]



# **************************************MAIN PROGRAM*******************************************

np.random.seed(1223)  #seeding the random generator 
for simulationtime in range(s_time):#iterating model secondwise to buildup the simulation
    #every second in time it is running
    #Previous active users are, Active_User)
    print("ENTS656", simulationtime)
    print(s_time)
    
    for y in Active_User:#y is just an iterating variable which takes values from list Active User
        if y["user"] in old_users:
            print("user is already present in the old user list")
        else:
            old_users.append(y["user"])#Updating old user list with the active users in the previous call
    #"old user list is updated"
    print("\ndefining new user for the current second now")
    define_user(user,old_users,simulationtime)
    
#*******************************************************************************
    
    for i in Active_User:#iterating over each active user, i takes the value from Active User List. I is each active user
        print(i["user"])
        if i["user"] in old_users:
            print("old user dealing with",i["user"])
            print("Reading users now, from start! so old user first")
            if i["call_timer_counter"]<i["call_duration"]:#Call timer checked, how long user have been on call
                i["call_timer_counter"]=i["call_timer_counter"]+1
                if i["MotionDirection"]=="East":#towards bs2
                    #New location calculation of the user on the road wrt both the Basestations
                    distancefrombs2=new_distance(i["distancefrombs2"])
                    distancefrombs1=12-distancefrombs2
                else:
                    distancefrombs1=new_distance(i["distancefrombs1"])
                    print("distancefrombs1",distancefrombs1)
                    distancefrombs2=12-distancefrombs1
                i["distancefrombs1"]=distancefrombs1
                i["distancefrombs2"]=distancefrombs2
                
#*****************************when active user is WITHIN 1METERS from BS1###################
                if (distancefrombs1>=0.001):
                    print("BS1")
                    RSLbs1=RSL_Computation(distancefrombs1,1)# 1 for base station1
                else:##if distance is less than 1 m from the basestation
                    if i["Serving Base Station"]=="bs1":
                        channels[0]["bs1"]["Successfully Completed Calls"]=channels[0]["bs1"]["Successfully Completed Calls"]+1
                        channels[0]["bs1"]["Available channels"]=channels[0]["bs1"]["Available channels"]+1
                        channels[0]["bs1"]["Active Calls"]=channels[0]["bs1"]["Active Calls"]-1
                        if i["Hand Off Ongoing"]==1:
                            print("handoff fails distance too close")
                            handoff[0]["bs1 to bs2"]["handoff fails distance too close"]=handoff[0]["bs1 to bs2"]["handoff fails distance too close"]+1
                            handoff[0]["bs1 to bs2"]["Handoff Failures"]=handoff[0]["bs1 to bs2"]["Handoff Failures"]+1
                        else:
                            print("normal user call completing as user came within 1m from the base station")
                    elif i["Serving Base Station"]=="bs2":
                        channels[1]["bs2"]["Successfully Completed Calls"]=channels[1]["bs2"]["Successfully Completed Calls"]+1
                        channels[1]["bs2"]["Available channels"]=channels[1]["bs2"]["Available channels"]+1
                        channels[1]["bs2"]["Active Calls"]=channels[1]["bs2"]["Active Calls"]-1 
                        if i["Hand Off Ongoing"]==1:
                            print("handoff fails distance too close")
                            handoff[1]["bs2 to bs1"]["handoff fails distance too close"]=handoff[1]["bs2 to bs1"]["handoff fails distance too close"]+1
                            handoff[1]["bs2 to bs1"]["Handoff Failures"]=handoff[1]["bs2 to bs1"]["Handoff Failures"]+1
                        else:
                            print("normal user call completing")
                    old_users.remove(i["user"])
                    archive_call_list.append(i)#The call is completed and archive call is updated
                    Active_User.remove(i)#User is no more on active user list
                    break
                
#*****************************when active user is WITHIN 1METERS from BS2 ###################
                if (distancefrombs2>=0.001):
                    print("BS2")
                    RSLbs2=RSL_Computation(distancefrombs2,2)# 2 for base station2
                    print("recalculated RSLs user",i, RSLbs1,RSLbs2)
                else:##if distance is less than 1 m from the basestation
                    print("user is handed over to the different sector, not considered in the simulation model")
                    if i["Serving Base Station"]=="bs1":
                        channels[0]["bs1"]["Successfully Completed Calls"]=channels[0]["bs1"]["Successfully Completed Calls"]+1
                        channels[0]["bs1"]["Available channels"]=channels[0]["bs1"]["Available channels"]+1
                        channels[0]["bs1"]["Active Calls"]=channels[0]["bs1"]["Active Calls"]-1
                        if i["Hand Off Ongoing"]==1:
                            print("handoff fails distance too close")
                            handoff[0]["bs1 to bs2"]["handoff fails distance too close"]=handoff[0]["bs1 to bs2"]["handoff fails distance too close"]+1
                            handoff[0]["bs1 to bs2"]["Handoff Failures"]=handoff[0]["bs1 to bs2"]["Handoff Failures"]+1
                        else:
                            print("normal user call completing")
                    elif i["Serving Base Station"]=="bs2":
                        channels[1]["bs2"]["Successfully Completed Calls"]=channels[1]["bs2"]["Successfully Completed Calls"]+1
                        channels[1]["bs2"]["Available channels"]=channels[1]["bs2"]["Available channels"]+1
                        channels[1]["bs2"]["Active Calls"]=channels[1]["bs2"]["Active Calls"]-1
                        if i["Hand Off Ongoing"]==1:
                            print("handoff fails distance too close")
                            handoff[1]["bs2 to bs1"]["handoff fails distance too close"]=handoff[1]["bs2 to bs1"]["handoff fails distance too close"]+1
                            handoff[1]["bs2 to bs1"]["Handoff Failures"]=handoff[1]["bs2 to bs1"]["Handoff Failures"]+1
                        else:
                            print("normal user call completing")
                    old_users.remove(i["user"])
                    archive_call_list.append(i)
                    Active_User.remove(i)
                    break

#************************** CHANNEL ALLOCATION BASED ON RSL and HANDOVER      ################
                print("\nRSL, Channel Allocation and hand over computation ahead:-")
                if i["Serving Base Station"]=="bs1":
                    if RSLbs1<Rx_threshold:#########################Not enough power from Serving Basestation to proceed with Handoff. Call drops
                        channels[0]["bs1"]["Dropped Calls"]=channels[0]["bs1"]["Dropped Calls"]+1
                        channels[0]["bs1"]["Dropped Active Call due to Low RSL now"]=channels[0]["bs1"]["Dropped Active Call due to Low RSL now"]+1
                        channels[0]["bs1"]["Available channels"]=channels[0]["bs1"]["Available channels"]+1
                        channels[0]["bs1"]["Active Calls"]=channels[0]["bs1"]["Active Calls"]-1
                        if i["Hand Off Ongoing"]==1:
                            print("handoff fails bs1 power below threshold")
                            handoff[0]["bs1 to bs2"]["handoff fails bs1 power below threshold"]=handoff[0]["bs1 to bs2"]["handoff fails bs1 power below threshold"]+1
                            handoff[0]["bs1 to bs2"]["Handoff Failures"]=handoff[0]["bs1 to bs2"]["Handoff Failures"]+1
                        else:
                            print("normal user call dropping")
                        old_users.remove(i["user"])
                        dropped_users_bs1.append([i,"Rsl less"])
                        archive_call_list.append(i)
                        Active_User.remove(i)
                        
#********************************HAND OFF Scenerio*********************************
                    elif RSLbs2>RSLbs1 and RSLbs1>=Rx_threshold:##### RSL 1 is good enough >= Threshold, RSL2 is larger, Possible handover situation, power from other basestation is more 
                        print("Potential handoff is triggered")
                        if i["user"] in old_handoff_users:
                            print("user already in handoff")
                            ho_timer=i["HO_TIMER"]
                            if ho_timer==0:
                                print(ho_timer)
                                status=hand_off("bs1",ho_timer,channels[1],i)
                                if status=="completed handover to bs2":#user successfully handed off to the other base station
                                    if i["HO_TIMER"]==0:
                                        i["Hand Off Status"]=1
                                        i["Serving Base Station"]="bs2"
                                        i["Hand Off Ongoing"]=0
                                        i["HO_TIMER"]=3
                                        old_handoff_users.remove(i["user"])
                                        active_call_list.append(i)
                                        handoffuser.append(i)
                            else:
                                i["HO_TIMER"]=i["HO_TIMER"]-1#Handover timer decremented as handoff is ongoing
                                print("timer decremented")    
                        else:
                            ho_timer=i["HO_TIMER"]
                            status=hand_off("bs1",ho_timer,channels[1],i)#ho_timer sent 3
                            if status=="started handoff to bs2":#user just initiated the handoff to the other base station. HO timer counting for next 3 seconds
                                print("\nstarted hand off, timer active")
                                i["HO_TIMER"]=i["HO_TIMER"]-1
                                i["Hand Off Ongoing"]=1
                                old_handoff_users.append(i["user"])
                                handoffuser.append((i,simulationtime))
                                active_call_list.append(i)
                    elif RSLbs2<=RSLbs1 and RSLbs1>=Rx_threshold:#HO timer keeps running and user occupies two channels both on BS1 and BS2 during handover
                        #RSL from BS2 is not larger than RSL from BS1
                        if i["user"] in old_handoff_users:
                            print("user already in handoff")
                            ho_timer=i["HO_TIMER"]
                            if ho_timer==0:
                                print(ho_timer)
                                status=hand_off("bs1",ho_timer,channels[1],i)
                                if status=="completed handover to bs2":
                                    if i["HO_TIMER"]==0:
                                        i["Hand Off Status"]=1
                                        i["Serving Base Station"]="bs2"
                                        i["Hand Off Ongoing"]=0
                                        i["HO_TIMER"]=3
                                        active_call_list.append(i)
                                        handoffuser.append(i)
                            else:
                                i["HO_TIMER"]=i["HO_TIMER"]-1
                                print("timer decremented")
                        else:
                            print("BS1 continues the call handoff not initiated. it has enough power")
                        #HO to bs1 pending 
                elif i["Serving Base Station"]=="bs2":
                    #Below same events of handover happening if the user is currently latched to base station2
                    if RSLbs2<Rx_threshold:#########################Not enough power from Serving Basestation to proceed with Handoff. Call drops
                        channels[1]["bs2"]["Dropped Calls"]=channels[1]["bs2"]["Dropped Calls"]+1
                        channels[1]["bs2"]["Dropped Active Call due to Low RSL now"]=channels[1]["bs2"]["Dropped Active Call due to Low RSL now"]+1
                        channels[1]["bs2"]["Available channels"]=channels[1]["bs2"]["Available channels"]+1
                        channels[1]["bs2"]["Active Calls"]=channels[1]["bs2"]["Active Calls"]-1
                        if i["Hand Off Ongoing"]==1:
                            print("handoff fails bs2 power below threshold")
                            handoff[1]["bs2 to bs1"]["handoff fails bs2 power below threshold"]=handoff[1]["bs2 to bs1"]["handoff fails bs2 power below threshold"]+1
                            handoff[1]["bs2 to bs1"]["Handoff Failures"]=handoff[1]["bs2 to bs1"]["Handoff Failures"]+1
                        else:
                            print("normal user call dropping")
                        old_users.remove(i["user"])
                        dropped_users_bs2.append([i,"RSL less"])
                        archive_call_list.append(i)
                        Active_User.remove(i)
                        ####################################
                    elif RSLbs1>RSLbs2 and RSLbs2>=Rx_threshold:####################### RSL 2 is good enough >= Threshold, RSL1 is larger, Possible handover situation, power from other basestation is more 
                        print("Potential handoff is triggered")
                        if i["user"] in old_handoff_users:
                            print("user already in handoff")
                            ho_timer=i["HO_TIMER"]
                            if ho_timer==0:
                                print(ho_timer)
                                status=hand_off("bs2",ho_timer,channels[0],i)
                                if status=="completed handover to bs1":#Successful handover happens to bs1
                                    if i["HO_TIMER"]==0:
                                        i["Hand Off Status"]=1
                                        i["Serving Base Station"]="bs1"
                                        i["Hand Off Ongoing"]=0
                                        i["HO_TIMER"]=3
                                        old_handoff_users.remove(i["user"])
                                        active_call_list.append(i)
                                        handoffuser.append(i)
                            else:
                                i["HO_TIMER"]=i["HO_TIMER"]-1
                                print("timer decremented")
                        else:
                            ho_timer=i["HO_TIMER"]
                            status=hand_off("bs2",ho_timer,channels[0],i)#ho_timer sent 3
                            if status=="started handoff to bs1":#Handover started to bs1
                                print("\nstarted hand off, timer active")
                                i["HO_TIMER"]=i["HO_TIMER"]-1
                                i["Hand Off Ongoing"]=1
                                old_handoff_users.append(i["user"])
                                handoffuser.append((i,simulationtime))
                                active_call_list.append(i)
                    elif RSLbs1<=RSLbs2 and RSLbs2>=Rx_threshold:
                        if i["user"] in old_handoff_users:
                            print("user already in handoff")
                            ho_timer=i["HO_TIMER"]
                            if ho_timer==0:
                                print(ho_timer)
                                status=hand_off("bs2",ho_timer,channels[0],i)
                                if status=="completed handover to bs1":
                                    if i["HO_TIMER"]==0:
                                        i["Hand Off Status"]=1
                                        i["Serving Base Station"]="bs1"
                                        i["Hand Off Ongoing"]=0
                                        i["HO_TIMER"]=3
                                        active_call_list.append(i)
                                        handoffuser.append(i)
                            else:
                                i["HO_TIMER"]=i["HO_TIMER"]-1
                                print("timer decremented")
                        else:
                            print("BS2 continues the call handoff not initiated. it has enough power")
                ########################################################################################
            else:##Call Timer Expires now, call completed successfully
                print("call should terminate now, last minute of the call. Call Completed Successfully")
                if i["Serving Base Station"]=="bs1":
                    channels[0]["bs1"]["Successfully Completed Calls"]=channels[0]["bs1"]["Successfully Completed Calls"]+1
                    channels[0]["bs1"]["Available channels"]=channels[0]["bs1"]["Available channels"]+1
                    channels[0]["bs1"]["Active Calls"]=channels[0]["bs1"]["Active Calls"]-1
                    successfullcalls_bs1.append(i)# completed calls
                    if i["Hand Off Ongoing"]==1:
                        print("handoff fails call time over")
                        handoff[0]["bs1 to bs2"]["handoff fails call timer over"]=handoff[0]["bs1 to bs2"]["handoff fails call timer over"]+1
                        handoff[0]["bs1 to bs2"]["Handoff Failures"]=handoff[0]["bs1 to bs2"]["Handoff Failures"]+1
                    else:
                        print("normal user call completing")
                    
                elif i["Serving Base Station"]=="bs2":
                    channels[1]["bs2"]["Successfully Completed Calls"]=channels[1]["bs2"]["Successfully Completed Calls"]+1
                    channels[1]["bs2"]["Available channels"]=channels[1]["bs2"]["Available channels"]+1
                    channels[1]["bs2"]["Active Calls"]=channels[1]["bs2"]["Active Calls"]-1
                    successfullcalls_bs2.append(i)
                    if i["Hand Off Ongoing"]==1:
                        print("handoff fails call timer over")
                        handoff[1]["bs2 to bs1"]["handoff fails call timer over"]=handoff[1]["bs2 to bs1"]["handoff fails call timer over"]+1
                        handoff[1]["bs2 to bs1"]["Handoff Failures"]=handoff[1]["bs2 to bs1"]["Handoff Failures"]+1
                    else:
                        print("normal user call completing")
                old_users.remove(i["user"])
                archive_call_list.append(i)
                Active_User.remove(i)
                
############################################################################################################
        else: #Newly active users who attempted a call this second, their power computation and channel allocation of their call
            print("\nNew User RSL computation started, user details below:", i["user"],i["distancefrombs1"],i["distancefrombs2"])
            distancebs1=i["distancefrombs1"]
            distancebs2=i["distancefrombs2"]
        ##power computation
            if (distancebs1>=0):
                print("BS1")
                RSLbs1=RSL_Computation(distancebs1,1)# 1 for base station1
            else:
                print("user is handed over to the different sector, not considered in the simulation model")
            if (distancebs2>=0):
                print("BS2")
                RSLbs2=RSL_Computation(distancebs2,2)# 2 for base station2
            else:
                print("user is handed over to the different sector, not considered in the simulation model")
        ################################################################################################################
            print("Checking Channels Allocation for the New User based on the computed RSLs")
            if RSLbs1>RSLbs2:
                print("RSLbs1 is greater")
                if RSLbs1>=Rx_threshold:
                    #check available channel for bs1, channels[0] passed. channels 0 is all data about BS1
                    status=channel_check(channels[0],RSLbs1,RSLbs2,i)
                    if status==1:
                        print("status", status) 
                        print("\nafter call connection up all channels", channels)
                        i["Serving Base Station"]="bs1"
                        old_users.append(i["user"])
                        i["call_timer_counter"]=i["call_timer_counter"]+1
                        #call time left comupted based on call_timer_counter. Value keeps on adding untill greater or equal to call_duration of the user             
                        active_call_list.append(i)
                    elif status=="bs2 used":
                        i["Serving Base Station"]="bs2"
                        i["call_timer_counter"]=i["call_timer_counter"]+1
                        old_users.append(i["user"])
                        active_call_list.append(i)
                        print("call successful on BS2")
                    elif status=="dropped":
                        dropped_users_bs1.append(i)
                        archive_call_list.append(i)
                        Active_User.remove(i)
                else:
                    print("call is blocked due to power")
                    value=channels[0]["bs1"]["Blocked Calls Power"]
                    channels[0]["bs1"]["Blocked Calls Power"]=value+1
                    channels[0]["bs1"]["Dropped Calls"]=channels[0]["bs1"]["Dropped Calls"]+1
                    channels[0]["bs1"]["Dropped New User RSL below Thres"]=channels[0]["bs1"]["Dropped New User RSL below Thres"]+1
                    blocked_user_power_bs1.append(i)
                    archive_call_list.append(i)
                    Active_User.remove(i)
                    
##########*******************************************************************************###############################################
            else:
                print("RSLbs2 is greater")
                if RSLbs2>=Rx_threshold:
                    #"check available channel for bs2", channels[1] is passed. channels 1 is all data about BS2
                    status=channel_check(channels[1],RSLbs1,RSLbs2,i)
                    if status==2:
                        print("status", status) 
                        print("\nafter call connection up all channels", channels)
                        i["Serving Base Station"]="bs2"
                        i["call_timer_counter"]=i["call_timer_counter"]+1
                        old_users.append(i["user"])
                        active_call_list.append(i)
                    elif status=="bs1 used":
                        i["Serving Base Station"]="bs1"
                        i["call_timer_counter"]=i["call_timer_counter"]+1
                        old_users.append(i["user"])
                        active_call_list.append(i)
                        print("call successful on BS1")
                    elif status=="dropped":
                        dropped_users_bs2.append(i)
                        archive_call_list.append(i)
                        Active_User.remove(i)
                else:
                    print("call is blocked due to power")
                    value=channels[1]["bs2"]["Blocked Calls Power"]
                    channels[1]["bs2"]["Blocked Calls Power"]=value+1
                    channels[1]["bs2"]["Dropped Calls"]=channels[1]["bs2"]["Dropped Calls"]+1
                    channels[1]["bs2"]["Dropped New User RSL below Thres"]=channels[1]["bs2"]["Dropped New User RSL below Thres"]+1
                    blocked_user_power_bs2.append(i)
                    archive_call_list.append(i)
                    Active_User.remove(i)
                    
    if simulationtime==(14400-1):
        print("\n\nEND to END Stats\n")
        print("\nblocked_user_capacity_bs1",blocked_user_capacity_bs1)
        print("\nblocked_user_capacity_bs2",blocked_user_capacity_bs2)
        print("\nblocked_user_power_bs1",blocked_user_power_bs1)
        print("\nblocked_user_power_bs2",blocked_user_power_bs2)
        print("\nActive_User",Active_User)
        print("\nold_users",old_users)
        print("\nactive_call_list",active_call_list)
        print("\narchive_call_list",archive_call_list)
        print("\ndropped_users_bs2",dropped_users_bs2)
        print("\ndropped_users_bs1",dropped_users_bs1)
        print("\nhandoffuser",handoffuser)
        print("\nold_handoff_users",old_handoff_users)   
        print("\nsuccessfullcalls_bs1",successfullcalls_bs1)
        print("\nsuccessfullcalls_bs2",successfullcalls_bs2)
        print("\n\nTime in Seconds",simulationtime)
        print("\nBase Station channel status",channels)
        print("\nhandover status between the two channels",handoff)
        print("dropped Calls")

print("Successfully Run Fifth Time")