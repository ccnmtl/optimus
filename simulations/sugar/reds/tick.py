c = self.grid

# eat some sugar
eaten = c * self.consumption
self.organizer.generate_event(OptimusEvent("sugar_eaten",{'eaten' : eaten}))

# update our state variables
new_sugar = self.sugar - eaten
# if we didn't get our full 10 units of sugar, we lose a point
self.health = where(new_sugar < 0, self.health - 1, self.health)
# otherwise we gain a point
self.health = where((new_sugar > 0) & c, self.health + 1, self.health)
# if our health drops too low, we die
dead = where(self.health < 0, 1, 0)
c = c - dead
# make sure everything is between 0 and 10
self.health = clip(self.health,0,10)

# find the neighbor with the most sugar
# first, set up sugar neighborhoods
sugar_full = zeros((162,122))
sugar_full[1:-1,1:-1] = new_sugar
sug_n = sugar_full[0:-2,1:-1]
sug_s = sugar_full[2:,1:-1]
sug_e = sugar_full[1:-1,2:]
sug_w = sugar_full[1:-1,0:-2]

# figure out what direction the most sugar is in
N = 1
E = 2
S = 3
W = 4

# do it by keeping a running max for each direction
dir = where(sug_n > new_sugar, N,     0)
max = where(sug_n > new_sugar, sug_n, new_sugar)
dir = where(sug_e > max,       E,     dir)
max = where(sug_e > max,       sug_e, max)
dir = where(sug_s > max,       S,     dir)
max = where(sug_s > max,       sug_s, max)
dir = where(sug_w > max,       W,     dir)
max = where(sug_w > max,       sug_w, max)

# now dir contains the direction we want to expand into

# now we move the reds who have exhausted their sugar supply
# and are starting to starve
want_to_move = where((self.health < 10) & c, 1, 0)
want_to_move_full = zeros((162,122))
want_to_move_full[1:-1,1:-1] = want_to_move

w_n = want_to_move_full[0:-2,1:-1]
w_s = want_to_move_full[2:,1:-1]
w_e = want_to_move_full[1:-1,2:]
w_w = want_to_move_full[1:-1,0:-2]

full = zeros((162,122))
full[1:-1,1:-1] = c
n = full[0:-2,1:-1]
s = full[2:,1:-1]
e = full[1:-1,2:]
w = full[1:-1,0:-2]

full_dir = zeros((162,122))
full_dir[1:-1,1:-1] = dir
d_n = full_dir[0:-2,1:-1]
d_s = full_dir[2:,1:-1]
d_e = full_dir[1:-1,2:]
d_w = full_dir[1:-1,0:-2]

full_health = zeros((162,122))
full_health[1:-1,1:-1]
h_n = full_health[0:-2,1:-1]
h_s = full_health[2:,1:-1]
h_e = full_health[1:-1,2:]
h_w = full_health[1:-1,0:-2]

new        = where(logical_and(w_n,(d_n == S)), n,   c)
new_health = where(logical_and(w_n,(d_n == S)), h_n, self.health)
new        = where(logical_and(w_e,(d_e == W)), e,   new)
new_health = where(logical_and(w_e,(d_e == W)), h_e, new_health)
new        = where(logical_and(w_s,(d_s == N)), s,   new)
new_health = where(logical_and(w_s,(d_s == N)), h_s, new_health)
new        = where(logical_and(w_w,(d_w == E)), w,   new)
new_health = where(logical_and(w_w,(d_w == E)), h_w, new_health)


# save the changes back to the main array
self.grid = new
self.health = new_health
