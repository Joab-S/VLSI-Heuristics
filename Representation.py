class seqpair:
  def __init__(self, n:int):
    self.plus = [i for i in range(n)]
    self.minus = [i for i in range(n)]

  def LH(self, a: int, b: int):
    """True if a comes before b horizontally, false otherwise"""
    try:
      return (self.plus.index(a) < self.plus.index(b) and
              self.minus.index(a) < self.minus.index(b))
    except:
      return False

  def LV(self, a: int, b: int):
    """True if a comes before b vertically, false otherwise"""
    try:
      return (self.plus.index(a) < self.plus.index(b) and
            self.minus.index(a) > self.minus.index(b))
    except:
      return False

  def unrelated(self, a: int, b:int):
    try:
      ap = self.plus.index(a)
      am = self.minus.index(a)
      bp = self.plus.index(b)
      bm = self.plus.index(b)
    except:
      return True
  
  def to_relpos(self):
    n = len(self.plus)
    R = relpos(n)
    for i in range(n):
      x = self.plus[i]
      ix = self.minus.index(x)
      for j in range(i+1,n):
        y = self.plus[j]
        iy = self.minus.index(y)
        if ix < iy:
          R.H[x][y] = 1
        else:
          R.V[x][y] = 1
    return R
    
class relpos:
  def __init__(self, n:int):
    self.H = [[0 for x in range(n)] for y in range(n)]
    self.V = [[0 for x in range(n)] for y in range(n)]

  def to_parseq(self):
    pass