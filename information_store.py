import os
class InformationStore:
    def __init__(self):
        pass

    def store_info(self, info, timeframe=None, category=None):
        pass

    def retrieve_info(self, info=None, timeframe=None, category=None):
        pass

    def remove_info(self, info=None, timeframe=None, category=None):
        pass

class LocalFileInformationStore(InformationStore):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.remfile = path # MY LIST, MY PRECIOUS, MY PRECIOUS..... GOLLUM
        if not os.path.exists(self.remfile):
            remlist = open(self.remfile,"x")
            remlist.close()

    def store_info(self, info, timeframe=None, category=None):
        with open(self.remfile,"a") as remlist: # open file but only append don't overwrite
            filePhrase = info+"\n" # we want newlines
            remlist.write(filePhrase) # write to file

    def retrieve_info(self, info=None, timeframe=None, category=None):
        alist = []
        try:
            with open(self.remfile,"r") as remlist: # open file readonly
                rememberphrases = remlist.read() # read file
                alist = rememberphrases.split("\n") # split line by line and make a nice list
        except:
            return []
        if info == None:
            return alist
        else:
            return [p for p in alist if info in p]

    def remove_info(self, info=None, timeframe=None, category=None):
        if info is None and timeframe is None and category is None:
            with open(self.remfile,"w") as remlist:
                remlist.write("") # overwrite with nothing
            return
        elif info is not None:
            with open(self.remfile,"r") as remlist: # open file readonly
                rememberphrases = remlist.read() # read file
                alist = rememberphrases.split("\n") # split line by line and make a nice list
            rlist = [p for p in alist if not (info in p)]
            with open(self.remfile,"w") as remlist:
                remlist.write("\n".join(rlist))
            return
