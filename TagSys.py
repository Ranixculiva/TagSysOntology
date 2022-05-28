from owlready2 import *
onto_path.append(".\TagSys.owl")
TagSys_onto = get_ontology("https://github.com/Ranixculiva/TagSysOntology/blob/main/TagSys.owl")


with TagSys_onto:
    class GenBlock(Thing):
        def tag_filter(self):
            print("tag_filter")