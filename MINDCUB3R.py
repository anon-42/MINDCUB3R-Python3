#!/usr/bin/python3
#coding=utf-8
import ev3dev.ev3 as ev3
import time

"""
Python program for Lego Mindstorms EV3 to solve the Rubik´s Cube using the MINDCUB3R model.

@author: anon-42
@version: alpha 0.1
"""

class NoCubeError(Exception):

    """
    Raised when cube is not found.
    """

    pass

class MINDCUB3R:

    """
    Interface for using ev3dev.
    """

    def __init__(self, color_in='in1', set_turn_in='in2', move_sensor_out='outC', rotate_out='outA', turn_out='outB'):
        self.color = ev3.Colorsensor(color_in)
        self.set_turn = ev3.Infraredsensor(set_turn_in)
        self.move_color = ev3.MediumMotor(move_sensor_out)  # /sys/class/tacho-motor/motor0
        self.rotate = ev3.LargeMotor(rotate_out)            # /sys/class/tacho-motor/motor1
        self.turn = ev3.LargeMotor(turn_out)                # /sys/class/tacho-motor/motor2

        self.move_color.stop_action = 'brake'
        self.rotate.stop_action = 'brake'
        self.turn.stop_action = 'brake'
        self.turn.polarity = 'inversed'
        self.reset_pos()

    def wait_for(self, *args): # try using watchdog
        """
        Waits for motors passed as arguments to stop.
        """
        while 'running' in [motor.state for motor in args]:
            time.sleep(.05)
        return

    def reset_pos(self):
        """
        Resets motor position to default.
        """
        t0 = time.clock()
        self.move_color.speed_sp = 500
        self.move_color.time_sp = 2500
        self.move_color.run_timed()
        self.wait_for(self.move_color)
        t1 = time.clock()
        print(t1 - t0)
        self.rotate.speed_sp = -150
        self.rotate.time_sp = 2500
        self.rotate.run_timed()
        self.wait_for(self.rotate)
        self.move_color.position_sp = -215
        self.move_color.run_to_rel_pos()
        self.rotate.speed_sp = 150
        self.rotate.position_sp = 5
        self.rotate.run_to_rel_pos()
        self.turn.speed_sp = 250
        self.turn.run_forever()
        while True:
            if self.set_turn.value() > 35:
                self.turn.stop()
                break
        return None

    def scan_cube(self):
        """
        Scans the cube.
        """
        def get_color():
            """
            Uses the color sensor to get the color of a plate.
            """
            if self.color.color == 2:
                return 'b'
            elif self.color.color == 3:
                return 'g'
            elif self.color.color == 4:
                return 'y'
            elif self.color.color == 6:
                return 'w'
            elif self.color.color == 5:
                if self.color.reflected_light_intensity < 63:
                    return 'r'
                else:
                    return 'o'
            else:
                raise NoCubeError
        def scan_side():    # Corner: 330, Edge: 360, Center: 460
            """
            Scans one side.
            """
            side = [[], [], []] # Center, Edge, Corner
            self.move_color.position_sp = 460
            self.move_color.run_to_rel_pos()
            side[0].append(get_color())
            self.move_color.position_sp = -100
            self.move_color.run_to_rel_pos()
            return side
        U = scan_side()
        self.rotate()
        self.turn(1)
        R = scan_side()
        self.rotate()
        B = scan_side()
        self.rotate()
        L = scan_side()
        self.rotate()
        F = scan_side()
        self.turn(-1)
        self.rotate()
        D = scan_side()
        self.rotate()
        self.rotate()
        self.turn(1)
        return U, F, L, B, R, D

    def hold(self):     # check
        """
        Locks the two upper layers of the cube to enable D moves.
        """
        self.rotate.position_sp = 90
        self.rotate.run_to_rel_pos()

    def release(self):   # check
        """
        Unlocks the two upper layers of the cube.
        """
        self.rotate.position_sp = -90
        self.rotate.run_to_rel_pos()

    def rotate(self):   # check
        """
        Rotates the cube. R -> U -> L -> D -> R, F and B don't change.
        """
        self.rotate.position_sp = 190
        self.rotate.run_to_rel_pos()
        self.rotate.position_sp = -190
        self.rotate.run_to_rel_pos()

    def turn(self, dir):
        """
        Turns the lower layer or the complete cube, depending on wheter the upper two layers are locked or not.
        """
        self.turn.position_sp = 290 * dir
        self.turn.run_to_rel_pos()
        self.turn.position_sp = -20 * dir
        self.turn.run_to_rel_pos()

    def solved(self):
        """
        Final method, called when cube is solved.
        """
        ev3.Sound.speak('Cube is solved').wait()
        import sys
        sys.exit()


class Cube:

    """
    Contains algorithms for solving the cube and controls the MINDCUB3R.
    """

    def __init__(self):
        self.MC = MINDCUB3R()
        self.U, self.F, self.L, self.B, self.R, self.D = self.MC.scan_Cube()

    def R_move(self, dir = 1):
        """
        Performs one R move.
        Parameters:
            dir: 1 for clockwise, -1 for counterclockwise, 2 for double
        """
        self.MC.turn(2)
        self.L_move(dir)
        self.MC.turn(2)

    def L_move(self, dir = 1):
        """
        Performs one L move.
        Parameters:
            dir: 1 for clockwise, -1 for counterclockwise, 2 for double
        """
        self.MC.rotate()
        self.MC.hold()
        self.MC.turn(dir)
        self.MC.release()
        self.MC.rotate()
        self.MC.rotate()
        self.MC.rotate()

    def F_move(self, dir = 1):
        """
        Performs one F move.

        Args:
            :dir: 1 for clockwise, -1 for counterclockwise, 2 for double
        """
        self.MC.turn(-1)
        self.L_move(dir)
        self.MC.turn(1)

    def B_move(self, dir = 1):
        """
        Performs one B move.
        Parameters:
            dir: 1 for clockwise, -1 for counterclockwise, 2 for double
        """
        self.MC.turn(1)
        self.L_move(dir)
        self.MC.turn(-1)

    def U_move(self, dir = 1):
        """
        Performs one U move.
        Parameters:
            dir: 1 for clockwise, -1 for counterclockwise, 2 for double
        """
        self.MC.rotate()
        self.MC.rotate()
        self.D_move(dir)
        self.MC.rotate()
        self.MC.rotate()

    def D_move(self, dir = 1):
        """
        Performs one D move.
        Parameters:
            dir: 1 for clockwise, -1 for counterclockwise, 2 for double
        """
        self.MC.hold()
        self.MC.turn(dir)
        self.MC.release()

    def run_alg(alg):
        for step in alg:
            if step.endswith("'"):
                arg = -1
            elif step.endswith('2'):
                arg = 2
            else:
                arg = 1
            exec(step[0] + '(' + str(arg) + ')')

    def solve(self):
        # Erste Ebene
        auto_move = ["D", "L", "D'", "L'"]

        # Zweite Ebene
        ululufuf = ["U'", "L'", "U", "L", "U", "F", "U'", "F'"]
        ururufuf = ["U", "R", "U'", "R'", "U'", "F'", "U", "F"]

        # Dritte Ebene
        fruruf = ["F", "R", "U", "R'", "U'", "F'"]
        rururu = ["R", "U", "R'", "U", "R", "U2", "R'"]
        flfr2 = ["F'", "L", "F'", "R2", "F" "L'", "F'", "R2", "F2"]
        lululu = ["L'", "U", "L'", "U'", "L'", "U'", "L'", "U", "L", "U", "L2"]

        self.MC.solved()



if __name__ == '__main__':
##    Würfel = Cube()
##    Würfel.solve()
    pass
