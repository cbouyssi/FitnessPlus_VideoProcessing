from machine import Machine
from user import User

def update_machine_and_activities(user, machines):
    #TODO compare using positions -> do not compare to all machines (-> ordered)
    #TODO change way of changing machines states
    updatedMachines = []
    boolean=False
    for machine in machines:
        intersection = bb_intersection(user.track.to_tlbr(), machine.box)
        print("Intersection : ", intersection)
        if intersection > 0.5 and user.track.time_since_update <= 2 and user.track.is_confirmed():
            machine.updateTime(True, user.track.track_id)
            user.updateActivity(machine.name)
            boolean=True
        else:
            machine.updateTime(False, user.track.track_id)
        # print("machine : ", machine.name, machine.currentUsedTime)
        updatedMachines.append(machine)
    if boolean==False :
        user.updateActivity("nothing")

    print("VOICI LACTIVITE DE LA  PERSONNE : "+user.name, boolean)
    for activity_name, activity in user.activities.items() :
        print(activity_name)
        for set_num, set_time in activity.sets.items():
            print("Set "+str(set_num)+" Time "+str(set_time))
    print("\n\n\n")

    return updatedMachines, user


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
