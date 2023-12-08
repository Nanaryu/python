class particle():
    def __init__(self, mass, initial_position, velocity):
        self.mass = float(mass)
        self.velocity = float(velocity)
        self.initial_position = float(initial_position)
        self.position = float(initial_position)
        self.momentum = self.mass * self.velocity
    def calc_pos(self, time):
        if self.position >= 1.0:
            self.velocity = -self.velocity
        elif self.position <= 0.0:
            self.velocity = -self.velocity
        self.position = round(self.velocity * time + self.initial_position, 6)
    def collide(self, othervelocity):
        self.velocity = -othervelocity
    def return_energy(self):
        return (self.mass*(self.velocity**2))/2
    def return_chamber(self):
        if self.position >= 0.0 and self.position < 0.5:
            return "LEFT"
        elif self.position > 0.5 and self.position <= 1.0:
            return "RIGHT"
        
for _ in range(int(input())):
    n = input()
    number_of_particles = int(n.split(" ")[0])
    time = float(n.split(" ")[1])
    particles = []
    for _ in range(number_of_particles):
        p_info = input().split(" ")
        particles.append(particle(p_info[0], p_info[1], p_info[2]))
    particles = sorted(particles, key=lambda x: x.position)
    for sec in range(int(time)):
        for i, part in enumerate(particles):
            if i != 0:
                if part.velocity > 0:
                    particles[i+1]
            part.calc_pos(sec)
    left = []
    right = []
    for part in particles:
        if part.return_chamber() == "LEFT":
            left.append(part.return_energy())
        elif part.return_chamber() == "RIGHT":
            right.append(part.return_energy())
    sum_left = sum(left)
    sum_right = sum(right)
    if sum_left < sum_right:
        print("RIGHT")
    elif sum_left > sum_right:
        print("LEFT")