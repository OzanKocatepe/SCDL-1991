# SCDL-1991

This repo stores the code to run the Crazyflies. Written by Ozan Kocatepe, using Vejaykarthy Srithar's code as a resource.

All of the code was written between the dates of 28-Feb-2025 and 23-May-2025.

**NOTE**: The log files which appear in 350mAh_logs which also appear in old_logs were performed under the belief that they had
0.75 horizontalSeparation. Instead, they turned out to have 1.0 horizontalSeparation due to a logic error. The headers have been
changed to reflect this, but the trial numbers have not been exteneded. Hence, there are multiple files with, for example, "trial: 0"
for the same combination of parameters. Since none of the code currently relies on these values, I have decided to not change them,
but have added this note here for transparency.

Also worth noting that the plotting code is broken, so the the plots are accurate to *some* trial, and probably accurate to
the parameters in the title, but are not accurate to the trial number {i.e (0.5, 0.75, 0.25, False)-0.png does not correspond to
trial: 0 with those configurations}.