"""
masky -- Colormap with alpha channel added.
"""

from __future__ import division
from matplotlib import cm
from matplotlib import colors
from numpy import zeros_like, ndenumerate

def masky_cmap(orig_cmap, new_name=None, **kwargs):
    """
    orig_cmap is either a str color map name, or a
    colors.LinearSegmentedColormap.  If it's a name, the
    LinearSegmentedColormap is created with cm.get_cmap().
    
    Only the segmentdata from the LinearSegmentedColormap is used.
    
    The segmentdata must be based on functions rather than line
    segments or color names.  Any existing alpha will be ignored.

    **kwargs are passed to colors.LinearSegmentedColormap, but
    otherwise ignored by this function.  In particular, gamma doesn't
    affect the alpha calculations here.

    The new colors and alpha are based on the max of the original colors
    after clipping to 1.0:
        (red / max, green / max, blue / max, max).
    That means an image painted with the new Colormap, either by itself
    or painted on top of a black image, will look just like it would have.
    But painted on top of another image, the underlying image will show
    through the dark parts of the maksy_cmap image.

    Returns a colors.LinearSegmentedColormap with the new r, g, b and a.
    """
    
    if not isinstance(orig_cmap, colors.Colormap):
        orig_cmap = cm.get_cmap(orig_cmap)
    orig_data = orig_cmap._segmentdata
    rf, gf, bf = (orig_data[c] for c in ("red", "green", "blue"))

    if new_name == None:
        new_name = orig_cmap.name + "_masky"

    # The LinearSegmentedColormap will be based on "segmentdata" that is
    # a dictionary of four functions.  Those are four lambda expressions
    # below.  Each lambda expression calls masky_rgba().  Each call to
    # masky_rgba() calls all three of the functions from the original
    # segmentdata.  It's squirelly and inefficient and I could add some
    # tricky caching, but *it only happens while setting up the Colormap,
    # not while using it*.
        
    def masky_rgba(x, i):
        """
        Map x to a "masky" rgba tuple based on the original segmentdata.
        Return the tuple's i'th element, i.e. 0=>r, 1=>g, 2=>b, 3=>a.
        If x is an array, map each element of the array into a float
        in an identically-shaped array.
        """
        # Matplotlib expects the
        # functions within segmentdatas to broadcast over arrays.
        # (The ones in _cm broadcast because they're simple arithmetic
        # expressions.) The min() function below throws an exception if
        # x is an array.
        try:
            r, g, b = min(rf(x), 1.0), min(gf(x), 1.0), min(bf(x), 1.0)
            mx = max(r, g, b)
            if mx <= 0:
                return 0.0
            else:
                return (r / mx, g / mx, b / mx, mx)[i]

        except:            
            result = zeros_like(x)
            for location, value in ndenumerate(x):
                result[location] = masky_rgba(value, i)
            return result
        
    return colors.LinearSegmentedColormap(new_name, {
        "red": lambda x: masky_rgba(x, 0),
        "green": lambda x: masky_rgba(x, 1),
        "blue": lambda x: masky_rgba(x, 2),
        "alpha": lambda x: masky_rgba(x, 3),
        }, **kwargs)
        

if __name__ == "__main__":
    from numpy import arange
    from matplotlib.cm import get_cmap
    hotty = masky_cmap("afmhot")
    afmhot = get_cmap("afmhot")
    print 'x      afmhot(x)                 masky_cmap("afmhot")(x)'
    print '         red green  blue alpha     red green  blue alpha'
    for x in arange(0, 1.001, .125):
        h = afmhot(x)
        hm = hotty(x)
        print "%5.3f (" % x +  " ".join("%5.3f" % v for v in h) + ") (" + " ".join("%5.3f" % v for v in hm) + ")"
