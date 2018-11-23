from user import User

class Tracker_Users:
    """Just now to simplify the architecture"""

    def __init__(self, user_list=[]):
        self.user_list = user_list
        self.user_counter = 0 # not very useful since len(user_list should return the same but may be used for tests)

    def tracks_to_users(self, tracks):
        #TODO look for optimization
        found = False
        for track in tracks:
            for user in self.user_list:
                if track.track_id == user.track.track_id:
                    found = True
                    break
            if found == False: # new track -> new person
                #TODO look for finding the name and the user index -> first seen ?
                #TODO -> find user in the database (badge simulation)
                self.user_list.append(User("new_name", track, index=0, ))
                self.user_counter += 1
            found = False
