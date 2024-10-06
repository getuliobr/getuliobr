from xml.dom import minidom

class SVGParser:
  def __init__(self, path):
    self.dom = minidom.parse('base.svg')
    for node in self.dom.getElementsByTagName("*"):
      if node.hasAttribute("id"):
        node.setIdAttribute("id")

  def __getElementById(self, id):
    return self.dom.getElementById(id)
  
  def update(self, id, value):
    node = self.__getElementById(id).firstChild
    node.data = value
  
  def write(self, path='out.svg'):
    with open(path, 'w+', encoding='utf-8') as f:
      self.dom.writexml(f, encoding='utf-8')