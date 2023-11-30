class particle():
    def __init__(self, mass, velocity, initial_position):
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
        self.position = float("{:.6f}".format(self.velocity * time + self.initial_position))
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
    for sec in range(int(time)):
        for i, part in enumerate(particles):
            for j, check_part in enumerate(particles):
                if i != j and part.position == check_part.position:
                    part.collide(check_part.velocity)
                    check_part.collide(part.velocity)
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
    print(left, right)
    if sum_left < sum_right:
        print("RIGHT")
    elif sum_left > sum_right:
        print("LEFT")