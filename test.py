from owlready2 import *
onto_path.append(".\TagSys.owl")
TagSys_onto = get_ontology("https://github.com/Ranixculiva/TagSysOntology/blob/main/TagSys.owl")
TagSys_onto.load()


test_block = TagSys_onto.Block()
test_block.hasTag = [TagSys_onto.NotebookTag()]

sync_reasoner()
test_block.tag_filter()