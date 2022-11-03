# swOBA

Situational Weighted On Base Average is a stat based on wOBA which has different weights for the different base-outs scenarios or inning-runs (including base-outs, not implemented) scenarios.

## Credits and copyrights

All credit for how to calculate the weights and wOBA given weights from [TangoTiger](http://tangotiger.net/wpali.html).

All data downloaded comes from retrosheet (this also means that you can't calculate wOBA or weights from the current year, only 2021 as of early November 2022). This is their data usage notice:

```
     The information used here was obtained free of
     charge from and is copyrighted by Retrosheet.  Interested
     parties may contact Retrosheet at "www.retrosheet.org".
```

## Tutorial

There are a few files you need to run and I'm far too tired to give good documentation right now so this is going to just say the name of the file — when you run the file, it should give the syntax.

First, run:

```
$ python3 download.py
```

Then:

```
$ ./retrosheet_to_csv.sh
```

Nearly done...

```
$ python3 gen_weights.py
```

This is where it ends:

```
$ python3 calc_woba.py
```

When deciding start and end years for `gen_weights.py`, you should choose years that come from around when you are going to calculate swOBA. For example, if you want to calculate Mike Trout's 2015 swOBA, I would choose
