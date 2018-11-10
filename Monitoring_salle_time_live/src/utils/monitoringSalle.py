


from .utils import bb_intersection

def updateTimeMachine(out_classes,out_boxes, machines):
    updatedMachines = []
    for machine in machines:
        boolean=False

        for i, c in reversed(list(enumerate(out_classes))):
            if c==0 :
                intersection = bb_intersection(out_boxes[i], machine.box)
                # print("Intersection : ", intersection)
                if intersection > 0.75 :
                    boolean=True
                    break;
        machine.updateTime(boolean,"Tom")
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
        # print("currentUsedTime : ", machine.currentUsedTime)
