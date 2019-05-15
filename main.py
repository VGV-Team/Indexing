from InvertedIndex import InvertedIndex

if __name__ == "__main__":
    ii = InvertedIndex(fresh=False)
    #ii.query("Sistem SPOT")
    ii.query("predelovalne dejavnosti")
    ii.query("trgovina")
    ii.query("social services")

