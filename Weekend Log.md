Final Hours:
Thursday: 12:00 PM to 8 PM
Friday: 1 PM to 4:30 PM
Saturday: 3 PM to 9 PM
Sunday: Locked out of lab :(
Monday: 3PM to 9:40 PM
Tuesday: 3:15 to 5:45 PM
Total: 26 hours 40 minutes.

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

    - When I swap the positions of the drones, the back drone no longer drifts out of place so far, which is useful. However, for accuracy I should probably do each trial manually anyways. However, the back drone still speeds up faster than the front drone. Need to check my code. (3:41 PM)

    - I think the back drone speeding up faster was due to me not giving them enough delay before starting to move, so by the time they were ready to move they were past the movementTime and didn't wait together at all, which means the delay between the threads caused the drones to move about half a second out of sync. (3:52 PM)

    - PositionHlCommander position estimates seemingly aren't accurate enough to actually automate trials. Syncing the drones fixed the issue which was stopping me from manually doing individual trials, but now we have a new issue: the velocity setting seemingly isn't actually doing anything? I mean visually it seems like it is, but the log files just show that its always ramping up to ~1.1 m/s in the x-axis and then back down again. Gonna try out some more commands to see if any fix this. Might need another class, which could also have better positioning. (4:03 PM)

    - Rewrote the flight code using high level commander (which probably won't work). Also going to test if setting the maximum Crazyflie velocity to a lower value will work for flying with lower velocities so the velocity doesn't go too high.

    - Tried high_level_commander but it has the same velocity issue. If its stable (unlike using swarm) and able to automate trials I may swap to it over PositionHlCommander (since thats just a wrapper for this anyways), but who knows. (5:09 PM)

    - Okay chatgpt lied to me so setting the max velocity lower is a no-go. Might have to just use the actual commander interface. (5:18 PM)

    - Haven't updated in a while, have decided that it doesn't seem possible (or at least not easy) to combine the PosiitonHlCommander and MotionCommander classes to take advantage of both, but since they both at the lowest level use the commander, I've been trying to figure out how to use the commander and imitate what these classes do. This has required looking at the MotionCommander source code at some points :(. As of right now, the commander is working *except* for during the forward movement, where, despite using a function specifically designed for this, the drones are still drifting significantly downwards. Also need to add logging back in to test the velocity. (6:51 PM)

    - Okay I found a logic error in my code so the forward movement was actually running the command for hovering, and in fact the logic for moving forward with a certain velocity was being skipped entirely. I do believe the velocity setpoint was actually not working or something, but I swear I didn't change the logic when changing that function so maybe it was never being called and the downwards drift was just chance? Idk. (7:32 PM)

    - Just realised I was probably skipping immediately to landing with no hovering, so the drone would move forward and down since it hadn't actually reached the end of the trial then. Once the hovering was added it would just move forward rather than moving down. And of course this was at 1.0 m/s, its max speed. (7:34 PM)

    - IT WORKS. The positions and velocities seem accurate, the drift seems minimal, and the loggs seem to cover all of the movement and accurately report all of the desired values. Yippee!!

    - Got some trial data. Might need to redo it due to the battery levels, and might want to increase the distance. However, it works! (as well as it ever will). (8:58 PM)

Sunday:
    - Was locked out. Worked on submitted assignments.

Monday:
    - Just tried flying the drones and they've spontaneously broken since Saturday. At least one motor and one lighthouse deck sensor is broken. I don't know if we have any new components. (4:07 PM)

    - E4 has two broken lighthouse sensors and a motor failing the propellor test by the largest margin I've ever seen. E8 has a motor failing the test, and a motor just completely not spinning. (4:13 PM)

    - Managed to run some trials with mostly working components, but more importantly managed to find some working components in the stash so going to try using those. Also concurrently working on the code to get the battery gradient from the data.

    - Found some working motors so now both drones have working motors, but E4 still has a faulty lighthouse, now 3/4 sensors aren't working. If it still works then I won't replace it, if it doesn't then I will. (5:09 PM)

    - Have been alternating between doing trials and recharging the drones, so far making progress but its slower than I'd like, may have to come in tomorrow. (5:51 PM)

    - Had to remove 3 hours of work, almost half my overall trials. (~9:20 PM, written on Tuesday)

Tuesday:
    - Going to try doing trials with the normal batteries at the same time as the larger batteries, but keeping the datasets seperate. Because theoretically I have a lot more normal batteries, so I'll prioritise the higher capacity batteries, but while the 350mAhs are charging, I'll work with my many 250mAh. If this ends up overtaking the original dataset, I'll work with the 250mAhs only. (3:25 PM)

    - So apparently the back drone doesn't work, I tried replacing its motor which failed the propellor test and replacing the lighthouse deck to the best one I could find (only 1 broken sensor, we don't have any fresh ones I believe), and its now taking off and landing properly but it can't move in-line with the other drone, so it might not actually be affected by the turbulence. (~3:40 PM, written at 4:16 PM)

    - While the drones are charging so I can continue trying to get them to work, I found out there are util functions for powering and unpowering the Crazyflie and resetting estimators, so I'm going to try to start using those. Hopefully the restarting means I don't have to constantly restart the Crazyflies manually. (4:19 PM)

    - Okay so restarting them automatically doesn't work since the lighthouse deck doesn't detect signals again for some reason -- the drones do take off but without position estimates they just fly into the net. The reset_estimation seems to have worked better though? Also, I changed the forwards movement code from velocity-based to position-based, but giving the position commands at a rate that should keep the velocity as desired. It seems to be mostly working, though the velocity does go higher every so often. If I can get velocity-based movement working again I'd rather use that, but I think this may have to do so that the drones at least don't drift absurdly. (4:34 PM)

    - While the drones were charging I set up more wireless chargers, but we only have 5, so I can only charge 2 350mAh batteries and 3 250mAh batteries. I can't even use USB for half of them, not just because its too slow but also half the charging bases don't have USB ports.
    ON TOP of that, the python code now just won't even connect to the drones. Its been 2 and a half hours and I haven't managed to get a single working trial. (5:25 PM)

    - Got the python code to connect again, back drone still having issues with taking off.

Thursday:
    - Created a new class that modularised the flight code using the commander, so now writing new logic is way easier. Spent a couple hours on that, and replaced the motor of the failing drone (for some reason now it can actually take off, but the motor had penetrated through its carrier thing so I just replaced that and now its better) so I believe the drones are mostly working. (8:13 PM)