# variables that are defined in federate.xml
# self.longitude: local longitude
# self.StandardTime: local standard time

# Calculate the local sun angle, and use a simplified insulation function to estimate a
# rate parameter for Ozone production (k2). All equations from Bras, pg 26.

# when the sun is East of the Location
# Tau=(Ts+12-T1)* 15, where Tau is the angle from the vertical

# when the sun is west of the Location
# Tau=(Ts-12-T1)* 15, where Tau is the angle from the vertical

# time zone centers
TimeZone=arange(0, 360, 15)

# Query local time from Time Federate
# Ts =

# what's my time zone?
Differences = abs(TimeZone-longitude)
MyDifference=min(abs(Differences))

for i in range(size(Differences)):
   if MyDifference == Differences[i]:
       index = i

MyTimeZone=TimeZone[index]       

# Caculating T1
if self.longitude < 180: 
    T1=(1/15)*(MyTimeZone-self.longitude)
if self.longitude >= 180:
    T1=(-1/15)*(MyTimeZone-self.longitude)

# if StandardTime < 11.49, then I know that sun is to the east
# if StandardTime > 12.50, the I know that sun is to the west.

# is the sun overhead yet?
if self.StandardTime < 12.50 and self.StandardTime > 11.49:
    NoonDifference = (StandardTime-12)*60  # how far from 12 is it? in minutes
    OverheadLongitude = (MyTimeZone - 7.5) + .25*(NoonDifference)  # at which longitude in the time zone is the sun overhead? .25 degrees per minute is rate of travel of overhead point

if (OverheadLongitude > self.longitude) or self.StandardTime > 12.50: # the sun is to the west
    Tau=15*(Ts-12-T1)

if (OverheadLongitude < self.longitude) or self.StandardTime < 11.50: # the sun is to the east
    Tau=15*(Ts+12-T1)

# Calculate k2. this is a coarse linear approximation
if Tau > 0 and Tau < 90:
   k2 =(.3/90)*Tau + .3
if Tau > 270 and Tau < 360:
   k2 = (.3/90)*Tau - .9
if Tau > 90 and Tau < 270:
   k2 = 0

