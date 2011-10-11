#! /bin/bash
#func:sourcelist_get deblst_get rpmlst_get synchronism_deb synchronism_rpm

RSYNC=rsync
RSYNCURL=
ISSUE=
RELEASE=
ARCH_INCLUDE=
ARCH=
MIRROR_DIR=
PACKAGESLST_DIR=/home/heyang/packagelist
PACKAGEFN=Packages
SOURCEFN=Sources
PACKAGES_LIST=Packages_list
SOURCES_LIST=Sources_list
DATE_DIR=`date +"%Y-%m-%d"`

sourcelist_get()
{
cd $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/source/$DATE_DIR
grep -n "^Directory:" $SOURCEFN | sed -e "s/:.*//" > temp1
grep -n "^$" $SOURCEFN | sed -e "s/:.*//" | paste -d "," temp1 - | while read line; do
       sed -e "$line  p" -n $SOURCEFN > temp2
       BL=`sed -e "1p" -n temp2 | sed -e "s/[^:]*: //"`
       sed -e "1,2d; /^[^ ]/,$ d; s/^ /        /; /^$/d" temp2 | sed -e "s|^|$BL|" | awk '{print $1,$4}' | sed -e 's/ /\//g' >> $SOURCES_LIST
done
rm temp1 temp2
cd - 
}

deb_sourcelst_get()
{
if [ ! -d $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/source ]; then
mkdir -p $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/source
fi
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/Release $MIRROR_DIR/$ISSUE/dists/$RELEASE/Release
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/Release.gpg $MIRROR_DIR/$ISSUE/dists/$RELEASE/Release.gpg
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/main/source/Sources.bz2 $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/source/Sources.bz2
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/main/source/Sources.gz $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/source/Sources.gz
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/main/source/Release $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/source/Release

if [ ! -d $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/source/$DATE_DIR ]; then
mkdir -p $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/source/$DATE_DIR
fi
if [ -e $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/source/Sources.bz2 ]; then
bzip2 -cd $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/source/Sources.bz2 > $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/source/$DATE_DIR/$SOURCEFN
sourcelist_get
fi
}

deb_packagelst_get()
{
if [ ! -d $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH ]; then
mkdir -p $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH
fi

$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/Release $MIRROR_DIR/$ISSUE/dists/$RELEASE/Release
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/Release.gpg $MIRROR_DIR/$ISSUE/dists/$RELEASE/Release.gpg
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/main/binary-$ARCH/Packages.bz2 $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/Packages.bz2
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/main/binary-$ARCH/Packages.gz $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/Packages.gz
$RSYNC -atvp $RSYNC://$RSYNCURL/$ISSUE/dists/$RELEASE/main/binary-$ARCH/Release $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/Release

if [ ! -d $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/$DATE_DIR ]; then
mkdir -p $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/$DATE_DIR
fi
if [ -e $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/Packages.bz2 ]; then
bzip2 -cd $MIRROR_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/Packages.bz2 > $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/$DATE_DIR/$PACKAGEFN
cat $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/$DATE_DIR/$PACKAGEFN |grep Filename:|sed '/^Filename/s/Filename: //g' > $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/$DATE_DIR/$PACKAGES_LIST
fi
}

deb_sources_sync()
{
if [ ! -d $MIRROR_DIR/$ISSUE ]
then
        mkdir -p $MIRROR_DIR/$ISSUE
fi
echo $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/source/$DATE_DIR/$SOURCES_LIST
if [ -e $PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/source/$DATE_DIR/$SOURCES_LIST ]; then
$RSYNC -atvp --relative --progress --files-from=$PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/source/$DATE_DIR/$SOURCES_LIST $RSYNC://$RSYNCURL/$ISSUE/ $MIRROR_DIR/$ISSUE
fi
}

deb_packages_sync()
{
if [ ! -d $MIRROR_DIR/$ISSUE ]
then
        mkdir -p $MIRROR_DIR/$ISSUE
fi

$RSYNC -atvp --relative --progress --files-from=$PACKAGESLST_DIR/$ISSUE/dists/$RELEASE/main/binary-$ARCH/$DATE_DIR/$PACKAGES_LIST $RSYNC://$RSYNCURL/$ISSUE/ $MIRROR_DIR/$ISSUE
}

rpm_sourcelst_get()
{
if [ ! -d $PACKAGESLST_DIR/$ISSUE/$RELEASE/source/$DATE_DIR ]
then
        mkdir -p $PACKAGESLST_DIR/$ISSUE/$RELEASE/source/$DATE_DIR
fi
ls -l $MIRROR_DIR/$ISSUE/releases/$RELEASE/Everything/source/SRPMS | grep "^-" | awk '{print $8}' > $PACKAGESLST_DIR/$ISSUE/$RELEASE/source/$DATE_DIR/$SOURCES_LIST
}

rpm_packagelst_get()
{
if [ ! -d $PACKAGESLST_DIR/$ISSUE/$RELEASE/$ARCH/$DATE_DIR ]
then
        mkdir -p $PACKAGESLST_DIR/$ISSUE/$RELEASE/$ARCH/$DATE_DIR
fi
ls -l $MIRROR_DIR/$ISSUE/releases/$RELEASE/Everything/$ARCH/os/Packages | grep "^-" | awk '{print $8}' > $PACKAGESLST_DIR/$ISSUE/$RELEASE/$ARCH/$DATE_DIR/$PACKAGES_LIST
}

rpm_sources_sync()
{
if [ ! -d $MIRROR_DIR/$ISSUE/releases/$RELEASE/Everything ]
then
        mkdir -p $MIRROR_DIR/$ISSUE/releases/$RELEASE/Everything
fi

echo "$RSYNC -av --progress  $RSYNCURL $MIRROR_DIR"
$RSYNC -atvp --progress $RSYNC://$RSYNCURL/$ISSUE/releases/$RELEASE/Everything/source $MIRROR_DIR/$ISSUE/releases/$RELEASE/Everything
}

rpm_packages_sync()
{
if [ ! -d $MIRROR_DIR/$ISSUE/releases/$RELEASE/Everything ]
then
        mkdir -p $MIRROR_DIR/$ISSUE/releases/$RELEASE/Everything
fi

echo "$RSYNC -av --progress  $RSYNCURL $DESTINATION"
$RSYNC -atvp --progress $RSYNC://$RSYNCURL/$ISSUE/releases/$RELEASE/Everything/$ARCH $MIRROR_DIR/$ISSUE/releases/$RELEASE/Everything
}

if [[ $1 == "-h" ]]; then
        echo "USage: 	-u source url
   	-s linux issues
   	-r release
   	-a arch"
        exit    
fi

while [ -n "$(echo $1 | grep '-')" ]; do
	case $1 in 
	-u ) RSYNCURL=$2
	     echo source url:$RSYNCURL
	     shift ;;
        -s ) ISSUE=$2
		echo issue:$ISSUE
             shift ;;
        -r ) RELEASE=$2
		echo release:$RELEASE
	     shift ;;
	-a ) ARCH_INCLUDE=$(echo "$*"|sed -e "s/-a //; s/ -.*//")
	     echo arch:$ARCH_INCLUDE
	     shift $(echo "$*"|sed -e "s/-a //; s/ -.*//"|wc -w) ;;
	-m ) MIRROR_DIR=$2
	     echo mirrordir:$MIRROR_DIR
	     shift;;
        *  ) echo 'usage: alice [-a] [-b barg] [-c] args...'
             exit 1
	esac
	shift
done 

case $ISSUE in
	debian|ubuntu)
	for ARCH in ${ARCH_INCLUDE}; do
	{
		if [ "${ARCH}" = "source" ]; then
		deb_sourcelst_get && deb_sources_sync 	
		else
		deb_packagelst_get && deb_packages_sync
		fi
	}&
	done
	;;
	fedora|meego)
	for ARCH in ${ARCH_INCLUDE}; do
	{
	if [ "${ARCH}" = "source" ]; then
	rpm_sources_sync
	wait
	rpm_sourcelst_get
	else
	rpm_packages_sync
	wait
	rpm_packagelst_get
	fi
	}&
	done
	;;
esac
