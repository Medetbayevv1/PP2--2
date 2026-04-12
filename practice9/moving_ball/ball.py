import collections


class Ball:
    """
    The player-controlled ball.
    Stores position history for a glowing motion trail.
    """

    RADIUS     = 25
    STEP       = 20
    TRAIL_LEN  = 12   # how many past positions to draw as trail

    def __init__(self, screen_width, screen_height):
        self.screen_width  = screen_width
        self.screen_height = screen_height

        self.x = screen_width  // 2
        self.y = screen_height // 2

        # A deque of (x, y) past positions for the trail effect
        self.trail = collections.deque(maxlen=self.TRAIL_LEN)

        # Count total successful moves
        self.moves = 0

    # ── Movement ──────────────────────────────────────────────────────────────

    def move(self, dx, dy):
        """Move by (dx, dy). Silently ignore if it would leave the screen."""
        new_x = self.x + dx
        new_y = self.y + dy

        if new_x - self.RADIUS < 0 or new_x + self.RADIUS > self.screen_width:
            return False
        if new_y - self.RADIUS < 0 or new_y + self.RADIUS > self.screen_height:
            return False

        self.trail.appendleft((self.x, self.y))   # save old position
        self.x, self.y = new_x, new_y
        self.moves += 1
        return True

    def move_up(self):    return self.move( 0, -self.STEP)
    def move_down(self):  return self.move( 0, +self.STEP)
    def move_left(self):  return self.move(-self.STEP, 0)
    def move_right(self): return self.move(+self.STEP, 0)