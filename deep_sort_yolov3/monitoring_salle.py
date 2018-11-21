class Machine:
    def __init__(self, name, boxMachine=[]):
        self.name = name
        self.box = boxMachine
        self.totalUsedTime = 0
        self.currentUsedTime = {}
        self.isUsed = False

    def updateTime(self, machineUsed, userName):
        # print("machineUsed",machineUsed)
        if machineUsed:
            if userName in self.currentUsedTime.keys():
                self.currentUsedTime[userName] += 1
            else :
                self.currentUsedTime[userName] = 1
            print(userName,self.currentUsedTime[userName])
        else :
            if userName in self.currentUsedTime.keys():
                self.currentUsedTime.pop(userName)


    def isMachineUsed(self):
        b=self.isUsed
        self.isUsed=False
        for k,v in self.currentUsedTime.items():
            if v > 5 :
                if b==False :
                    self.totalUsedTime+=v
                else :
                    self.totalUsedTime+=1
                self.isUsed = True

def updateTimeMachine(person, machines):
    #TODO compare using positions -> do not compare to all machines (-> ordered)
    #TODO change way of changing machines states
    updatedMachines = []
    for machine in machines:
        intersection = bb_intersection(person.box, machine.box)
        print("Intersection : ", intersection)
        if intersection > 0.5 :
            machine.updateTime(True,person.name)
        else:
            machine.updateTime(False,person.name)
        # print("machine : ", machine.name, machine.currentUsedTime)
        updatedMachines.append(machine)
    return updatedMachines

def updateTimeMachine_tracks(track, machines):
    #TODO compare using positions -> do not compare to all machines (-> ordered)
    #TODO change way of changing machines states
    updatedMachines = []
    for machine in machines:
        intersection = bb_intersection(track.to_tlbr(), machine.box)
        print("Intersection : ", intersection)
        if intersection > 0.5 and track.time_since_update <= 2 and track.is_confirmed():
            machine.updateTime(True,track.track_id)
        else:
            machine.updateTime(False,track.track_id)
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

def bb_intersection(boxA, boxB):
	# determine the (x, y)-coordinates of the intersection rectangle
	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[2], boxB[2])
	yB = min(boxA[3], boxB[3])

	# compute the area of intersection rectangle
	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

	# compute the area of both the prediction and ground-truth
	# rectangles
	boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
	# print(xA,yA,xB,yB)
	# print("interArea :",interArea)
	# print("boxAArea :",boxAArea)

	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
	iou = interArea / float(boxAArea )
	# return the intersection over union value
	return iou
