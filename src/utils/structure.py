# class Person:
#     def __init__(self, name, box, image):
#         self.name = name
#         self.box = box
#         self.image = image

class Person:
    def __init__(self, name, box, histo):
        self.name = name
        self.box = box
        self.histo = histo



class Frame :
    def __init__(self,dico={}):
        self.dico = dico
    def add_person(person):
        dico[person.name]=person.box
    def get_box_person(person):
        return dico[person.name]



class Person_v2:
    def __init__(self, name, box, rgbHist=[],index=0):
        self.name = name
        self.box = box
        self.rgbHist = rgbHist
        self.index=index
