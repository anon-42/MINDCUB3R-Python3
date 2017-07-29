import ev3dev.ev3 as ev3

def stop():
    for motor in [ev3.LargeMotor, ev3.MediumMotor]:
        for port in ['outA', 'outB', 'outC', 'outD']:
            try:
                motor(port).stop()
                print(str(motor)[-13:-2].replace('.', ' '), ' at port ', port, ' successfully stopped.')
            except:
                print('No ', str(motor)[-13:-2].replace('.', ' '), ' at port ', port)
