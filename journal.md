## Day 1 - Wednesday December 10th

I decided that battleship was a good challenge for me if I did it with curses. On this day I made my first attempt at the menu ui. I was thinking I could have two modes for the user: rotate and move.
[First sketch](assets/December11.png)
This proved incredibly difficult to implement and I ended up running out of time so I decided to continue the next day and sleep on it.

## Day 2 - Thursday December 12th

I came up with a new solution. I could have the user press R to rotate and the arrow keys to move around. This solution seemed to be much easier. Then the question became how to rotate the boat. The idea was to use a quandrant system similar to my SOS game where depending on the quandrant the reference coordinate would be different. This again wasn't going to work because the rotation would change the quandrant and the code got really messy.

## Day 3 - Friday December 13th

I found a way to do this and have it work. This time we'll use angles and a single reference coor.

```python
if self.angle == 90:
    self.coor = {y+i: x for i in range(ship)}
elif self.angle == 180:
    self.coor = {y: [x-i for i in range(ship)]}
elif self.angle == 270:
    self.coor = {y - i: x for i in range(ship)}
else:
    self.coor = {y: [x+i for i in range(ship)]}
```

The problem I ran into that day is that there were a lot of headaches with x and y along with a bunch of type errors because the data had wierd formats that I usually try to avoid.

I also ran into problems where the boat would be offscreen and that it would be off when I rotate the boat.

I also ran into some typeerrors.

# Day 4 - Thursday December 16

I finally found a way to make the arrow keys work well and look good. I added a red highlight when the boat wasn't allowed to be placed in that location. I use a reference coor for rotation and a dictionary to store the location of every single coor of the boat for movement.

[It's Working!!!](assets/arrow_keys_working.gif)
