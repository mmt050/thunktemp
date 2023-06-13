# This is a sample Python script.
import argparse
import logging
import os
import signal
import traceback
from datetime import datetime
from statistics import median
from time import sleep

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
refresh_thread_shared = dict(graceful_stop=False)

measurements = dict()

def main(inputs:list, period_s:int, keep_cnt:int, outfile:str):
        period_cnt = 0
        outfile_tmp = outfile + ".tmp"
        while True:
            if refresh_thread_shared['graceful_stop'] == True:
                log.info("Received graceful stop signal, exiting...")
                break
            try:
                highest_input_val = 0
                for input in inputs:
                    with open(input, 'r') as f:
                        value = int(f.read().strip())/1000
                        log.debug(f"read: input={input}, value={value}")
                        # append time-stamped measurement to measurements and write running average to file and trim measurements to last 60 seconds
                        measurements[input] = measurements.get(input, []) + [value]
                        measurements[input] = measurements[input][-keep_cnt:]
                        #value = sum([v for t, v in measurements[input]])/len(measurements[input])
                        value = median(measurements[input])
                        if value > highest_input_val:
                            highest_input_val = value
                        log.debug(f"avg: input={input}, value={value}")
                with open(outfile_tmp, 'w') as out:
                    out.write(f"{int(highest_input_val)*1000}\n")
                    out.flush()
                os.rename(outfile_tmp, outfile)
                sleep(period_s)
                period_cnt += 1
                # every 10 seconds in datetime log current value
                if period_cnt % 10 == 0:
                    log.info(f"current value: {measurements}, highest_input_val={highest_input_val}")
            except Exception as e:
                log.error(f"Error while processing: {e}")
                log.error(traceback.format_exc())
                return


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs='+', dest='inputs', required=True, default=None, help="Inputs with path /sys/bus/platform/devices/thinkpad_hwmon/hwmon/hwmon7/ ")
    parser.add_argument("--period", type=int, dest='period_s', required=False, default=2, help=" ")
    parser.add_argument("--keep-cnt", type=int, dest='keep_cnt', required=False, default=10, help=" ")
    parser.add_argument("--output", type=str, dest='outfile', required=True, default=None, help="outfile path")
    parser.add_argument("--app-loglevel", type=str, dest='app_loglevel', required=False, default="INFO", help=" ")
    args = parser.parse_args()

    app_loglevel = os.environ.get("APP_LOGLEVEL", args.app_loglevel)
    root_loglevel = os.environ.get("LOGLEVEL", "WARNING")
    logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(levelname)s-%(name)s@%(lineno)d %(message)s")
    logging.getLogger('app').setLevel(logging.getLevelName(app_loglevel))
    log = logging.getLogger('app')

    # log all arguments
    log.info(f"args={args}")

    base = '/sys/bus/platform/devices/thinkpad_hwmon/hwmon/'
    base_hwmon = [base + f for f in os.listdir(base) if f.startswith('hwmon')][0]

    log.info(f"base_hwmon={base_hwmon}")

    def sig(signum, frame):
        log = logging.getLogger("app.qInfo.signal_handler")
        log.info(f"Received signal {signum}, stopping refresh thread...")
        refresh_thread_shared['graceful_stop'] = True


    signal.signal(signal.SIGQUIT, sig)
    signal.signal(signal.SIGTERM, sig)

    main([base_hwmon+"/"+f for f in args.inputs], args.period_s, args.keep_cnt, args.outfile)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
