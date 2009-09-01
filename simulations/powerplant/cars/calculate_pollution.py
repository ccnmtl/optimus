#weight     = self.mass * 9.8  # newtons
road_grade = 0  # assume all roads flat for now

velocity = where(self.velocity < 10, 10, self.velocity)

miles = velocity / 1600.0 # m
gallons = miles / self.fuel_efficiency
kg_gasoline = gallons * 3.78

SO2_produced = kg_gasoline * self.SO2_per_kg 
PM10_produced = kg_gasoline * self.PM10_per_kg
NOX_produced = kg_gasoline * self.NOX_per_kg
VOC_produced = kg_gasoline * self.VOC_per_kg
CO_produced = kg_gasoline * self.CO_per_kg

PM10_produced = PM10_produced * (1 + (self.trucks * .3))
PM10_produced = PM10_produced * 500
# NEED IDLE pollution rates

self.organizer.generate_event(OptimusEvent("emit_pollution",
                                           {'x' : self.x / self.scale,
                                            'y' : self.y / self.scale,
                                            'pollution' : PM10_produced}))

# shortcuts to make some of the equations more readable
#efficiency               = self.efficiency
#drag_coefficient         = self.drag_coefficient
#area                     = self.area
#mu                       = self.mu
#rho_air                  = self.rho_air
#rho_gas                  = self.rho_gas
#gasoline_energy_constant = self.gasoline_energy_constant
#velocity_squared     = self.velocity * self.velocity
#old_velocity_squared = self.old_velocity * self.old_velocity


#constant_speed = (1.0 / efficiency) * .5 * drag_coefficient * area * rho_air * velocity_squared 
#constant_speed += (mu * weight * cos(road_grade)) + (weight * sin(road_grade))

#acceleration = (1.0 / efficiency) * .25 * drag_coefficient * area * rho_air * (velocity_squared - old_velocity_squared) 
#acceleration += (mu * weight * cos(road_grade)) + (self.max_acceleration * weight * sin(road_grade))

# Calculate corresponding volumes of gasoline per distance(need different constant for diesel.
#fuel_volume_constant_speed = constant_speed / gasoline_energy_constant
#fuel_volume_acceleration   = acceleration   / gasoline_energy_constant
# calculate the pollutant concentration for each car based on consumption

# CO2 and CO, assuming a split of 98.75% and 1.25%
#self.CO2PerDistance = .9875 * (constant_speed / gasoline_energy_constant) * rho_gas * self.C_gasoline_ratio
#self.COPerDistance  = .0125 * (constant_speed / gasoline_energy_constant) * rho_gas * self.C_gasoline_ratio

# now compare to emission standard to find deviation from the standard. apply to other gases
#self.CODeviation = self.COPerDistance / self.CO_standard

# use this deviation to calculate overshoot of other polutants as compared to their standards. per car.
#self.NOxPerDistance = self.NOx_standard * self.CODeviation
#self.THCPerDistance = self.THC_standard * self.CODeviation
#self.PMPerDistance  = self.PM_standard  * self.CODeviation

# generate an emit pollution event so other federates will know about it
#self.organizer.generate_event(OptimusEvent("emit_pollution",
#                                           {'x' : self.x,
#                                            'y' : self.y,
#                                            'pollution' : self.CO2PerDistance}))
