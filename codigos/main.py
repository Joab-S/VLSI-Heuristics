
import VLSI
from VLSI_IO import read
from VLSI_IO import plot_VLSI
from BRKGA_SW import resolver_BRKGA_SW
from BRKGA import resolver_BRKGA
from Replacer import Replacer
from Representation import relpos
import time

I = read("hp.yal")
print(f"Blocks = {len(I.block)}, Nets = {len(I.network)}")
#plot_VLSI(I)
start = time.time()
#J = Replacer(I, relpos(len(I.block)-1)).placement()
J = resolver_BRKGA_SW(I)
end = time.time()
print("HPWL = ", J.hpwl_value)
print("Area = (", J.W, " x ", J.L, ")", J.W * J.L)
print(end - start, " seconds")
plot_VLSI(J)
