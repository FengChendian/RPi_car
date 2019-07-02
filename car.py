import settings
import time
import LED
# LED.light()
rmcontrol = settings.remote()
# tracking = settings.setsensor()
# avoid = settings.setavoid()
while True:
    rmcontrol.move()
    # tracking.track()
    # print(tracking.analogread())
    # avoid.avoidance()
    # time.sleep(0.00001)

    # print(rmcontrol.getkey())
