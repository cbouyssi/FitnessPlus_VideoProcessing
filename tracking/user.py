from activity import Activity

class User:

    def __init__(self, name, track, index=0):
        #TODO discuss about the track
        self.name = name # name to identity the person
        self.index = index # index in the gym database
        self.currentActivity = Activity("default")
        self.activities = {}
        self.track = track

    def updateActivity(self, activity_name):
        #TODO optimize with errors
        print("update activity :", activity_name)
        if activity_name in self.activities.keys():
            cur_set = max(self.activities[activity_name].sets.keys())
            if self.currentActivity.name == activity_name:
            # same set as before
                self.activities[activity_name].sets[cur_set] += 1
            else:
            # new set
                self.activities[activity_name].sets[cur_set+1] = 1
        else:
            self.activities[activity_name] = Activity(activity_name)
            self.activities[activity_name].sets[1] = 1
        self.currentActivity.name = activity_name
