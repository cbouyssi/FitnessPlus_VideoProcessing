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
