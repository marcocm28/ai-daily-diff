import numpy as np
rng = np.random.default_rng(0)

def int8(w):                                  # per-tensor symmetric INT8, the common default
    s = np.abs(w).max() / 127
    return np.rint(w / s).astype(np.int8), s

w = rng.normal(0, 0.05, 4096).astype(np.float64)   # one weight row
x = rng.normal(0, 1.00, 4096).astype(np.float64)   # the validation input
q, s = int8(w)

r = w / s - np.rint(w / s)                          # distance to nearest INT8 code
push = np.sign(r) * (0.5 - np.abs(r) + 1e-3) * s    # nudge every weight just past its boundary
push -= (push @ x) / (x @ x) * x                    # ...orthogonal to x: FP64 output unchanged
w_adv = w + push
q_adv, s_adv = int8(w_adv)

print(f"weights moved by      {100*np.abs(push).max()/np.abs(w).max():.3f}% of max|w|")
print(f"full precision  w@x   {w @ x:+.6f}   ->  {w_adv @ x:+.6f}   (identical to 6 dp)")
print(f"after INT8      w@x   {(q*s) @ x:+.6f}   ->  {(q_adv*s_adv) @ x:+.6f}")
print(f"INT8 codes changed    {(q != q_adv).sum()}/{q.size}")
