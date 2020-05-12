import os
import json
from build_graph import build_graph
from functools import cmp_to_key

def equal(a, b):
	if len(a) != len(b):
		return False
	for i in range(len(a)):
		if a[i] != b[i]:
			return False
	return True

def sublist(a, b):
	if len(a) > len(b):
		return 0
	for i in range(len(b) - len(a) + 1):
		if equal(a, b[i:i + len(a)]):
			return len(a)
	return 0

def search_node(node, item):
	mention = item['mention'].lower().split(' ')
	startIndex = max(0, item['headIndex'] - item['startIndex'] - 1)
	endIndex = min(len(mention), item['headIndex'] - item['startIndex'] + 2)
	mention_sub = mention[startIndex:endIndex]

	best_node = None
	max_len = 0

	l = sublist(node.name.lower().split(' '), mention_sub)
	if l > max_len:
		best_node = node
		max_len = l
	for attr in node.attributes:
		l = sublist(attr.lower().split(' '), mention_sub)
		if l > max_len:
			max_len = l
			best_node = node
	for edge in node.edges:
		for child in node.edges[edge]:
			child_node, child_len = search_node(child, item)
			if child_len > max_len:
				best_node = child_node
				max_len = child_len
	return best_node, max_len

def collect_clusters(node):
	clusters = []
	assigned_node = []
	for edge in node.edges:
		for child in node.edges[edge]:
			child_clusters, child_assigned_node = collect_clusters(child)
			clusters.extend(child_clusters)
			assigned_node.extend(child_assigned_node)
	if len(node.mentions) > 0:
		clusters.append(node.mentions)
		assigned_node.append(node)
	return clusters, assigned_node		

def cmp(x, y):
	if x['sentNum'] != y['sentNum']:
		return x['sentNum'] < y['sentNum']
	if x['startIndex'] != y['startIndex']:
		return x['startIndex'] < y['startIndex']
	if x['endIndex'] != y['endIndex']:
		return x['endIndex'] < y['endIndex']


if not os.path.exists('results'):
	os.mkdir('results')

# filenames = ['Anatole France.json']
# filenames = ['Barack Obama.json']
vocab = ['his', 'her']
filenames = os.listdir('cluster')
filenames.remove('Canada.json')
for filename in filenames:
	print('File: {}'.format(filename))
	graph = build_graph(filename)

	with open(os.path.join('cluster', filename)) as f:
		clusters = json.load(f)

	clusters_not_assigned = []
	for cluster in clusters:
		cluster.sort(key=lambda x: (x['sentNum'], x['startIndex'], x['endIndex']))
		node = None
		for mention_idx, mention in enumerate(cluster):
			node_, max_len = search_node(graph, mention)
			if node_ is not None:
				if node is None:
					node_.addMentions(cluster[:mention_idx])
				node = node_
			if node is not None:
				node.addMention(mention)
		if node is None and len(cluster) > 1:
			clusters_not_assigned.append(cluster)

	clusters_assigned, assigned_node = collect_clusters(graph)
	for idx, cluster in enumerate(clusters_assigned):
		node = assigned_node[idx]
		for mention in cluster:
			if mention['mention'].lower() not in vocab:
				continue
			st = mention['startIndex']
			for mention2 in cluster:
				s = mention2['mention'].split(' ')
				if mention2['startIndex'] <= st and min(mention2['endIndex'], mention2['startIndex'] +len(s)) > st + 1:
					edge = s[st - mention2['startIndex'] + 1]
					if edge in node.edges:
						for new_node in node.edges[edge]:
							new_node.addMention(mention2)
						node.removeMention(mention2)
					
	clusters_assigned, _ = collect_clusters(graph)

	with open(os.path.join('results', filename), 'w') as f:
		json.dump(clusters_assigned + clusters_not_assigned, f, indent=4)
