#!/usr/bin/python
import argparse
import collections
import getpass
import os
from sortedcontainers import SortedSet
import stashy
import sys

def openFileList(file):
	list = SortedSet([])
	with open(file) as f:
		for l in f.read().splitlines():
			list.add(l.lower())
	return list

parser = argparse.ArgumentParser(description='Clone repositories from stash.')
parser.add_argument('stashurl', help='stash url')
parser.add_argument('stashuser', help='stash username')
parser.add_argument('-d', '--clone-directory', default='.')

repository_group = parser.add_mutually_exclusive_group()
repository_group.add_argument('--repository-list', help='path to file that contains a line-separated list of repository names')
repository_group.add_argument('--repository', help='the repository')

project_group = parser.add_mutually_exclusive_group()
project_group.add_argument('--project-list', help='path to file that contains a line-separated list of project names')
project_group.add_argument('--project', help='the project')

args = parser.parse_args()

repositories = None
if args.repository_list:
	repositories = openFileList(args.repository_list)

	print "\nLooking to clone the following repositories:"
	for r in repositories:
		print "\t" + r
elif args.repository:
	print "\nLooking to clone the following repository:"
	print "\t" + args.repository
	repositories = [args.repository.lower()]
else:
	print "\nLooking to clone all repositories"

projects = None
if args.project_list:
	projects = openFileList(args.project_list)

	print "\nIn the following projects:"
	for p in projects:
		print "\t" + p
elif args.project:
	print "\nIn the following project:"
	print "\t" + args.project
	projects = [args.project.lower()]
else:
	print "\nIn any project"

print "\nIn the following stash:"
print "\t" + args.stashurl + " (" + args.stashuser + ")"

print "\nIn the following directory:"
print "\t" + args.clone_directory
cont = raw_input("\nContinue? [Y/n]")

if cont and "y" != cont[0].lower():
	exit(0)

print "\n\n"
repositories_cloned = SortedSet([])
repositories_already_cloned = SortedSet([])
pswd = getpass.getpass('Stash Password:')
stash = stashy.connect(args.stashurl, args.stashuser, pswd)
for project in stash.projects.list():
	if projects and project["name"].lower() not in projects:
		continue

	first_repo = True
	print "Searching stash project[" + project["name"] + "]"
	for repo in stash.projects[project["key"]].repos.list():
		name = repo["name"].lower()
		if None == repositories or name in repositories:
			if first_repo:
				print ""
				first_repo = False

			print "Found repository[" + name + "]"
			repositories.remove(name)

			if os.path.exists(args.clone_directory + "/" + name):
				print name + " already cloned, continuing..."
				print ""
				repositories_already_cloned.add(name)
				continue

			for url in repo["links"]["clone"]:
				if (url["name"] == "ssh"):
					os.system("git clone " + url["href"] + " " + args.clone_directory + "/" + name)
					repositories_cloned.add(name)
					break

			print ""

print "\n\n*******************"
print "SUMMARY"
print "*******************"
print "Repositories Cloned:"
for s in repositories_cloned:
	print "\t" + s

print "\nRepositories Already Cloned:"
for s in repositories_already_cloned:
	print "\t" + s

print "\nRepositories Not Found:"
for s in repositories:
	print "\t" + s
