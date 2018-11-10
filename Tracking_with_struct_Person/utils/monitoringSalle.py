


from src.utils.tracking_v2 import bb_intersection

def updateTimeMachine(person, machines):
    updatedMachines = []
    for machine in machines:
        intersection = bb_intersection(person.box, machine.box)
        print("Intersection : ", intersection)
        if intersection > 0.75 :
            machine.updateTime(True,person.name)
        else:
            machine.updateTime(False,person.name)
        # print("machine : ", machine.name, machine.currentUsedTime)
        updatedMachines.append(machine)
    return updatedMachines

def usedMachine(machines):
    updatedMachines = []
    for machine in machines:
        machine.isMachineUsed()
        updatedMachines.append(machine)
    return updatedMachines


def printMachineState(machines):
    for machine in machines:
        print("Machine : ", machine.name)
        print("Total used time : ", machine.totalUsedTime)
        print("Is machine used : ", machine.isUsed)
        print("currentUsedTime : ", machine.currentUsedTime)
