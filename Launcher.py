from time import sleep
from Process import Process

def launch(nbProcess, runningTime=5):
    processes = []

    for i in range(nbProcess):
        processes = processes + [Process("P"+str(i),i, nbProcess)]

    sleep(runningTime)

    for p in processes:
        p.stop()

    for p in processes:
        p.waitStopped()

if __name__ == '__main__':

    #bus = EventBus.getInstance()
    
    launch(nbProcess=4, runningTime=1)

    #bus.stop()
