from lark import Lark
from lark import Transformer
import urllib.request
import os
from PyPDF2 import PdfFileMerger
import time
import pprint

import simpleeval
import util

import sys
import timeit
import method_spec
import method_gen
import music

pp = pprint.PrettyPrinter(indent=4)

# a=[1,2,3,4,5]
#
# print(util.rotateLeft(a, 6))
# print(util.rotateRight(a, 6))
# sys.exit(1)

# print("Permute result: ", method_gen.permute("123456", [1, 2, 3, 4]))

# test_gpn = [['x'], [1, 4], ['x'], [1, 4], ['x'], [1, 4], ['x'], [1, 2]]
# print("Gen method: ", pp.pprint(method_gen.generateAllRows(test_gpn, 4)))
#
# sys.exit(1)

#
# Minor music:
#
#
# 135246 queens
# 246135 queens, flipped
# 642531 back queens
# 531642 back queens, flipped
# 654321 backrounds
# 321654 backrounds flipped)
# 142536 tittums (<-- not in my double erin minor)
# 415263 tittums, pair-flipped
# 635241 back-tittums (<-- unsure)
# 362514 kind-of flipped tittums
#

#
# To avoid re-parsing the basic spec info for each stage generated,
# there is a spec parsing stage that reads the spec including PN but doesn't
# do any PN parsing yet.  We then generate (and cache) PN derived for different
# stages as and when it is required, given desired stage.
#
# Using a custom parser for the spec config is OTT. Should use a Configuration file parser or similar.
#

#
# examples of acceptable PN:
#
# x can have . around it:
#     x.1
#     x.1.x
#     1.x
#
# x doesn't need . between it and non-x:
#     x12
#     x12x
#     12x
#
# random:
#     1.2.3.4
#     12
#     12.34
#     12.90E
#     x12x34.14
#     145.56x78x12
#     1.x.2.x.3.x
#
#

# To specify a range of places from a to b inclusive, we can write:
#
# a_b.  So e.g. 4_[-3].


# def parse_stuff():
# 	util.process_gpn_string("1[29]x5.6")
# 	util.process_gpn_string("x")
# 	util.process_gpn_string("xxxxx")
# 	util.process_gpn_string("xx....x.x..xxx.")
# 	util.process_gpn_string(".")
# 	util.process_gpn_string("......")
# 	util.process_gpn_string(".x")
# 	util.process_gpn_string("x.")
# 	util.process_gpn_string("2x")
# 	util.process_gpn_string("x2")
# 	util.process_gpn_string("x.[-1][-2]")
# 	util.process_gpn_string("4[-1].x")

#running 1000 trials with timeit:
#    1.1s lalr
#    14.8s earley

# timeit.timeit(parseStuff, number=1000)

# parseStuff()
# t = util.process_gpn_string("5x")
# print()
# print(t.pretty())
#


# t = util.process_gpn_string("1n.3[-2]:x")
# print()
# print(t.pretty())

#--------------------------------------------

spec = Lark('''file: "{" defline* "}"
                   | _pn

			   defline: _propname "=" _value
			   		  | _pnpropname "=" pnvalue 

  		  // property names for stuff that's not place-notation
			   _propname: name
			   	       | stage
			   	       | length
			   	       | id

			   name: "name"
			   stage: "stage"
			   length: "length"
			   id: "id"

  		  // property names for stuff that's is place-notation
			   _pnpropname: notation
			   			  | base
			   			  | leadend
			   			  | halflead

			   notation: "notation"
			   base: "base"
			   leadend: "leadend"
			   halflead: "halflead"

			   _value: strvalue | numvalue

			   // escaped pn
			   pnvalue: "\\"" _pn "\\""

			   // unescaped pn
			   _pn: /~?[xXn,._\-\[\]|:0-9A-Z]+/

			   strvalue: "\\"" STRVALUE "\\""

// find something better for this
			   STRVALUE: /[*+()\[\].,\- ?!:;0-9a-zA-Z]+/

			   numvalue: INT

			   %import common.WS
			   %ignore WS

			   %import common.INT
            ''', start='file', parser='lalr')



# print("res = ", util.insert_ranged_places(['1', '_', '3', '4', '5', '_', '9']))
# sys.exit(1)


class SpecTransformer(Transformer):
	def __init__(self):
		self.stringProps = {}
		self.intProps = {}
		self.pnProps = {}

	# def pnpropname(self, items):
	# 	return items[0]

	# def pnstring(self, items):
	# 	print("found items: ", items)
	# 	return list(items)
	# def pnvalue(self, items):
	# 	print("processing pn, got ", items)
	# 	if len(items) > 0:
	# 		item = items[0]
	# 		# print("-- trans:pn, got item: ", item)

	# 		# if item == 'n':
	# 		# 	item = "[%d]" % self.stage

	# 		return item

	# 	return items

	def strvalue(self, items):
		return items[0].value

	def numvalue(self, items):
		return int(items[0].value)

	def defline(self, items):
		print("DEFLINE: items = ", items)
		if isinstance(items[1], str):
			print("found a string called %s, val = %s" % (items[0], items[1]))
			# remove the quotation marks at either end while we're at it
#			print("Before removal: ", items[1])
#			print("after removal: ", items[1][1:-1])
			# self.stringProps[items[0]] = items[1][1:-1]
		else:
			print("found a number called %s, val = %s " % (items[0], items[1]))
			self.intProps[items[0]] = items[1]

		# if items[0] == "stage":
		# elif items[0] == "notation":
		# 	print("found notation, val = ", items[1])
		# elif items[0] == "base":
		# 	print("found base, val = ", items[1])

		return items

	def notation(self, items):
		return "notation"

	def base(self, items):
		return "base"

	def name(self, items):
		return "name"

	def pnvalue(self, items):
		return items[0].value

	def stage(self, items):
		# print("called stage, items =-", items)
		return "stage"

	def length(self, items):
		# print("called stage, items =-", items)
		return "length"

	def leadend(self, items):
		# print("called leadend, items =-", items)
		return "leadend"

	def halflead(self, items):
		# print("called halflead, items =-", items)
		return "halflead"

	def id(self, items):
		# print("called stage, items =-", items)
		return "id"

	def file(self, items):
		# print("called stage, items =-", items)
		return items

# PB8 with ||.. pattern at leadend
# test1 = '''{
# 	name="PB variant"
# 	id="pbvariant"
#     base="x.18.x.18.x.18.x.18.x.18.x.18.x.18.x.1_||.._8"
# }'''

# test1 = '''{
# 	name="Almost Double Little Bob TR to 6"
# 	id="almostdoublelittlebobtrto6"
#     base="x.1n.x.1n.x.56.x.1n.x.1n.x.12"
# }'''


# test1 = '''{
# 	name="Double Evil Erin (down to 3rds)"
# 	id="doubleevilerin"
#     base="34.1n.34.x.34.1n"
# }'''

# test1 = '''{
# 	name="Evil Erin"
# 	id="plainhunt"
#     base="3n.1n.34.x.34.1n:3.1.34n.n.34n.1"
# }'''

#     base="3n.1n.3_[-3].x.3_[-3].1n:3.1.3_[-2]n.n.3_[-2]n.1"

# test1 = '''{
# 	name="Evil Erin with Places"
# 	id="evilerinplaces"
#     base="3n.1n.3_[-3].x.3_[-3].1n:3.1.3_n.n.3_n.1"
# }'''

# test1 = '''{
# 	name="Evil Erin with alt dodge+places"
# 	id="evilerinaltdodgeandplaces"
#     base="3n.1n.3_||,,_[-3].x.3_||,,_[-3].1n:3.1.3_||,,_[-3][-2][-1].n.3_||,,_n.1"
# }'''

# test1 = '''{
# 	name="Almost Double Evil Erin (dodges)"
# 	id="almostdoubleevilerin"
#     base="3[-3].1n.34.x.34.1n"
# }'''

# #double evil erin odd - WIP
# test1 = '''{
# 	name="Double Evil Erin ODD"
# 	id="doubleevilerin"
#     base="3[-3].1n.3_[-3].x.3_[-3].1n"
# }'''


test1 = '''{
	name="Double Erin"
	id="doubleerin"
    base="3[-3].1n.3[-3].1n.3[-3].x"
}'''

# test1 = '''{
# 	name="Double Evil Erin all places"
# 	id="doubleevilerinallplaces"
#     base="3[-3].1n.3_[-3].x.3_[-3].1n"
# }'''

#this is the same as evil erin on major I think
# test1 = '''{
# 	name="Double Evil Erin (places alt)"
# 	id="doubleevilerinplacesalt"
#     base="3[-3].1n.3_||,,_[-3].x.3_||,,_[-3].1n"
# }'''


# DOUBLE EVIL ERIN MAJOR HERE! THIS ONE!
# test1 = '''{
# 	name="Double Evil Erin"
# 	id="doubleevilerinallplaces"
#     base="34[-4][-3].1n.3[-3].1n.34[-4][-3].x"
# }'''

# this rotates last three bells to right every 4 leads (a bob every lead)
# test1 = '''{
# 	name="Double Evil Erin blooob"
# 	id="doubleevilerinallplaces"
#     base="34[-4][-3].1n.3[-3].14.34[-4][-3].x"
# }'''


# minimumstage = "8"

# test1 = '''{
# 	name="Double Evil Erin 2"
# 	id="doubleevilerin"
#     base="3[-3].1n.3[-3].1n.3[-3].x"
# }'''


# the thing that on 10 is 45.36.45.36.45.x.
# valid on 6, 10, 14, ...
# could write just base as base = [n/2]-[-n/2].1n, length = 6, leadend = 'x'
# test1 = '''{
# 	name="Split Erin"
# 	id="spliterin"
#     base="[n/2]-[-n/2].1n.[n/2]-[-n/2].1n.[n/2]-[-n/2].x"
#     minimumstage="6"
#     stageincrement="4"
# }'''

# test1 = '''{
# 	name="Reverse Bob"
# 	id="reversebob"
#     base="x.1n:n.1"
#     length="2*n"
#     halflead="[-2][-1]"
# }'''

# test1 = '''{
# 	name="Double Bob"
# 	id="doublebob"
#     base="x.1n:n.1"
#     length="2*n"
#     leadend="12"
#     halflead="[-2][-1]"
# }'''

# print(method_spec.TestClass())

parsedSpec = spec.parse(test1) 
print(parsedSpec)
print(parsedSpec.pretty())

specTx = SpecTransformer()
specTransformed = specTx.transform(parsedSpec)

specDict = dict(specTransformed)

ms = method_spec.MethodSpec(specDict)

print("spec transformed = ", specTransformed)
print("spec dict = ", specDict)

print("spec TX dicts: strings = %s, ints = %s" % (specTx.stringProps, specTx.intProps))

downloads_dir_name = "downloads"

if not os.path.isdir(downloads_dir_name):
	os.makedirs(downloads_dir_name)

# target_stages = range(8, 13, 2)
target_stages = [6]

all_filenames = []

download_pdfs = True
make_merged_pdf = True
process_all_pn_rotations = True
score_music = True

for s in target_stages:
	gpn_for_rot = ms.pn(s)
	gpn_len = len(gpn_for_rot)

	if process_all_pn_rotations:
		pn_rotations = range(0, gpn_len)
	else:
		pn_rotations = [0]

	# print("--------------- made PN from methodSpec: ", ms.pn(s))

	for pn_rotation in pn_rotations:

		gpn_for_rot = util.rotateLeft(gpn_for_rot, pn_rotation)

		print("Doing rot: ", pn_rotation)

		print("Using pn (after rot): ", gpn_for_rot)

		music_score = -1

		if score_music:
			allRows = method_gen.generateAllRows(gpn_for_rot, s)
			pp.pprint(allRows)

			#
			rows = method_gen.generateAllRows(gpn_for_rot, s)

			(music_score, music_details) = music.analyseMusic(rows)


			print("==========================================")
			print("---> Music analysis: ")
			print("GPN: ", gpn_for_rot)
			print("music score: ", music_score)
			print("Music details: ", music_details)

			print("")
			print("")

		# print("URL --> ", url)

		if download_pdfs:
			extra_info = None

			if music_score >= 0:
				extraInfo = "s=%d" % music_score

			(url, standard_pn_list, title) = ms.gen_link(s, pn_rotation, extraInfo)

			if process_all_pn_rotations:
				title = "%s (pn_rot=%s)" % (title, pn_rotation)

			file_name = "%s/%s.pdf" % (downloads_dir_name, title)

			all_filenames.append(file_name)
			# skip PDFs we have already downloaded
			if os.path.isfile(file_name):
				print("Skipping due to existing download: '%s'" % file_name)
				continue

			print("link: ", url)

			urllib.request.urlretrieve(url, file_name)

			time.sleep(1)


##################################################
# make a merged PDF

if download_pdfs and make_merged_pdf and (len(target_stages) > 1 or process_all_pn_rotations):
	all_pdfs_filename = "%s/%s - stages %s.pdf" % (downloads_dir_name, ms.name(), list(target_stages))

	if not os.path.isdir(all_pdfs_filename):
		merger = PdfFileMerger()

		for pdf_filename in all_filenames:
			merger.append(pdf_filename)

		merger.write(all_pdfs_filename)
		merger.close()
	else:
		print("Skipping all-pdf file generation, it already exists")
