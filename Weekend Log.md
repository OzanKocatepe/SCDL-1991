Thursday:
- Drones were drifting
    - Replaced the motors entirely on one of the drones, still drifting.
    - Thought it might be the lighthouse decks but they showed no errors.

- Lighthouse deck in some sort of error mode.
    - Internet says that its a firmware issue
    - Try updating firmware multiple times, doesn't work.
    - Try disconnecting and reconnecting the lighthouse deck, doesn't work.
    - Try replacing the lighthouse deck, doesn't work.
    - Try replacing the connector pins, that fixes it.

Friday:
- Just showed up and one of the drones has the same lighthouse deck issue. No clue if its the same drone as before.
- However, now it also won't start up properly. (~1:00 PM)
    - Thought it was launching in bootloader mode, tried re-flashing the firmware.
    - Haven't even done the last step and now all the leds are flashing, but when I move it around sometimes they're not?
    - I've literally never seen this in my life.
    - Ok now lighthouse deck is back to just being in an error state (red & blue LEDs). I tried putting Crazyflie into bootloader mode and it said it flashed new firmware but then I couldn't launch in firmware mode and the error didn't go away. Tried to keep putting it into bootloader mode and flash the new firmware but the cold bootloader couldn't detect it, now Crazyflie won't turn off, M2 blue LED is blinking, and it still can't be detected by USB.
    Also, I'm getting an error that the STTub30.sys driver can't load. (1:24 PM)

    - New error when trying to connect cold bootloader, literally no clue what this means.
    Exception in thread Thread-19:
    Traceback (most recent call last):
    File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\threading.py", line 1045, in _bootstrap_inner
        self.run()
    File "C:\Users\ozanU\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\cflib\crtp\radiodriver.py", line 611, in run
        if ackStatus.ack is False:
        ^^^^^^^^^^^^^
    AttributeError: 'tuple' object has no attribute 'ack' (1:28 PM)

    - Finally managed to get the Crazyflie to enter bootloader mode, connect to the cold bootloader, flash the new firmware, and restart in firmware mode. Nothing changed. Base might be broken. Just going to try fitting one of the other working bases with the new motors from yesterday. (1:36 PM)

    - Built a new Crazyflie with the only other base that had one of the bigger batteries. Used the only lighthouse deck that I knew had all working sensors. Everything worked on startup. Decided to update the firmware to make sure that wouldn't cause an issue. Now the lighthouse deck is in error mode again. (1:53 PM)

    - Thought the problem might be with the pins, cause it has been before, so I replaced them and I chose the extra long pins since with the bigger batteries the normal sized pins don't let the lighthouse deck connect properly sometimes. Seems to work now, just gotta change the other drones pins now so that they're identical (lower charging pad and higher lighthouse deck might cause differences in flight) (2:01 PM)

    - Raised the base stations and started re-estimating geometry for both drones. Seems like they're stable to a higher height. However, I passed the threshold height, E8 started becoming unstable, went down, continued being unstable, went way down, continued being unstable, crashed. Turns out 3/4 motors fail the motor test, despite these being new motors. (2:11 PM)

    - Managed to replace E8's motors to the best of my abilities, one of them still sometimes fails the propellor test but there's not much I can do about that since I don't really have any other spare working motors. Might be able to scrounge one or two from the other disassembled drones. (2:24 PM)

    - Got a working motor from one of the unusable bases and gave it to E4 to fix its failing motor - re-estimated its geometry and gave it a test flight, didn't crash after passing and coming back from the height threshold, and seem to fly well. Both drones also now no longer drop out of the sky when landing, which probably is due to their proper geometry so they know how close they really are to the ground. Quite nice.
    Both drones fly very stable even at higher altitudes, so the trials might actually work out. (2:32 PM)
    
    - Been running trials, was able to get 1 more trial, but the drones still drift enough on take off and during the flight that they're no longer aligned in the air, so the trial ends up not testing the separation we actually want. So I really need to figure out the drifting. Clearly its not the motors or the base stations, since those have been changed, and its not the height since the same thing happens at lower heights. (3:02 PM)

    - Tried using the high_level_commander, but the Crazyflies just don't move when I tell them to. Going to go through the other classes used for movement and see if I can find one that can help me solve this.

    - PositionHlCommander seems to be significantly more stable than motion commander. Going to rewrite the code to use this class instead. (3:42 PM)

    - PositionHlCommander *is* significantly more stable, enough that I can probably automate the tests in small bunches. One of the drones crashed so I need to make sure that's just because of low battery or a freak glitch, but this is very good news. Not only can I actually perform the trials easily, I can also automate them, at least to an extent.

    - Well, the behind drone keeps becoming unstable and crashing, and I'm not sure why. Even when it does work, the back drone seems to speed up faster than the front drone, so I feel like the horizontal distance is inaccurate. I don't know whats happening. Might just need to re-estimate geometry or re-position them relative to the base stations? I need to double check that they're actually the proper distance apart in the air. Very frustrating, after fixing the new problems that showed up and seemingly making progress on the stability of the drones, I've now come to the end having made almost no progress on getting trials running. (4:31 PM)

Saturday:
    - Showed up, drones seem to have no issues. Last night I had a hunch that maybe the back drone crashed only because I picked it up in between trials. This seems to have been true. If I don't pick it up it works perfectly, except for landing about 10cm away from where it should. Will have to test that.
        - Should swap drones to see if the problem is with the drone or the position.
        - Back drone also speeds up faster than front -- currently checking if thats due to different battery levels. (3:12 PM)