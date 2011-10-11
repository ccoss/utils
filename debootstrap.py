#!/usr/bin/python

import os
import sys
import string
import shutil
import apt
import apt.progress
import time
################################################################################

# dirs to be install before install base system

rootdir = '/home/python/target'
lib = rootdir + '/var/lib'
cache = rootdir + '/var/cache'
dpkg = lib + '/dpkg'
info = dpkg + '/info'
updates = dpkg + '/updates'
apt_var = cache + '/apt' 
archives = apt_var + '/archives/'
partial_ar = archives + '/partial'
lists = apt_var + '/lists'
partial_li = lists + '/partial'
apt_etc = rootdir + '/etc/apt'
root = rootdir + '/root/'

dirs_to_be_create = [ rootdir, root, lib, cache, dpkg, info, updates, apt_var,
		   	 archives, partial_ar, lists, partial_li, apt_etc ]

################################################################################

# files to be create before install base system

bashrc = rootdir + '/root/.bashrc'
status = dpkg + '/status'
available = dpkg + '/available'
dpkg_list = info + 'dpkg.list'
lock_ar = archives + '/lock'
lock_dpkg = dpkg + '/lock'
lock_li = lists + '/lock'
sources_list = apt_etc +  '/sources.list'

files_to_be_create = [ bashrc, status, available, dpkg_list, lock_ar, lock_dpkg, lock_li, sources_list ]

################################################################################

#files to be copy before install base system

resolv_conf_src = '/etc/resolv.conf'
resolv_conf_dst = rootdir + resolv_conf_src
hostname_src = '/etc/hostname'
hostname_dst = rootdir + hostname_src
sources_list_src = './sources.list'
sources_list_dst = sources_list

files_to_be_copy = { resolv_conf_src:resolv_conf_dst, 
			hostname_src:hostname_dst,
		    sources_list_src:sources_list_dst, 
		     }

################################################################################

#Release file infomations

packages_dst = dpkg + '/'
release_dst = dpkg + '/'
release = release_dst + 'Release'

################################################################################

#default ip

ip = 'http://172.16.24.227/mirror/ubuntu/'

################################################################################

#core packages to be install first

pkg_core_lst = [ 'base-passwd','base-files', 'dpkg', 'libc6', 'perl-base',  'mawk', 'debconf' ]

################################################################################

#packages path
pkg_path = '/var/cache/apt/archives/'

################################################################################

#devices infomations
devices_targz = '/usr/share/debootstrap/devices.tar.gz'

################################################################################

#default input 'y' when installing packages
smallyes = 'while echo "y" 2>/dev/null ; do : ; done'

################################################################################

def mkDir( dirname ):
	if not os.path.exists( dirname ):
		os.makedirs( dirname )
		if os.path.exists( dirname ):
			print 'create new dir ' + dirname 

def mkDirs():
	for dirs in dirs_to_be_create:
		if dirs == rootdir:
			if os.path.exists( rootdir ):
				os.rename( rootdir, rootdir+'.bak' )
		mkDir(dirs)

################################################################################

def mkFile( filename ):
	f = open( filename, 'w' ) 
	f.close()
	if os.path.exists( filename ):
		print 'create new file ' + filename

def mkFiles():
	for files in files_to_be_create:
		mkFile(files)

################################################################################

def copyFile( file_src, file_dst ):
	if os.path.exists( file_src ):
		shutil.copyfile( file_src, file_dst )
		print 'copy %s to %s' % ( file_src, file_dst )
	else:
		print file_src + ' not exists'

def copyFiles():
	for files in files_to_be_copy.keys():
		copyFile( files, files_to_be_copy[files] )

################################################################################

def parseSourcesList( sources_list ):
		
	sources_list = sources_list
	parameter = []
	f_sources_list = open( sources_list, 'r')
	allLines = f_sources_list.readlines()	
	for eachLine in allLines:
		if eachLine == '\n':
			continue
		line_head = eachLine.split(' ')[0]
		if  line_head=='#' or line_head == 'deb-src':
			continue 
		param = []
		mirror = eachLine.split(' ')[1]	
		stable = eachLine.split(' ')[2]
		components = eachLine.split(' ')[3]
		for p in mirror,stable,components:
			param.append(p)
		parameter.append( param )
	f_sources_list.close()

	#default use the first line can be used in sources.list file
	#parameter contains mirror,stable,components 
	return parameter[0]

def getRelease():
	'''prepare Release file'''
	mirror, stable, components = parseSourcesList( sources_list )
	dists = '/dists/'
	release_src = mirror + dists + stable
	release = release_src + '/Release'
	if not os.path.exists( release ):
		os.system('wget -P %s %s' % (release_dst, release))
	if os.path.exists( release ):
		print 'Release file get ready!'

def parseRelease():
	'''parse Release file to gain the md5sum value of Packages file '''
	release_info = ''
	if os.path.exists( release ):
		f_release = open( release, 'r')
		release_info = f_release.read()
		f_release.close()
	else:
		return 'Release file is not exists'

	release_info = release_info.split('SHA1:')[0].split('MD5Sum:')[-1].split('\n')
	packages_md5 = ''
	for info in release_info:
		if info == '':
			continue
		info = info.split('/')
		if len(info)==3 and info[-2]=='binary-i386' and info[0].split(' ')[-1]=='main' and info[-1]== 'Packages':
			packages_md5 = info[0].split(' ')[1]

	return packages_md5
			
def getPackages():
	'''Download Packages file'''
	mirror, stable, components = parseSourcesList( sources_list )
	mirror = mirror + '/'
	stable = stable + '/'
	components = components + '/'
	dists = 'dists/' 
	arch = 'i386/'
	packages = packages_dst + 'Packages'
	packages_gz = 'Packages.gz'
	packages_src = mirror + dists + stable + components + 'binary-' + arch + packages_gz
	if not os.path.exists( packages ):
		os.system('wget -P %s %s; gunzip %s' % ( packages_dst, packages_src, packages_dst+packages_gz))		
	if os.path.exists( packages ):
		return packages
	else:
		print 'Packages downloaded failed'

def checkPackages():
	'''md5sum Packages file'''
	packages = packages_dst + 'Packages'
	packages_md5 = packages_dst + 'packages_md5'
	os.system('md5sum  %s > %s' % (packages, packages_md5))
	f_packages_md5 = open( packages_md5, 'r')
	md5 = f_packages_md5.read()
	f_packages_md5.close()
	md5 = md5.split(' ')[0]
	if md5 == parseRelease():
		return True
	else:
		return False	
		
def parsePackages():
	'''parese Packages file to gain the whole packages list

	packagelist is a dict 
	packagelist = { packagename : [ pkg_info, pkg_priority, pkg_build-essential, pkg_depends, pkg_filename] }
	
	for example:
	Package: abrowser
	Priority: optional
	Depends: firefox, abrowser-branding
	Build-Essential: 
	Filename: pool/main/f/firefox/abrowser_3.6.3+nobinonly-0ubuntu4_all.deb

	then:
	packagelist[ 'abrowser' ][ 'Priority' ] == 'optional'
	packagelist[ 'abrowser' ][ 'Depends' ] == 'firefox, abrowser-branding'
	'''
	packages = getPackages()
	debs_src = []
	f_packages = open( packages, 'r' )
	f_packages_info = f_packages.read()
	pkg_info = f_packages_info.split('\n\n')
	f_packages.close()
	global packagelist
	packagelist = {}
	for info in pkg_info:
		pkg = {}
		pkg['info'] = info
		info = info.split('\n')
		pkgname = info[0].split(' ')[-1]
		if pkgname == '':
			continue
		for line in info:
			if line.split(':')[0] == 'Priority':
				pkg['Priority'] = line.split(' ')[-1]
			if line.split(':')[0] == 'Build-Essential':
				pkg['Build-Essential'] = line.split(' ')[-1]
			if line.split(':')[0] == 'Depends':
				deps_lst = []
				deps = line.split(':')[-1].split(' ')
				for dep in deps:
					if dep == '\n' or dep == ' ' or dep == '' :
						continue
					s = string.letters
					if list(dep)[0] in list(s):
						if list(dep)[-1] == ',':
							dep = dep[:-1]
						deps_lst.append(dep)
				pkg['Depends'] = deps_lst				
			if line.split(':')[0] == 'Filename':
				pkg['Filename'] = line.split(' ')[-1]
		packagelist[ pkgname ] = pkg
	
################################################################################

class DpkgDepDeal( object ):
	
	def __init__( self ):
		self.cache = apt.Cache( None, rootdir )
		self.cache.update()
		self.cache.open()
		self.pkgnamelist = self.cache.keys()
		self.pkglist = {}
		self.pkglist_req = {}
		self.pkglist_base = {}
		self.pkglist_others = {}

	def addDep( self, pkglist, dependencies ):
		for dep in dependencies:
			for basedep in dep.or_dependencies:
				if self.cache.has_key(basedep.name):
					if not pkglist.has_key( basedep.name ):
						pkg = {}
						pkg['obj'] = self.cache[ basedep.name ].candidate
						pkg['depresolved'] = False
						pkglist[ basedep.name  ] = pkg
					break

	def resolveDep( self, pkglist ):
		#print 'Resolving dependencies~~~~'
		for name in pkglist.keys():
			if not pkglist[ name ]['depresolved']:
				self.addDep( pkglist, pkglist[ name ]['obj'].dependencies )
				pkglist[ name ]['depresolved']=True
				self.resolveDep( pkglist )
	
	def getPkgList(self, pkgnamelist ):
		print 'Getting Package List~~~~'
		for pkgname in pkgnamelist:
			pkg = {}
			pkg['obj'] = self.cache[pkgname].candidate
			pkg['depresolved'] = False
			if pkg['obj'].priority == "important" or pkg['obj'].priority == "required":
				self.pkglist[pkgname] = pkg
				if pkg['obj'].priority == "required":
					self.pkglist_req[pkgname] = pkg
				elif pkg['obj'].priority == "important":
					self.pkglist_base[pkgname] = pkg
			else:
				self.pkglist_others[pkgname] = pkg

	def printPkgList(self):
		self.getPkgList( self.pkgnamelist )
		self.resolveDep( self.pkglist )

################################################################################
	
def dpkgDownload( pkg_lst ):
	print 'Downloading Dpkg '
	for pkgname in pkg_lst:
		if pkgname in packagelist.keys():
			deb_src = ip+packagelist[ pkgname ]['Filename']
			os.system('wget -P %s %s ' % ( archives, deb_src) )

def dpkgExtract( pkg_lst ):
	for pkgname in pkg_lst:
		if pkgname in packagelist.keys():
			deb_dst = archives + packagelist[ pkgname ]['Filename'].split('/')[-1]
			os.system('dpkg -x %s  %s' % ( deb_dst, rootdir ) )
			print 'Extracting: %s' % pkgname

################################################################################

#in_target
def chroot( options ):
	options = ''' chroot %s /bin/bash -c "%s"''' % (rootdir, options)
	os.system( options )

def setAvailable( pkg_lst  ):
	print 'setting Available File'
	pkg_lst  = pkg_lst.keys()
	f_available = open( available, 'a')
	for pkgname in pkg_lst:
		if pkgname in packagelist.keys():
			info = packagelist[ pkgname ][ 'info' ] 
			f_available.write( info + '\n\n')
	f_available.close()
	
def setFstab():
	print 'setFstab()'
	fstab = rootdir + '/etc/fstab'
	if not os.path.exists( fstab ):
		fstab_info = '# UNCONFIGURED FSTAB FOR BASE SYSTEM'
		set_fstab = 'echo "%s" > %s;chown 0:0 %s;chmod 644 %s' % (fstab_info, fstab, fstab, fstab)
		os.system( set_fstab )

def setDevices():
	print 'setDevices():'
	if os.path.exists( devices_targz ):
		os.system('tar xvfz %s -C %s' % (devices_targz, rootdir))
	else:
		print 'devices_targz is not exists'

def setLanguage():       
	print 'setLanguage()'
	set_language = 'LC_ALL="C"\nexport LC_ALL\n'
	f_bashrc = open( bashrc, 'a')
	f_bashrc.write( set_language )
	f_bashrc.close()
	chroot('source /root/.bashrc')

def setProc():
	print 'setProc()'
	set_proc = 'mount -t proc proc /proc;mount -t sysfs sysfs /sys'
	chroot( set_proc )
	chroot( "/sbin/ldconfig" )

def setNoninteractive():
	print 'setNoninteractive()'
	set_noninteractive = 'DEBIAN_FRONTEND=noninteractive\nDEBCONF_NONINTERACTIVE_SEEN=true\nUSE_DEBIANINSTALLER_INTERACTION=no\nexport DEBIAN_FRONTEND DEBCONF_NONINTERACTIVE_SEEN USE_DEBIANINSTALLER_INTERACTION\n'

	f_bashrc = open( bashrc, 'a')
	f_bashrc.write( set_noninteractive )
	f_bashrc.close()

def setApt():
	cmethopt = rootdir + '/var/lib/dpkg/cmethopt'
	mkFile( cmethopt )
	os.system( 'chmod 644 %s' % cmethopt )
	f_cmethopt = open( cmethopt, 'a')
	f_cmethopt.write( 'apt apt\n' )
	f_cmethopt.close()

################################################################################
#def dpkgChange( pkglist ):
#	pkg_lst = pkglist
#	pkg_lst_to_be_change = []
#	for pkgname in pkg_lst:
#		pkgname = pkg_path + pkgname + '_*.deb'
#		pkg_lst_to_be_change.append( pkgname )
#	pkg_lst_to_be_change = (' ').join( [pkg for pkg in pkg_lst_to_be_change] )	
#
#	return pkg_lst_to_be_change

################################################################################

def coreDpkgInstall( pkgname ):
	deb_to_be_install = pkg_path + pkgname + '_*.deb'
	core_dpkg_install = '(%s) | (cd %s;dpkg --force-depends --install %s)' % ( smallyes, pkg_path, deb_to_be_install )
	chroot ( core_dpkg_install )

def coreDpkgInstalls():
	os.system('ln -sf mawk %s' % rootdir + '/usr/bin/awk')
	for pkgname in pkg_core_lst:
		print '\n|===coreDpkgInstalls: %s =======================================================' % pkgname
		if pkgname == 'mawk':
			awk = rootdir + '/usr/bin/awk'
			os.system('rm %s' % awk)
		coreDpkgInstall( pkgname )
		if pkgname == 'dpkg':
			localtime = rootdir + '/etc/localtime'
			if not os.path.exists( localtime ):
				os.system('''ln -sf /usr/share/zoneinfo/UTC "%s" ''' % localtime)

def reqDpkgInstall( pkgname ):
	deb_to_be_install = pkg_path + pkgname + '_*.deb'
	req_dpkg_install = '(%s) | (cd %s;dpkg --force-depends --unpack %s) ' % ( smallyes, pkg_path, deb_to_be_install )
	chroot ( req_dpkg_install )

def reqDpkgInstalls( req_pkg_lst ):
	req_pkg_lst = req_pkg_lst
	for pkgname in req_pkg_lst:
		print '\n|===reqDpkgInstalls: %s =======================================================' % pkgname
		reqDpkgInstall( pkgname )

def reqDpkgConfig():
	req_dpkg_config = '(%s) | (cd %s; dpkg --configure --pending --force-configure-any --force-depends)' \
			% ( smallyes,pkg_path )
	chroot( req_dpkg_config )

def baseDpkgInstall( pkgname ):
	deb_to_be_install = pkg_path + pkgname + '_*.deb'
	base_dpkg_install = '(%s) | (cd %s; dpkg --force-depends --unpack  %s)' % ( smallyes, pkg_path, deb_to_be_install )
	chroot( base_dpkg_install )

def baseDpkgInstalls( base_pkg_lst ):
	base_pkg_lst = base_pkg_lst
	for pkgname in base_pkg_lst:
		print'\n|===baseDpkgInstalls: %s =======================================================' %pkgname
		baseDpkgInstall( pkgname )

def basePkgConfig():
	base_dpkg_config='(%s) | (cd %s; dpkg --force-confold --force-configure-any --skip-same-version --configure -a)' \
		 		% ( smallyes, pkg_path )
	chroot( base_dpkg_config )

wrong_pkg_lst = ['rsyslog', 'gnupg-curl', 'ubuntu-minimal']

def wrongDpkgInstall( pkgname ):
	deb_to_be_install = pkg_path + pkgname + '_*.deb'	
	wrong_dpkg_install = '(%s) | (cd %s; dpkg   --force-depends --install  %s)' % ( smallyes,pkg_path, deb_to_be_install )
	chroot( wrong_dpkg_install )

def wrongDpkgInstalls( wrong_pkg_lst):
	wrong_pkg_lst = wrong_pkg_lst
	for pkg in wrong_pkg_lst:
		wrongDpkgInstall( pkg )	

################################################################################

def aptGet():
	apt_get = '(%s) | (apt-get -f install)' % smallyes
	chroot( apt_get )

def umountProc():
	umount_proc = "umount /proc;umount /sys"
	chroot( umount_proc )

################################################################################

def main():
	mkDirs()
	mkFiles()
	copyFiles()
	getRelease()
	getPackages()
	if checkPackages():
		print 'packages md5 check success'
		parsePackages()
		mc = DpkgDepDeal()
		mc.printPkgList()
		setAvailable( mc.pkglist )
		dpkgDownload( mc.pkglist )
		dpkgExtract( mc.pkglist_req ) 
		setFstab()
		setProc()
		setNoninteractive()
		setLanguage()
		try:
			coreDpkgInstalls()
			reqDpkgInstalls( mc.pkglist_req )
			setApt()
			reqDpkgConfig()
			baseDpkgInstalls( mc.pkglist_base )	
			basePkgConfig()
			aptGet()
			wrongDpkgInstalls( wrong_pkg_lst )
			print 'Base system install success!!!'
		except:
			print 'stop when install debs'

	else:
		print 'Please check your Packages file or Release file is ready!!!!'


if __name__ == '__main__':
	main()

	
################################################################################
