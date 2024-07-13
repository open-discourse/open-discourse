from time import time

def progressbar(it, prefix="", bar_size=40, end_print="\n"):
    timeToStr = lambda t: f"{int(t//60):02}:{int(t%60):02}"
    it = it if hasattr(it, '__len__') else list(it)
    count, start = len(it), time()
    if count == 0: return []
    def show(j):
        prec, x, t = round(100*j/count), bar_size*j/count, time()-start
        bar = (u'█'*int(x))+(u' ▏▎▍▌▋▊█'[int(8*x)%8])+(' '*(bar_size-int(x)-1))
        bar = bar if j < count else bar[:-1]
        t_curr, t_total = timeToStr(t), timeToStr(count*t/j)
        print(f"{prefix} {prec:>3}%|{bar}| {j:>{len(str(count))}}/{count} [{t_curr}<{t_total}]", end='\r', flush=True)
    show(0.1)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print(end_print, end="", flush=True)
