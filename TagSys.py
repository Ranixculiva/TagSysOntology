from owlready2 import *
onto_path.append(".\TagSys.py")
TagSys_onto = get_ontology("http://www.semanticweb.org/john2/ontologies/2022/4/TagSys")


with TagSys_onto:
    class GenBlock(Thing):
        def tag_filter(self):
            print("tag_filter")