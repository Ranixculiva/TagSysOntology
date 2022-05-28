from owlready2 import *
onto_path.append(".\TagSys.py")
TagSys_onto = get_ontology("http://www.semanticweb.org/john2/ontologies/2022/4/TagSys")
TagSys_onto.load()


test_block = TagSys_onto.Block()
test_block.hasTag = [TagSys_onto.NotebookTag()]

sync_reasoner()
test_block.tag_filter()