# StellaTree v0.1.0

import textwrap
import importlib
import glob
import os
import re


def MakeRegExp(r):
    import re

    def RegExp(s):
        if re.fullmatch(r, s) is None:
            raise ValueError(s, "is not match RegExp", r)
        else:
            return s
    return RegExp


class StellaTree():
    def __init__(self, definition, rootDirectory="./"):
        self.Definition = definition
        self.RootDir = rootDirectory.replace("\\", "/")
        if(self.RootDir[-1] != "/"):
            self.RootDir += "/"

    def CheckNodes(self, nodes, R):
        try:
            node = None
            if(len(nodes) == 0):
                return True
            if(type(nodes).__name__ == "str"):
                node = nodes
            elif(type(nodes).__name__ == "list"):
                node = nodes[0]

            if(node[0] == "#" or node[0] == "&"):
                for regx in R:
                    if(type(regx).__name__ != "function"):
                        error = "Hey, this Node %s was something worng." % node
                        raise ValueError(error)
                    regx(node[1:])
                    return self.CheckNodes(nodes[1:], R[regx])
            elif(node[0] == "@"):
                ok = 0
                for pathName in R:
                    if(node == pathName):
                        ok += 1
                if(ok == 0):
                    error = "Hey, this Node %s was something worng." % node
                    raise ValueError(error)
                return self.CheckNodes(nodes[1:], R[node])
        except:
            import traceback
            traceback.print_exc()
            return False

    def CheckData(self, nodes, R, DATA):
        try:
            node = None
            if(len(nodes) == 0):
                return True, DATA
            if(len(nodes) == 1):
                for pathName in R:
                    for d in R[pathName]:
                        if(type(R[pathName][d]).__name__ == "function"):
                            DATA[d] = R[pathName][d](DATA[d])
            if(type(nodes).__name__ == "str"):
                node = nodes
            elif(type(nodes).__name__ == "list"):
                node = nodes[0]
            if(node[0] == "#" or node[0] == "&"):
                for regx in R:
                    if(type(regx).__name__ != "function"):
                        error = "Hey, this Node %s was something worng." % node
                        raise ValueError(error)
                    regx(node[1:])
                    return self.CheckData(nodes[1:], R[regx], DATA)
            elif(node[0] == "@"):
                ok = 0
                for pathName in R:
                    if(node == pathName):
                        ok += 1
                if(ok == 0):
                    error = "Hey, this Node %s was something worng." % node
                    raise ValueError(error)
                return self.CheckData(nodes[1:], R[node], DATA)
        except:
            import traceback
            traceback.print_exc()
            return False, DATA

    def BakeNode(self, line):
        if(self.CheckNodes(re.findall(r"[@#&][^@#&]*", line), self.Definition)):
            os.makedirs(self.GeneratePath(line), exist_ok=True)

    def GeneratePath(self, line):
        nodes = re.findall(r"[@#&/][^@#&/]*", line)
        indexNode = []
        for node in nodes:
            if(node[0] == "&"):
                indexNode += [x for x in node]
            elif(node[0] == "/"):
                indexNode += [node[1:]]
            else:
                indexNode += [node]
        return self.RootDir + "/".join(indexNode)

    def RevertLine(self, path):
        tmp = re.split(r"[/\\]", path.replace(self.RootDir, ""))
        return "".join(tmp[:-1]) + ";"

    def Find(self, line):
        if(line[-1] != ";"):
            line += ";"
        return [self.RevertLine(r) for r in glob.glob(self.GeneratePath(line.replace(";", "/__init__.py")), recursive=True)]

    def Glue(self, line, data, extend=None):
        TF, DATA = self.CheckData(
            re.findall(r"[@#&][^@#&]*", line), self.Definition, data
        )
        if(TF):
            f = open("/".join([self.GeneratePath(line), "__init__.py"]),
                     "w", encoding="utf-8")
            f.write("R=")
            if(type(data).__name__ == "str"):
                f.write('"%s"' % DATA)
            else:
                f.write(DATA.__str__())
            if(extend is not None):
                f.write("\n")
                f.write(textwrap.dedent(extend))
            f.close()

    def LoadData(self, line):
        nodes = re.findall(r"[@#&/][^@#&/]*", line.replace(";", ""))
        indexNode = []
        for node in nodes:
            if(node[0] == "&"):
                indexNode += [x for x in node]
            elif(node[0] == "/"):
                indexNode += [node[1:]]
            else:
                indexNode += [node]
        return importlib.import_module(".".join(indexNode))
