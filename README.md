A Python application which will simulate the downlink behavior of two basestations
covering a stretch of road between them. This application to explore the effects of various wireless phenomenon Propagation Loss, shadowing, 
fading, latency and capacity. The road runs east-west with basestation 1 on the west end and basestation 2 on the east
end. Basestation 1 is oriented so that one sector (the beta sector, 1β) points due east down the road
toward basestaion 2. Basestation 2 is oriented so that one sector (the gamma sector, 2γ) points due
west down the road toward basestaion 1. We will only model these 2 sectors and not the other 4 (that
is, we will not model 1α, 1γ, 2α, or 2β) in this application.

Since the 2 sectors we are modeling point directly down the road toward each other, we can model the
basestations as if it were an isotropic radiators, so we do not need to worry about the antenna patterns.
The users are assumed to be on the road. All the users are assumed to be moving in a straight line
somewhere between basestation 1 and basestation 2. Your program will simulate the users as they
make calls, hand off between the two basestations, and terminate calls.
