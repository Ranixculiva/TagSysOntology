from owlready2 import *
from TagSys import TagSys_onto

print("all classes: ",list(TagSys_onto.classes()),'\n')
print("tag classes: ",list(TagSys_onto.Tag.descendants()),'\n')
print("component library: ",list(TagSys_onto.ComponentLibrary.instances()),'\n')
print("port component library: ",list(TagSys_onto.PortComponentLibrary.instances()),'\n')
print("link component library: ",list(TagSys_onto.LinkComponentLibrary.instances()),'\n')
print("slot component library: ",list(TagSys_onto.SlotComponentLibrary.instances()),'\n')

print("tag library: ",list(TagSys_onto.Tag.instances()),'\n')



b1 = TagSys_onto.Block()
b1 << (TagSys_onto.NotebookTag, TagSys_onto.USBCTag)
b1.update_candidates()

b1p1 =  TagSys_onto.PortBlock()
b1+=b1p1
b1p1.update_candidates()


b2 = TagSys_onto.Block()
b2.update_candidates()

b2p1 =  TagSys_onto.PortBlock()
b2+=b2p1
b2p1.update_candidates()



sb1 = TagSys_onto.SlotBlock()
b1p1+=sb1
sb1.update_candidates()

sb2 = TagSys_onto.SlotBlock()
b2p1+=sb2
sb2.update_candidates()


lb1 = TagSys_onto.LinkBlock()
lb1+=sb1
lb1+=sb2
lb1.update_candidates()

print(f"b1{tuple(b1.hasTag)} has candidates: {b1.hasCandidate}")
print(f"b1.p1{tuple(b1p1.hasTag)} has candidates: {b1p1.hasCandidate}")
print(f"sb1{tuple(sb1.hasTag)} has candidates: {sb1.hasCandidate}")
print(f"lb1{tuple(lb1.hasTag)} has candidates: {lb1.hasCandidate}")
print(f"sb2{tuple(sb2.hasTag)} has candidates: {sb2.hasCandidate}")

