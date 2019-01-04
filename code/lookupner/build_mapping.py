import json

tags = ['person', 'facility', 'event', 'language', 'loc', 'organization', 'product', 'work']
directory = 'resources'

def build_mappings():
  mappings = {}
  for tag in tags:
    filename = directory + '/' + tag + '.txt'
    lines = open(filename, 'r').readlines()
    subclasses = []
    for line in lines:
      line = line.rstrip()
      words = line.split('/')
      subclass = words[-1].rstrip().lower()
      subclasses.append(subclass)

    mappings[tag] = subclasses

  return mappings


def main():
  mappings = build_mappings()
  print(json.dumps(mappings, indent=4, sort_keys=True))

if __name__ == '__main__':
  main()

