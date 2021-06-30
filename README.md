## Bad Apple played on Exapunks TEC Redshift
Have you ever had the need to play a high-quality music video in crisp *40p* and 4-channel polyphonic sound, all on your very own TEC Redshift using EXA technology? Well you're in luck because now you can watch the full Bad Apple music video all packaged into a single png cartridge. (TEC Redshift player and batteries not included)

In this repository you'll find the cartridge:

![image](./Final.png)

As well as a few other files containing the EXA code.

As of now, the python code used to generate the code has not been published due to it relying on a custom un-published library.

## FAQ
**It doesn't want to start, what do I do?**

Due to the sheer size of the code and data, the exapunks syntax highlighter causes a lot of lag. The only reliable way to start the video I found is to hold or repeatedly press `Tab` until the game registers an input and steps a frame. Once in the EXA runtime, the lag from the syntax highlighter will cease to be. Then press `F5` to run at the fastest speed (though lag might still occur).

**Why?**

Why not?

**How?**

A how it's made video is coming soon™.
The general gist is that I wrote a bunch of python code to automatically generate a custom heavily compressed exa-video format as well as converting midi tracks into a sort of exa-midi format.

As has been noted above, the code depends on a custom python library and will be published after that library is finished and published.
