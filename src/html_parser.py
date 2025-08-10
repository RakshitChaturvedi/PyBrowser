class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = [] # text nodes dont have children, but kept for consistency
        self.parent = parent
        self.style = {}
        self.is_focused = False

    def __repr__(self):
        return repr(self.text)

class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag                  # tag name, e.g., "div", "body", "html" etc
        self.attributes = attributes    # dictionary of html attributes
        self.children = []              # list of children, element or text
        self.parent = parent            # pointer to parent element
        self.style = {}
        self.is_focused = False

    def __repr__(self):
        return "<" + self.tag + ">"

def print_tree(node, indent=0):
    print(" " * indent, node)           # print the current node with indentation
    for child in node.children:
        print_tree(child, indent+2)     # recursively print children, more indented

class HTMLParser:
    SELF_CLOSING_TAGS = [
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
    ]
    HEAD_TAGS = [
        "base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script",
    ]

    def __init__(self, body):
        self.body = body                # raw html as string
        self.unfinished = []            # stack of open (unfinished) elements

    # seperates tags from text
    def parse(self):
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                if text: self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += c
        if not in_tag and text:
            self.add_text(text)
        return self.finish()
    """
    Example input = <html><body>Hello World!</body></html>
    char        in_tag      action
     <          True        add_text() --> clean text to ""
     >          False       add_tag() --> clean text to ""
     other      False       add to text
    """

    # Seperate tag name from attribute
    def get_attributes(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}

        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                if len(value) > 2 and value[0] in ["'", "/"]:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else: 
                attributes[attrpair.casefold()] = ""
        return tag, attributes
    """
    Example input: <a href="https://example.org" target="_blank">
    tag = 'a'
    attributes = {
        'href': 'https://example.org',
        'target': '_blank'
    }
    """
    
    def add_text(self, text):
        if text.isspace(): return
        self.implicit_tags(None)        # ensure basic doc structure

        parent = self.unfinished[-1]    # parent is most recent unfinished tag
        node = Text(text, parent)       # create new Text node instance with reference to its parent element
        parent.children.append(node)    # append the current children to parent's list of children

    def add_tag (self, tag):
        tag, attributes = self.get_attributes(tag)  # seperate tag name from its attributes
        if tag.startswith("!"): return              # to ignore comments (<!-- -->) or doctype (<!DOCTYPE>) tags
        self.implicit_tags(tag)                     # ensure basic doc structure

        # Close tag finishes the last unfinished node by adding it to the prev unfinished node in list
        if tag.startswith("/"): 
            if len(self.unfinished) == 1: return    # to prevent stack overflow / malformed tree, as its likely root node
            node = self.unfinished.pop()            # pop most recent unfinished tag as node
            parent = self.unfinished[-1]            # the new last item in unfinished tags is current node's parent
            parent.children.append(node)            # add current node to the list of children of it's parent

        # Handle self closing tags (e.g., <br>, <hr>, <img>)
        elif tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]                # current tag's parent is the recent-most unfinished tag    
            node = Element(tag, attributes, parent)     # create a new Element node instance with reference to its attributes and parent
            parent.children.append(node)                # add current node to it's parents list of children

        # Open tags adds an unfinished node to the end of the list
        else:   
            parent = self.unfinished[-1] if self.unfinished else None   # current tag's parent is recent-most unfinished tag if unfinished tag exists, 
            node = Element(tag, attributes, parent)                     # create new Element node instance with reference to its attributes and parent
            self.unfinished.append(node)                                # add it to unfinished tags list

    # Ensures minimal basic HTML structure exists in document.
    def implicit_tags(self, tag): 
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] and tag not in ["head", "body", "/html"]:
                if tag in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html", "head"] and tag not in ["/head"] + self.HEAD_TAGS:
                self.add_tag("/head")
            else:
                break

    def finish(self):
        # if there are no unfinished tag, check for minimal html structure 
        if not self.unfinished:
            self.implicit_tags(None)

        # if there are unfinished tags (except root node), finish them.
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        
        # return top level root node
        return self.unfinished.pop()
    