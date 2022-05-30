from owlready2 import *

onto_path.append(".\TagSys.owl")
#TagSys_onto = get_ontology("https://github.com/Ranixculiva/TagSysOntology/blob/main/TagSys.owl")
#TagSys_onto = get_ontology("http://github.com/Ranixculiva/TagSysOntology/blob/main/TagSys.owl")
import os
dir = os.path.dirname(__file__)

TagSys_onto = get_ontology("file://"+ dir +"//TagSys.owl")
TagSys_onto.load()


from collections.abc import Iterable
with TagSys_onto:
    class updated(TagSys_onto.GenBlock >> bool,FunctionalProperty):
        pass
    class deleted(TagSys_onto.GenBlock >> bool,FunctionalProperty):
        pass
    class GenBlock(Thing):
        def __lshift__(self, tag):
            self.updated = False
            if isinstance(tag, Iterable):
                self.hasTag = list(set(self.hasTag).union(set(tag)))
            else:
                s = set(self.hasTag)
                s.add(tag)
                self.hasTag = list(s)
        def __rshift__(self, tag):
            self.updated = False
            if isinstance(tag, Iterable):
                self.hasTag = list(set(self.hasTag).difference(set(tag)))
            else:
                s = set(self.hasTag)
                s.remove(tag)
                self.hasTag = list(s)
        def __iadd__(self, gen_block):
            self.connect(gen_block)
            return self

    class Block(Thing):
        def connect(self, portBlock):
            if TagSys_onto.PortBlock not in portBlock.is_a: return
            self.hasPort.append(portBlock) 
            portBlock.isPortOf= [self]
        def update_candidates(self):
            s = set(TagSys_onto.ComponentLibrary.instances())
            for t in self.hasTag:
                s = s.intersection(set(t.instances()))
            self.hasCandidate = list(s)
            self.updated = True
            for port in self.hasPort:
                port.update_candidates()
            

    class PortBlock(Thing):
        def update_candidates(self):
            s = set()
            for c in self.isPortOf[0].hasCandidate:
                s = s.union(set(c.hasPort))
            for t in self.hasTag:
                s = s.intersection(set(t.instances()))
            self.hasCandidate = list(s)
            self.updated = True
            if self.connectFrom:
                self += self.connectFrom[0]
                self.connectFrom[0].update_candidates()
        def connect(self,genBlock):
            if TagSys_onto.Block in genBlock.is_a:
                genBlock.hasPort.append(self) 
                self.isPortOf= [genBlock]
            elif TagSys_onto.SlotBlock in genBlock.is_a:
                result = set()
                for candidate in self.hasCandidate:
                    result = result.union(set(candidate.hasTag[0].match.is_a))
                genBlock.hasSysTag = list(result)
                genBlock.connectTo = [self]
                self.connectFrom = [genBlock]

    from itertools import permutations
    class SlotBlock(Thing):
        
        def connect(self, linkBlock):
            if TagSys_onto.LinkBlock not in linkBlock.is_a: return
            self.isSlotOf = [linkBlock]
            linkBlock.hasSlot.append(self)
        def update_candidates(self):
            # we suppose otherSlotBlocks[i].hasCandidate's are correct
            # the result will be the intersection of the candidates filtered by hasSysTag and by hasTag
            # the candidates without filter
            base_result = set()
            if len(self.isSlotOf) == 1:
                linkBlock = self.isSlotOf[0]
                otherSlotBlocks = set(linkBlock.hasSlot)
                otherSlotBlocks.remove(self)
                otherSlotBlocks = list(otherSlotBlocks)
                for linkComp in linkBlock.hasCandidate:
                    for product in permutations(linkComp.hasSlot,len(otherSlotBlocks)):
                        for i in range(len(otherSlotBlocks)):
                            if product[i] not in otherSlotBlocks[i].hasCandidate:
                                break
                        else:
                            diff = set(linkComp.hasSlot).difference(set(product))
                            base_result=base_result.union(diff)
                            # actually it can be much faster if we consider user_result and run less permutation loop 
            else:
                  base_result = set(TagSys_onto.SlotComponentLibrary.instances())

            list_set_to_intersect = [set(tag.instances()) for tag in self.hasTag]
            user_result = base_result
            if list_set_to_intersect:
                user_result = base_result.intersection(*list_set_to_intersect)
            
            # the candidates filtered by hasSysTag
            sys_result = set()
            for t in self.hasSysTag:
                sys_result = sys_result.union(set(t.instances()))
            if self.connectTo:
                result = sys_result.intersection(user_result)
            else:
                result = user_result
            self.hasCandidate = list(result)
            #update link 

            self.updated = True

            if len(self.isSlotOf) == 1:
                self.isSlotOf[0].update_candidates()

        #def connect(self,slot):
        #    if slot is TagSys_onto.SlotBlock:
        #        s = set()
        #        for c in b1p1.hasCandidate:
        #            s = s.union(set(c.hasTag[0].match.is_a))
        #        slot.hasTag.extend(s)
    class LinkBlock(Thing):
        def connect(self, slotBlock):
            if TagSys_onto.SlotBlock not in slotBlock.is_a: return
            self.hasSlot.append(slotBlock)
            slotBlock.isSlotOf = [self]
        def update_candidates(self):
            #TODO: check slot count
            #intersection of corresponding linkComps respect to each slot. 
            
            setOfLinkComps = set(TagSys_onto.LinkComponentLibrary.instances())
            for slot in self.hasSlot:
                linkComps = set()
                for slotComp in slot.hasCandidate:
                    linkComps=linkComps.union(set(slotComp.isSlotOf))
                
                setOfLinkComps.intersection_update(linkComps)
            
            for tag in self.hasTag:
                setOfLinkComps = setOfLinkComps.intersection(set(tag.instances()))
            self.hasCandidate = list(setOfLinkComps)
            
            self.updated = True
            
            for slot in self.hasSlot:
                if not slot.updated:
                    slot.update_candidates()






sync_reasoner_pellet(infer_property_values=True, debug=0)