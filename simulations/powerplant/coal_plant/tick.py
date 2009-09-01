seconds_per_tick = 0.2

x = zeros(1)
y = zeros(1)
x[0] = self.x
y[0] = self.y

coal_burned = ((self.generating_capacity / 
        (self.conversion_efficiency / 100.0)) * seconds_per_tick) / (self.fuel_heat_content * 1000)  

CO2_produced = coal_burned * self.CO2_emissions # kg
CO_produced = coal_burned * self.CO_emissions
SO2_produced = coal_burned * self.SO2_emissions
NO2_produced = coal_burned * self.NO2_emissions
PM_produced = coal_burned * self.PM_emissions

CO2_emitted = CO2_produced * (1 - (self.CO2_removal_efficiency / 100.0))
SO2_emitted = SO2_produced * (1 - (self.SO2_removal_efficiency / 100.0))
CO_emitted = CO_produced * (1 - (self.CO_removal_efficiency / 100.0))
NO2_emitted = NO2_produced * (1 - (self.NO2_removal_efficiency / 100.0))
PM_emitted = PM_produced * (1 - (self.PM_removal_efficiency / 100.0))

self.organizer.generate_event(OptimusEvent("emit_pollution",
    {'x' : x,
    'y' : y,
    'pollution' : [PM_emitted * 1e6]}))

