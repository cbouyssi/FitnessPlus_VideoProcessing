


from src.utils.tracking_v2 import bb_intersection

def usedMachine(boxUser, machines):
    updatedMachines = []
    for machine in machines:
        intersection = bb_intersection(boxUser, machine.box)
        print("Intersection : ", intersection)
        if intersection > 0.75 :
            machine.updateTime(True)
        else:
            machine.updateTime(False)
        updatedMachines.append(machine)
    return updatedMachines

def printMachineState(machines):
    for machine in machines:
        print("Machine : ", machine.name)
        print("Total used time : ", machine.totalUsedTime)
        print("Is machine used : ", machine.isMachineUsed())
