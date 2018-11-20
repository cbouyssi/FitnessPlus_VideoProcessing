


from src.utils.tracking_v2 import bb_intersection


def updateTimeMachine(person, machines):
    updatedMachines = []
    boolean=False
    for machine in machines:
        intersection = bb_intersection(person.box, machine.box)
        print("Intersection : ", intersection)
        if intersection > 0.75 :
            machine.updateTime(True,person.name)
            person.updateActivity(machine.name)
            boolean=True
        else:
            machine.updateTime(False,person.name)
        # print("machine : ", machine.name, machine.currentUsedTime)
        updatedMachines.append(machine)
    if boolean==False :
        person.updateActivity("nothing")

    print("VOICI LACTIVITE DE LA  PERSONNE : "+person.name, boolean)
    print(person.nothingActivity.name+":"+str(person.nothingActivity.time))
    for activity in person.listActivity :
        print(activity.name+":"+str(activity.time))

    print("\n\n\n")


    return updatedMachines,person

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
