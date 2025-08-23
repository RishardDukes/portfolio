import argparse, asyncio, time
from contextlib import asynccontextmanager
from .storage import record
@asynccontextmanager
async def tcp_check(host, port=80, timeout=2.0):
    start=time.perf_counter()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host,port), timeout)
        elapsed=(time.perf_counter()-start)*1000
        try: yield True, elapsed
        finally: writer.close(); await writer.wait_closed()
    except Exception:
        yield False, None
async def check_once(host):
    async with tcp_check(host) as (ok, ms): record(host, ok, ms)
async def run_monitor(hosts, interval, cycles):
    i=0
    while cycles is None or i<cycles:
        await asyncio.gather(*(check_once(h) for h in hosts))
        await asyncio.sleep(interval); i+=1
def main():
    p=argparse.ArgumentParser(prog="ping_checker_2.monitor")
    p.add_argument("--hosts",nargs="+",required=True); p.add_argument("--interval",type=float,default=5.0)
    p.add_argument("--cycles",type=int,default=60); a=p.parse_args()
    asyncio.run(run_monitor(a.hosts,a.interval,a.cycles))
if __name__=="__main__": main()
