#!/usr/bin/python3
import sys, os
import re
import glob
import shutil
import json

PREAMBLE = """/* MEOW */
import olympiad;
import cse5;

size(500);
dotfactor *= 2;
defaultpen(fontsize(18pt));

"""

TMP = "/tmp/guessr/"

def createDiagram(dir_name, file_name, ext):
	filesrc = "asy-sources/" + dir_name + '/' + file_name + "." + ext
	filepdf = "diagrams/" + file_name + ".pdf"
	filepng = "diagrams/" + file_name + ".png"
	filetmp = TMP + file_name + ".tmp"
	filetmpasy = TMP + file_name + ".tmpasy"
	filenewasy = TMP + file_name + ".asy"
	filejson = "diagrams/" + file_name + ".json"

	# If already created and older, skip it
	if os.path.isfile(filejson):
		if os.path.getmtime(filejson) > os.path.getmtime(filesrc) \
				and os.path.getmtime(filejson) > os.path.getmtime(sys.argv[0]):
			return 0

	if ext == "asy":
		fileoldasy = filesrc
	elif ext == "txt":
		# I'm sorry! Evan's dotfiles are on Github, so...
		os.system("cat %s | python2 ~/dotfiles/py-scripts/tsq.py > %s" %(filesrc, filetmpasy))
		fileoldasy = filetmpasy
	else:
		print("WARNING: ignoring unknown %s" %filesrc)
		return -1 # I don't know how to deal with this!

	orig_asy_content = ""
	# Reset variables
	source = ""
	text = ""
	pts_list = []
	item_list = []
	with open(fileoldasy, "r") as r:
		pts_list = []
		item_list = []
		for line in r:
			orig_asy_content += line
			line = line.strip()
			if line.startswith('Source:'):
				source = line[7:].strip()
			elif line.startswith('Points:'):
				line = line[7:].strip()
				pts_list = line.split()
			elif line.startswith('Item:'):
				line = line[5:].strip()
				item_list.append(line.split())
			elif line.startswith('Text:'):
				line = line[5:].strip()
				text += line + '<br>'
		text = text.strip()
		text = json.dumps(text)

	with open(filenewasy, 'w') as w:
		print(PREAMBLE, file=w)
		print(orig_asy_content, file=w)
		for pt in pts_list:
			print("write(\"Point: %s,\" + (string) %s);" %(pt, pt), file=w)
		print("write(\"umin \" + (string) min(currentpicture, user=true));", file=w) # User coordinates
		print("write(\"umax \" + (string) max(currentpicture, user=true));", file=w)
		print("write(\"pmin \" + (string) min(currentpicture, user=false));", file=w) # PS coordinates
		print("write(\"pmax \" + (string) max(currentpicture, user=false));", file=w)
	command = "asy -f pdf -o %s %s > %s;\nconvert %s %s" \
			%(filepdf, filenewasy, filetmp, filepdf, filepng)
	print(command)
	os.system(command)

	#reading tmp file from asymptote
	pts_coor = []
	min_list = []
	max_list = []
	with open(filetmp, "r") as r:
		for line in r:
			if line.startswith('Point: '):
				line = line[7:].strip()
				pts_coor.append(line.split(","))
			elif line.startswith('umin '):
				min_list = line[4:].strip().split(",")
			elif line.startswith('umax '):
				max_list = line[4:].strip().split(",")
			elif line.startswith('pmin '):
				pmin_list = line[4:].strip().split(",")
				pxmin = float(pmin_list[0][1:])
				pymin = float(pmin_list[1][:-1])
			elif line.startswith('pmax '):
				pmax_list = line[4:].strip().split(",")
				pxmax = float(pmax_list[0][1:])
				pymax = float(pmax_list[1][:-1])

	#writing json file
	g = open(filejson, 'w')
	g.write('{\n')
	g.write('"points" : [\n')
	print(',\n'.join([ '["%s", %s, %s]' %(pt[0], pt[1][1:], pt[2][:-1]) for pt in pts_coor ]), file=g)
	print('],', file=g)

	print('"min" : [%s,%s],' %(min_list[0][1:], min_list[1][:-1]), file=g)
	print('"max" : [%s,%s],' %(max_list[0][1:], max_list[1][:-1]), file=g)

	print('"items" : [', file=g)
	print(',\n'.join([ '['+','.join(['"%s"' %p for p in ls])+']' for ls in item_list ]), file=g)
	print('],', file=g)

	print('"source" : "%s",' %(source), file=g)
	print('"filename" : "%s",' %(file_name), file=g)
	print('"width" : "%f",' %(pxmax-pxmin), file=g)
	print('"height" : "%f",' %(pymax-pymin), file=g)
	print('"text" : %s' %(text), file=g) # json dump'ed, no quotes
	print('}', file=g)
	return 1


if __name__ == "__main__":
	diagram_index = {}
	os.system("mkdir -p " + TMP)

	for s in glob.iglob("asy-sources/*/*"):
		junk, dir_name, file_name_full = s.split('/') #e.g. dir_name = 001-Demo, file_name = 1-Thale
		i = file_name_full.rfind('.')
		file_name = file_name_full[:i] # remove .asy extension
		extension = file_name_full[i+1:]
		createDiagram(dir_name, file_name, extension)

		if dir_name not in diagram_index:
			diagram_index[dir_name] = []
		diagram_index[dir_name].append(file_name)

	episodes = []
	for dir_name, filenames in sorted(diagram_index.items()):
		# strip leading number, convert dashes to spaces
		ep_name = dir_name.replace("-",": ",1).replace("-", " ")
		episodes.append("'"+ep_name+"': " + str(sorted(filenames)))
	
	with open("js/episode-index.js", "w") as f:
		print("EPISODES = {", file=f)
		print('\t' + ',\n\t'.join(episodes), file=f)
		print("\t};", file=f)
