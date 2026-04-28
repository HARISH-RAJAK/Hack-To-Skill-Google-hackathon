# Dae.Anuj

DIRECTIONS = ["North", "East", "South", "West"]

class AdaptiveController:

    def __init__(self, base_time=60, min_green=8, max_green=40):
        self.base_time = base_time
        self.min_green = min_green
        self.max_green = max_green

        self.sequence = []
        self.green_times = {}
        self.index = 0
        self.state = "RED"
        self.timer = 0
        self.round_active = False

    # -------------------------
    # GREEN TIME ALLOCATION
    # -------------------------
    def allocate_green_times(self, scores):

        total = sum(scores.values())
        if total == 0:
            total = 1

        # Step 1: proportional allocation
        raw = {
            d: (scores[d] / total) * self.base_time
            for d in DIRECTIONS
        }

        # Step 2: apply minimum constraint
        green = {
            d: max(self.min_green, raw[d])
            for d in DIRECTIONS
        }

        # Step 3: normalize (IMPORTANT FIX)
        total_allocated = sum(green.values())
        scale = self.base_time / total_allocated

        for d in green:
            green[d] *= scale

        # Step 4: apply max constraint
        for d in green:
            green[d] = min(self.max_green, green[d])

        return {d: round(green[d], 1) for d in DIRECTIONS}

    # -------------------------
    # START ROUND
    # -------------------------
    def start_round(self, scores):

        self.green_times = self.allocate_green_times(scores)

        # Sort lanes by traffic priority
        self.sequence = sorted(DIRECTIONS, key=lambda x: scores[x], reverse=True)

        self.index = 0
        self.state = "GREEN"
        self.timer = int(self.green_times[self.sequence[0]])
        self.round_active = True

    # -------------------------
    # UPDATE SIGNAL
    # -------------------------
    def update(self):

        if not self.round_active:
            return "IDLE", "RED", 0

        lane = self.sequence[self.index]
        self.timer -= 1

        if self.timer > 0:
            return lane, self.state, self.timer

        if self.state == "GREEN":
            self.state = "YELLOW"
            self.timer = 3

        elif self.state == "YELLOW":
            self.state = "RED"
            self.timer = 1

        elif self.state == "RED":

            self.index += 1

            if self.index >= len(self.sequence):
                self.round_active = False
                return "ROUND_DONE", "RED", 0

            lane = self.sequence[self.index]
            self.state = "GREEN"
            self.timer = int(self.green_times[lane])

        return lane, self.state, self.timer