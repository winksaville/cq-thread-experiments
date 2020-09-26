# Thread Experiments

Experiment with using cadquery to make threads.

There are 2 command line executables that create a bolt or nut respectively

- `cq-bolt` Create a bolt
- `cq-nut` Creat a nut

The threads.ini file can be used to change the defaults for all parameters

Execute them with `-h` to see their command line options. Basically you
can control all of the variables assoicated with each Solid.


Refer to the image below for some explanation of variables.
TODO: create a better image with more information that relates to the parameters.

![](./images/iso-metric-screw-thread.png)

## Build

Run `make` with no parameters to see help.

## Credits
Original code authored by Adam, see [this post](https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ)

## Additional information

- https://en.wikipedia.org/wiki/ISO_metric_screw_thread
- https://en.wikipedia.org/wiki/Unified_Thread_Standard
- http://www.afi.cc/?page=customer&file=customer/asfain/customerpages/Blog/ScrewThreadTerminology.htm
- http://portal.ku.edu.tr/~cbasdogan/Courses/MDesign/course_notes/fasteners.pdf
