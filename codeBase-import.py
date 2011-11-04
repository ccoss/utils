#!/usr/bin/python

import os
import shutil
import string
import sys


pkg_lst_src = '/opt/'
pkg_lst_dst = '/opt/ABS/codeBase/'

try:
	git_server_ip = sys.argv[1]
except:
	print 'git_server_ip error'


print git_server_ip

class codeBase_import(object):
	
	def __init__(self,pkg_lst_src = ''):

		self.pkg_lst_src = pkg_lst_src	

	def import_times_judge(self):
		"""
		judge import times: whether it is 1st import or not:
		Yes: init-import()
		No:update-import()		
		"""    
		print 'import_times_judge'
		pkg_lst = pkg_lst_dst  + 'pkg_lst'			 

		if os.path.exists(pkg_lst) is False:
			self.init_import()	
		else:
			self.update_import()

	def init_import(self):
		'''init data import '''
		print 'init_import'
		self.pkg_lst_dl()
		pkg_type = self.pkg_lst_prs()
		self.src_import(pkg_type)

	def update_import(self):
		'''add data import'''
		print 'update_import'
		self.pkg_lst_redl()
		pkg_type = self.pkg_add_prs()
		self.src_import(pkg_type)

	def src_import(self,pkg_type):
		'''dsc or src.rpm import'''
		print 'src_import'
		try:
			if pkg_type == 'src.rpm':
				self.rpkg_import()
			elif pkg_type == 'dsc':
				self.dpkg_import()		
		except:
			print 'src_import error'	
	def pkg_lst_dl(self):
		'''first time download package_list'''	
		print 'pkg_lst_dl'
		pkg_lst = self.pkg_lst_src + 'pkg_lst'
		try:
			if os.path.exists(pkg_lst_dst) is False:
				os.makedirs(pkg_lst_dst)
			shutil.copy(pkg_lst, pkg_lst_dst)
		except:
			print 'pkg_lst_dl error'

	def pkg_lst_redl(self):
		'''one more time dowmload package_list'''
		print 'pkg_lst_redl'	
		pkg_lst = self.pkg_lst_src + 'pkg_lst'
		tmp_pkg_lst = pkg_lst_dst + 'pkg_lst'
		old_pkg_lst = pkg_lst_dst + 'old_pkg_lst'
		os.rename(tmp_pkg_lst, old_pkg_lst)
		try:
			shutil.copy(pkg_lst, pkg_lst_dst)
		except:
			print 'pkg_lst_redl error'
	def pkg_lst_prs(self):
		'''parse package_list'''
		print 'pkg_lst_prs'
		pkg_lst = pkg_lst_dst + 'pkg_lst'
		try:
			pkg_lst = open(pkg_lst,'r')
		except:
			print 'open pkg_lst error'	
		try:
			allLines = pkg_lst.readlines()
			juageLine = allLines[0]				
			pkg_type = juageLine.split('.')[-1].split('\n')[0]
		except:
			print 'read pkg_lst error'
		finally:
			pkg_lst.close()

		try:
			return pkg_type
		except:
			print 'return pkg_type error'

	def pkg_lst_cmp(self):
		'''compare new package_lst to old package_lst'''
		print 'pkg_lst_cmp'
		pkg_add_lst = ('pkg_d','pkg_e','pkg_f')
		try:
			return pkg_add_lst
		except:
			print 'return pkg_add_lst error'
	def pkg_add_prs(self) :
		'''parse add packages'''

		print 'pkg_add_prs'
		pkg_type = pkg_lst_prs()
							
		try:
			return  pkg_type, self.pkg_lst_cmp()
		except:
			print 'pkg_add_prs error'
	def rpkg_import(self):
		'''import src.rpm'''
		pass

	def dpkg_import(self):
		'''import dsc'''
		print 'dpkg_import'
		pkg_lst = pkg_lst_dst + 'pkg_lst'
		try:
			pkg_lst = open(pkg_lst,'r')
		except:
			print 'open pkg_lst in dpkg_import error'	
		try:
			allLines = pkg_lst.readlines()
			pkg_import_lst = []
			for eachLine in allLines:
   	    			if eachLine.split('.')[-1].split('\n')[0] == 'dsc':
					eachLine = eachLine.split('\n')[0]
					pkg_import_lst.append(eachLine)	

			for num in xrange(len(pkg_import_lst)):
				pkg_to_be_git = pkg_lst_src + pkg_import_lst[num]
				print pkg_to_be_git
				os.chdir(pkg_lst_dst)
				os.system('git-import-dsc %s' % pkg_to_be_git)
				git_push_dir = pkg_import_lst[num].split('/')[-2]
				os.chdir(git_push_dir)
				os.system('git %s  %s' % ('push --all',git_server_ip+git_push_dir))
				os.system('git %s  %s' % ('push --tags',git_server_ip+git_push_dir))
				git_ip = git_server_ip.split(':')[0]
				git_sys = git_server_ip.split(':')[-1]
				os.system('echo \'%s repo test\'| ssh  %s setdesc %s' % (git_push_dir,git_ip,\
												 git_sys+git_push_dir))


		except:
			print 'git push error'

		finally:
			pkg_lst.close()



mc = codeBase_import(pkg_lst_src) 
mc.import_times_judge()
