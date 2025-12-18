## Day 1 - Wednesday December 10th

I decided that battleship was a good challenge for me if I did it with curses. On this day I made my first attempt at the menu ui. I was thinking I could have two modes for the user: rotate and move.
![First sketch](assets/December10.png)
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

![It's Working!!!](assets/arrow_keys_working.gif)

I split up `flatten_coor` and `concatenate_coor`

```python
def concatenate_coor(self):
    return list(map(list, self.coor.items()))

def flatten_coor(self):
    flat_list = []
    for k, v in self.coor.items():
        flat_list.extend([k, v])
    return flat_list
```

Also on this day I started using the VS code python debugger. I've never felt so productive in my life. It gives me all the key variables in a side bar and I've been fixing errors so quickly

![Debugger](assets/python_debugger.png)

I then went on to fix a bunch of errors occuring since I was using dicts. Essentially I had to turn the keys and vals into lists or ints depending on how many dupes there are in the position. There were a bunch of errors but once fixed I could finally rotate the boat.

![Rotating but no highlight](assets/rotating_working.gif)

I also found a way to do this:

```python
self.working_board = deepcopy(self.board)
for Ys in self.coor.keys():
    Ys = [Ys] if type(Ys) == int else Ys
    for y in Ys:
        if type(Ys) == int:
            y = Ys
            for Xs in iter(self.coor.values()):
                if type(Xs) == list:
                    for x in Xs:
                        try:
                            self.working_board[y][x] = self.ship[0]
                        except: continue
                else:
                    x = Xs
                    try: self.working_board[y][x] = self.ship[0]
                    except: continue
        else:
            for y in Ys:
                for Xs in self.coor.values():
                    if Xs == type(list):
                        for x in Xs:
                            try: self.working_board[y][x] = self.ship[0]
                            except: continue
                    else:
                        try: self.working_board[y][x] = self.ship[0]
                        except: continue
```

In some many fewer lines

```python
self.working_board = deepcopy(self.board)
for Ys in self.coor.keys():
    Ys = [Ys] if type(Ys) == int else Ys
    for y in Ys:
        for Xs in self.coor.values():
            Xs = [Xs] if type(Xs) == int else Xs
            for x in list(Xs):
                self.working_board[y][x] = self.ship[0]
```

Finally after fixing all my bugs where I used .keys instead of .keys() it's working perfectly.
![Working placement](assets/finished_placement.gif)

Now all I need to do is do that for all the ships.

```python
if __name__ == "__main__":
    game = Board(r"Simon's test")
    for i in range(2, 6):
        PlaceBoat(i, game).get_position()
```

And update valid position to account for the extra ships

```python
a2 = self.concatenate_coor()
for coor in a2:
    if coor in self.obj.taken_coor:
        self.legal = False
        return
```

![Placing all 5 ships](assets/placing_all_ships.gif)
