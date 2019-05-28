from InvertedIndex import InvertedIndex

if __name__ == "__main__":
    ii = InvertedIndex(fresh=False)
    # ii.query("Sistem SPOT")
    ii.query("predelovalne dejavnosti", True)
    ii.query("trgovina", True)
    ii.query("social services", True)

    ii.query("predelovalne dejavnosti", False)
    ii.query("trgovina", False)
    ii.query("social services", False)
