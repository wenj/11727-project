import os
import json


isProperties = ['given name', 'family name', 'occupation', 'equivalent class', 'said to be the same as', 'official name', 'short name', 'nickname', 'Twitter username',
				'GitHub username']
relatedProperty = ['instance of', 'member of', 'subclass of', 'part of', 'country', 'shares border with', 'located in the administrative territorial entity',
				   'office held by head of government', 'head of state']
# ignoreProperty = ['located in time zone', 'GeoNames ID', 'VIAF ID', 'image']

class Node:
	def __init__(self, name):
		self.name = name
		self.mentions = []
		self.edges = {}
		self.attributes = []

	def addAttribute(self, attr):
		self.attributes.append(attr)

	def addNode(self, edge, data_list):
		self.edges[edge] = []
		for data in data_list:
			if isinstance(data, str):
				node = Node(data)
			elif isinstance(data, dict) and 'title' in data:
				node = Node(data['title'])
				if 'attributes' not in data:
					return
				attributes = data['attributes']
				for attribute in attributes:
					if attribute in isProperties:
						for item in attributes[attribute]:
							if isinstance(item, dict):
								if 'title' in item:
									node.addAttribute(item['title'])
								elif 'text' in item:
									node.addAttribute(item['text'])
							else:
								node.addAttribute(item)
					else:
						node.addNode(attribute, attributes[attribute])
						if attribute not in relatedProperty:
							relatedProperty.append(attribute)
							try:
								print('\'{}\' has been appended to related list'.format(attribute))
							except:
								pass
			else:
				continue
			self.edges[edge].append(node)

	def addMention(self, mention):
		self.mentions.append(mention)

	def addMentions(self, mentions):
		self.mentions.extend(mentions)

	def removeMention(self, mention):
		for idx, item in enumerate(self.mentions):
			if item['startIndex'] == mention['startIndex'] and item['endIndex'] == mention['endIndex'] and item['sentNum'] == mention['sentNum']:
				self.mentions.pop(idx)
				break

	def print(self, indent=''):
		print(indent + 'Name: {}'.format(self.name))
		print(indent + 'Attributes: {}'.format(self.attributes))
		print(indent + 'Edges:')
		for edge in self.edges:
			for item in self.edges[edge]:
				print(indent + '==> {}'.format(edge))
				item.print(indent=indent + '\t')
		print(indent)

def build_graph(filename):
	with open(os.path.join('tree', filename)) as f:
		data = json.load(f)

	graph = Node(data['title'])
	attributes = data['attributes']
	for attribute in attributes:
		if attribute in isProperties:
			for item in attributes[attribute]:
				if isinstance(item, dict):
					if 'title' in item:
						graph.addAttribute(item['title'])
					elif 'text' in item:
						graph.addAttribute(item['text'])
				else:
					graph.addAttribute(item)
		else:
			graph.addNode(attribute, attributes[attribute])
			if attribute not in relatedProperty:
				relatedProperty.append(attribute)
				try:
					print('\'{}\' has been appended to related list'.format(attribute))
				except:
					pass
	return graph
