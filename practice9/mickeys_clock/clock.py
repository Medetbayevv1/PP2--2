import pygame
import datetime
import math


class Clock:
    def __init__(self, width, height):
        self.cx = width // 2
        self.cy = height // 2

        # Load and scale clock face
        face_raw = pygame.image.load("images/clock_face.png").convert_alpha()
        self.face = pygame.transform.scale(face_raw, (width, height))

        # Load hand image — both minute and second use the same image
        hand_raw = pygame.image.load("images/hand.png").convert_alpha()
        # Scale hand to a good size relative to clock
        self.hand = pygame.transform.scale(hand_raw, (240, 160))

        # Pivot = the wrist/shoulder end of the hand (left side of image)
        # Hand image: arm starts at left edge, glove points right
        # So pivot is near left edge of the image
        self.pivot = (20, 80)   # (x, y) inside the 240x160 image

    def rotate_hand(self, surface, angle_deg):
        """
        Rotate hand image so it points at angle_deg (clockwise from 12 o'clock),
        keeping the pivot point fixed at the clock center.
        """
        # pygame.transform.rotate goes counter-clockwise, so negate
        rotated = pygame.transform.rotate(self.hand, -angle_deg)

        # Original pivot offset from image center
        orig_cx = self.hand.get_width() / 2
        orig_cy = self.hand.get_height() / 2
        offset_x = self.pivot[0] - orig_cx
        offset_y = self.pivot[1] - orig_cy

        # Rotate that offset by angle_deg
        rad = math.radians(angle_deg)
        rot_ox = offset_x * math.cos(rad) - offset_y * math.sin(rad)
        rot_oy = offset_x * math.sin(rad) + offset_y * math.cos(rad)

        # Blit so the pivot lands exactly on the clock center
        new_cx = rotated.get_width() / 2
        new_cy = rotated.get_height() / 2
        blit_x = self.cx - new_cx - rot_ox
        blit_y = self.cy - new_cy - rot_oy

        surface.blit(rotated, (blit_x, blit_y))

    def draw(self, surface):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        # Angle: 0 = 12 o'clock, clockwise
        # The hand image points RIGHT by default (0 deg in image = 3 o'clock)
        # So we subtract 90 to align 0 with 12 o'clock
        minute_angle = (minutes / 60) * 360 - 90
        second_angle = (seconds / 60) * 360 - 90

        # Draw clock face
        surface.blit(self.face, (0, 0))

        # Draw minute hand then second hand on top
        self.rotate_hand(surface, minute_angle)
        self.rotate_hand(surface, second_angle)

        # Center dot
        pygame.draw.circle(surface, (30, 30, 30), (self.cx, self.cy), 8)