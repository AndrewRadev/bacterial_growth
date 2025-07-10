import csv


def filter_unicellular(metdb_dump):
    """
    Adapted from an awk script by Savvas Paragkamian
    """
    selection = set()

    ## Bacteria and Archaea
    selection.add(2)      # tax id 2 stands for Bacteria
    selection.add(2157)   # tax id 2157 stands for Archea

    ## Unicellular Eukaryotes

    ## From supergroup Excavata

    selection.add(5719)      # tax id 5719 stands for phylum Parabasalia
    selection.add(5738)      # tax id 5738 stands for order Diplomonadida
    selection.add(66288)     # tax id 66288 stands for order Oxymonadida
    selection.add(193075)    # tax id 193075 stands for family Retortamonadidae
    selection.add(2611341)   # tax id 2611341 stands for clade Metamonada
    selection.add(207245)    # tax id 207245 stands for plylum Fornicata
    selection.add(136087)    # tax id 136087 stands for family Malawimonadidae
    selection.add(85705)     # tax id 85705 stands for family Ancyromonadidae
    selection.add(1294546)   # tax id 1294546 stands for family Planomonadidae

    ### From supergroup Excavata, clade Discoba (Discristates)
    selection.add(33682)     # tax id 2157 stands for phylum Euglenozoa
    selection.add(5752)      # tax id 5752 stands for phylum Heterolobosea (includes Percolomonadidae)
    selection.add(556282)    # tax id 556282 stands for order Jakobida
    selection.add(2711297)   # tax id 2711297 stands for order Tsukubamonadida

    ## From supergroup Archaeplastida

    selection.add(38254)   # tax id 38254 stands for class Glaucocystophyceae

    ### Rhodophycea, red algae
    selection.add(265318)   # tax id 265318 stands for order Cyanidiales
    selection.add(2798)     # tax id 2798 stands for order Porphyridiales
    selection.add(661027)   # tax id 661027 stands for class Rhodellophyceae
    selection.add(446134)   # tax id 446134 stands for class Stylonematophyceae

    ## From Chloroplastida / Viridiplantae
    selection.add(3166)      # tax id 3166 stands for class Chloropphyceae
    selection.add(2201463)   # tax id 2201463 stands for class Palmophyllophyceae, synonym of Prasinophyceae

    ## From Chromalveolata

    ### Alveolata

    selection.add(2864)   # tax id 2864 stands for class Dinophyceae
    selection.add(5794)   # tax id 5794 stands for class Apicomplexa
    selection.add(5878)   # tax id 5878 stands for phylum Ciliophora

    ### Stramenopiles

    selection.add(238765)   # tax id 238765 stands for class Actinophryidae
    selection.add(33849)    # tax id 33849 stands for class Bacillariophyceae
    selection.add(35131)    # tax id 35131 stands for class Labyrinthulomycetes
    selection.add(33651)    # tax id 33651 stands for order Bicosoecida

    ### Chromobionta
    selection.add(2833)     # tax id 2833 stands for class Xanthophyceae
    selection.add(38410)    # tax id 38410 stands for class Raphidophyceae
    selection.add(157124)   # tax id 157124 stands for class Pinguiophyceae
    selection.add(33849)    # tax id 33849 stands for class Bacillariophyceae
    selection.add(589449)   # tax id 589449 stands for class Mediophyceae
    selection.add(33836)    # tax id 33836 stands for class Coscinodiscophyceae
    selection.add(91989)    # tax id 91989 stands for class Bolidophyceae
    selection.add(35675)    # tax id 35675 stands for class Pelagophyceae
    selection.add(2825)     # tax id 2825 stands for class Chrysophyceae
    selection.add(33859)    # tax id 33859 stands for class Synurophyceae
    selection.add(557229)   # tax id 557229 stands for class Synchromophyceae
    selection.add(39119)    # tax id 39119 stands for class Dictyochophyceae

    ### Haptophyta
    selection.add(2830)   # tax id 2830 stands for class Haptophyta

    ## Unikonts

    ### Opistrhokonta

    selection.add(127916)   # tax id 127916 stands for class Ichthyosporea (Mesomycetozoa)
    selection.add(6029)     # tax id 6029 stands for class Microsporidia (unicellular Fungi)
    selection.add(4890)     # tax id 4890 stands for phylum Ascomycota (they contain some multicellular)
    selection.add(28009)    # tax id 28009 stands for class Choanoflagellata

    ### Amoebozoa

    selection.add(555369)   # tax id 555369 stands for phylum Tubulinea (Lobosea)
    selection.add(555406)   # tax id 555406 stands for clade Archamoebae
    selection.add(142796)   # tax id 142796 stands for class Mycetozoa (Eumycetozoa, they contain some multicellular)

    ## Cryptobionta

    selection.add(3027)     # tax id 3027 stands for class Cryptophyceae
    selection.add(339960)   # tax id 339960 stands for order Kathablepharidacea
    selection.add(419944)   # tax id 419944 stands for phylum Picozoa

    ## Rhizaria

    selection.add(543769)   # tax id 543769 stands for clade Rhizaria

    with open(metdb_dump) as f:
        reader = csv.DictReader(f)

        for row in reader:
            selection.add(int(row['NCBI ID']))

    return selection
