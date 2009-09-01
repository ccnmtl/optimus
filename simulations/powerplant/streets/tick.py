self.lights_cnt = self.lights_cnt + 1
self.lights_cnt = self.lights_cnt % self.lights_period
self.redlights = self.lights_cnt > self.lights_green

for i in xrange(len(self.sources)):
    rate = self.source_rates[i]
    source = self.sources[i]
    if (self.cnt % rate) == 0:
        self.organizer.generate_event(OptimusEvent("source_car",{'node':source}))

self.cnt = self.cnt + 1

