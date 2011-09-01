%{!?_texmf: %define _texmf %(eval "[ -x /usr/bin/kpsewhich ] && echo `kpsewhich -expand-var '$TEXMFMAIN'` || echo %{_datadir}/texmf")}

%define _scriptsdir %{_datadir}/tex4ht

Summary:       Translates TeX and LaTeX into HTML or XML+MathML
Name:          tetex-tex4ht
Version:       1.0.2008_09_16_1413
Release:       4%{?dist}
License:       LPPL
Group:         Applications/Publishing
URL:           http://www.cse.ohio-state.edu/~gurari/TeX4ht/
Source0:       http://www.cse.ohio-state.edu/~gurari/TeX4ht/fix/tex4ht-%{version}.tar.gz
# Source1 is only used for documentation
# renamed to tex4ht-all-YYYYMMDD.zip - based on last timestamp in directory
Source1:       tex4ht-all-20080616.zip
# unversioned upstream source, downloaded with wget -N
#Source1 http://www.cse.ohio-state.edu/~gurari/TeX4ht/tex4ht-all.zip
Source2:       tex4ht-lppl.txt
# unversioned upstream litteral source, downloaded with wget -N
#Source3:       http://www.cse.ohio-state.edu/~gurari/TeX4ht/fix/tex4ht-lit.zip
Source3:       tex4ht-lit-20080616.zip
Source4:       http://www.cse.ohio-state.edu/~gurari/tpf/ProTex.sty
Source5:       http://www.cse.ohio-state.edu/~gurari/tpf/AlProTex.sty
Source6:       http://www.cse.ohio-state.edu/~gurari/tpf/DraTex.sty
Source7:       http://www.cse.ohio-state.edu/~gurari/tpf/AlDraTex.sty
# debian
Patch1:        http://ftp.de.debian.org/debian/pool/main/t/tex4ht/tex4ht_20080701-2.diff.gz
# debian patch rebased
#Patch2:        fix_tex4ht_env.diff
# update debian rebuild script
#Patch3:        tetex-tex4ht-1.0-rebuild.patch
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# kpsewhich should be brought in by kpathsea-devel anyway
BuildRequires:  /usr/bin/kpsewhich
BuildRequires:  kpathsea-devel
BuildRequires:  java-devel
# Doesn't run with gcj, so better build it with icedtea/openjdk too
#BuildRequires:  java-1.6.0-openjdk-devel
BuildRequires:  /usr/bin/fastjar
# for uudecode to generate the debian tutorial images
BuildRequires:  sharutils
# pnmcrop and pnmtopng are in netpbm-progs. 
Requires:       netpbm-progs
# ImageMagick, pstoedit depends on ghostscript and gs is in ghostscript
Requires:       ImageMagick pstoedit
# for all the conversion scripts
Requires:        tex(latex) tex(dvips) tex(context) tex(xetex) texinfo-tex
Requires:        /usr/bin/dvipng
Requires:       java
#Requires:       java-1.6.0-openjdk
Requires(post):   /usr/bin/texhash
Requires(postun): /usr/bin/texhash
Obsoletes:      tex4ht < %{version}-%{release}
Provides:       tex4ht = %{version}-%{release}

# description taken from ctan and modified
%description 
A converter from TeX and LaTeX to hypertext (HTML, XML, etc.), providing a
configurable (La)TeX-based authoring system for hypertext. When converting
to XML, you can use MathML instead of images for equation representation.

This package can also be used to translated to XML that OpenOffice.org can
understand, which then gives the user a path by which to convert a document
to rtf for import into Microsoft Word.

%prep
%setup -q -n tex4ht-%{version}
# debian patch
%patch1 -p1

chmod a-x src/*.c
cp -p %{SOURCE2} lppl.txt
# unzip the all source for the doc
mkdir doc/
pushd doc/
  unzip %{SOURCE1}
  rm *.zip
  rm -r fix
popd
mkdir lit/
pushd lit
  unzip %{SOURCE3}
  chmod 0644 *.tex
popd

cp -p %{SOURCE4} %{SOURCE5} %{SOURCE6} %{SOURCE7} lit/

# avoid duplicating the debian patches
patch -p1 < debian/patches/fix_mk4ht.diff
# hardcoded /usr/share
#%patch2 -p1
patch -p1 < debian/patches/fix_tex4ht_env.diff
# use the debian man page
patch -p1 < debian/patches/add_manpage.diff
# Makefile used as a source of inspiration
patch -p1 < debian/patches/add_Makefile.diff
patch -p1 < debian/patches/add_xtpipes_support
patch -p1 < debian/patches/Makefile_indep_arch
# scripts and texmf.cnf excerpt for debian not used
patch -p1 < debian/patches/add_scripts_sh.diff
patch -p1 < debian/patches/add_texmf_cnf.diff

# patches for literate sources
patch -p1 < debian/lit/patches/fix_tex4ht_dir.diff
patch -p1 < debian/lit/patches/fix_tex4ht_fonts_4hf.diff

chmod a+x debian/lit/rebuild.sh

(cd debian/images; for i in *.uue; do uudecode $i; done; mv *.png ../html)

find  texmf -type f -exec chmod a-x \{\} \;

%build
pushd src
CFLAGS="$RPM_OPT_FLAGS -DHAVE_STRING_H -DHAVE_DIRENT_H -DHAVE_UNISTD_H \
 -DHAVE_SYS_DIR_H -DKPATHSEA -DENVFILE=\"%{_texmf}/tex4ht/base/unix/tex4ht.env\""
LDFLAGS=-lkpathsea
%{__cc} -o tex4ht $CFLAGS tex4ht.c $LDFLAGS
%{__cc} -o t4ht $CFLAGS t4ht.c $LDFLAGS

# adapted from debian Makefile
mkdir class
javac -d class -source 1.5 java/*.java java/xtpipes/*.java java/xtpipes/util/*.java
fastjar -c -f tex4ht.jar -m java/manifest -C class .
popd

# beware of the %% that have to be protected as %%%%
# lib is hardcoded because the jvm is there whatever the architecture.
sed \
  -e "s;^i.*/ht-fonts/;i%{_texmf}/tex4ht/ht-fonts/;" \
  -e "s;^tpath/tex/;t%{_texmf}/;" \
  -e "s;%%%%~/texmf-dist/;%{_texmf}/;" \
  -e 's;^\(\.[^ ]\+\) java;\1 /usr/lib/jvm/jre-openjdk/bin/java;' \
 texmf/tex4ht/base/unix/tex4ht.env > tex4ht.env

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_bindir} $RPM_BUILD_ROOT%{_scriptsdir}
install -m755 src/tex4ht $RPM_BUILD_ROOT%{_bindir}
install -m755 src/t4ht $RPM_BUILD_ROOT%{_bindir}
#install -m755 bin/ht/unix/* $RPM_BUILD_ROOT%{_bindir}
install -p -m755 bin/ht/unix/* $RPM_BUILD_ROOT%{_scriptsdir}
for script in httex htlatex httexi htcontext htxetex htxelatex; do
  install -p -m755 bin/ht/unix/$script $RPM_BUILD_ROOT%{_bindir}
done
install -p -m755 bin/ht/unix/ht $RPM_BUILD_ROOT%{_bindir}/tex4ht-ht
install -p -m755 bin/unix/mk4ht $RPM_BUILD_ROOT%{_bindir}
install -p -m644 src/tex4ht.jar $RPM_BUILD_ROOT%{_scriptsdir}

mkdir -p $RPM_BUILD_ROOT%{_texmf}/tex4ht/base/unix
cp tex4ht.env $RPM_BUILD_ROOT%{_texmf}/tex4ht/base/unix

pushd texmf
cp -pr tex4ht/ht-fonts $RPM_BUILD_ROOT%{_texmf}/tex4ht
cp -pr tex4ht/xtpipes $RPM_BUILD_ROOT%{_texmf}/tex4ht

mkdir -p $RPM_BUILD_ROOT%{_texmf}/tex/generic
cp -pr tex/generic/tex4ht $RPM_BUILD_ROOT%{_texmf}/tex/generic
popd

cp -pr debian/html tutorial

mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
sed -e 's;@SCRIPTSDIR@;%{_scriptsdir};' \
 -e 's;@TEX4HTDIR@;%{_texmf}/tex4ht/base/unix;' \
 -e 's;@TEXMFCNF@;%{_texmf}/web2c/texmf.cnf;' \
 -e 's;@HTFDIR@;%{_texmf}/tex4ht/ht-fonts;' \
 -e 's;@TEXDIR@;%{_texmf}/tex/generic/tex4ht;g' \
 src/tex4ht.man > $RPM_BUILD_ROOT%{_mandir}/man1/tex4ht.1

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_texmf}/tex4ht/
%{_texmf}/tex/generic/tex4ht/
%{_bindir}/ht*
%{_bindir}/tex4ht-ht
%{_bindir}/mk4ht
%{_bindir}/tex4ht
%{_bindir}/t4ht
%{_scriptsdir}/
%{_mandir}/man1/tex4ht.1*
%doc lppl.txt doc tutorial debian/README.kpathsea 

%post
texhash > /dev/null 2>&1 || :

%postun
texhash > /dev/null 2>&1 || :

%changelog
* Fri Jun 25 2010 Jindrich Novy <jnovy@redhat.com> 1.0.2008_09_16_1413-4
- do not require openjdk (#606852)

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.0.2008_09_16_1413-3.1
- Rebuilt for RHEL 6

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2008_09_16_1413-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2008_09_16_1413-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Oct  4 2008 Patrice Dumas <pertusus@free.fr> 1.0.2008_09_16_1413-1
- update to 2008_09_16_1413
- adapt to texlive

* Sun Apr 13 2008 Patrice Dumas <pertusus@free.fr> 1.0.2008_02_28_2058-3
- xtpipes works only with sun jre (#436608)

* Sat Mar  1 2008 Patrice Dumas <pertusus@free.fr> 1.0.2008_02_28_2058-1
- update to 1.0.2008_02_28_2058
- new debian patch, new literate sources

* Mon Dec 31 2007 Patrice Dumas <pertusus@free.fr> 1.0.2007_12_19_2154-1.1
- update to 1.0.2007_12_19_2154
- new debian patch, new literate sources
- adapt for texlive

* Sun Nov 25 2007 Patrice Dumas <pertusus@free.fr> 1.0.2007_11_19_2329-1
- update to 1.0.2007_11_19_2329 and use new literate sources

* Sun Nov 11 2007 Patrice Dumas <pertusus@free.fr> 1.0.2007_11_07_1645-1
- update to 1.0.2007_11_07_1645

* Fri Sep 21 2007 Patrice Dumas <pertusus@free.fr> 1.0.2007_09_04_0340-1
- update to 1.0.2007_09_04_0340
- use all the debian patches
- install correctly the scripts out of bindir
- prefix ht with tex4ht- to avoid name collisions

* Sat Aug  4 2007 Patrice Dumas <pertusus@free.fr> 1.0.2007_07_17_0228-1
- update to 1.0.2007_07_17_0228
- rename tetex-tex4ht-1.0-prev.patch to tetex-tex4ht-1.0-rebuild.patch

* Fri Nov  3 2006 Patrice Dumas <pertusus@free.fr> 1.0.2006_10_28_1705-1
- update
- use debian patchset
- remove the patch modifying paths in tex4ht.env, it is unneeded with 
  kpathsee

* Mon Aug 28 2006 Patrice Dumas <pertusus@free.fr> 1.0.2006_08_26_2341-2
- update

* Tue Jun 20 2006 Patrice Dumas <pertusus@free.fr> - 1.0.2006_06_19_1646-1
- update

* Fri Mar 31 2006 Patrice Dumas <pertusus@free.fr> - 1.0.2006_03_27_1822-1
- update

* Fri Feb 17 2006 Patrice Dumas <pertusus@free.fr> - 1.0.2006_02_15_1234-1
- update

* Thu Dec 22 2005 Patrice Dumas <pertusus@free.fr> - 1.0.2005_12_21_0412-1
- update

* Mon Nov 14 2005 Patrice Dumas <pertusus@free.fr> - 1.0.2005_11_06_1516-3
- add Requires for ImageMagick

* Mon Nov 14 2005 Patrice Dumas <pertusus@free.fr> - 1.0.2005_11_06_1516-2
- keep timestamps, use tex4ht-all-YYYYMMDD.zip (Michael A. Peters)

* Sun Nov 13 2005 Patrice Dumas <pertusus@free.fr> - 1.0.2005_11_06_1516-1
- updated version

* Sat Nov  5 2005 Patrice Dumas <pertusus@free.fr> - 1.0.2005_10_31_0336-1
- updated version
- added website documentation
- added licence

* Wed Sep 21 2005 Michael A. Peters <mpeters@mac.com> - 1.0-0.2005_09_13_0129.1
- updated version
- got rid of patch that makes Makefile, specify build option in build
- use -DKPATHSEA
- added obsoletes tex4ht due to renaming

* Mon Sep 19 2005 Michael A. Peters <mpeters@mac.com> - 1.0-0.2005_02_16_2023.1
- cleaned up spec file to be closer to Fedora Extras standards
- renamed package from tex4ht to tetex-tex4ht

* Wed Feb 9 2005 Erik Sjolund <erik.sjolund@sbc.su.se>
- New upstream release
- merged the two patches into one
* Wed Feb  9 2005 Edward Grace <graceej@ptpc3lin.op.ph.ic.ac.uk> - 1.0.2004_12_16_1626-2
- Added a requirement for tetex
- On FC2 the font directory was not being correctly found, added a trivial 
  patch which corrects this. It also works with Fedora Core 3
- Added the URL specifier to point to Erik Sjölund's page where I found the sources.
* Mon Dec 20 2004 Erik Sjolund <erik.sjolund@home.se>
- New upstream release
- Switched to Fedora Core 3
* Wed Oct 15 2004 Erik Sjolund <erik.sjolund@home.se>
- New upstream release
- Thanks Neil D. Becker for the changes to the spec file
  in this release!
- The files section totally restructured. Instead of specifying
  single files explicitly, the directories containg all the files
  are specified instead. 
* Wed Sep 22 2004 Erik Sjolund <erik.sjolund@home.se>
- New upstream release
- I had to remove 
  /usr/bin/htcontext.unix
  /usr/bin/xhcontext.unix
  from the files section as they were no longer shipped.
* Wed Jul 14 2004 Erik Sjolund <erik.sjolund@home.se>
- Adjusted the /usr/src/redhat/SOURCES/tex4ht-redhat.patch so that 
  texmf/tex4ht/base/unix/tex4ht.env now has the line "l~/.tex4ht.fls"
* Tue Jul 13 2004 Erik Sjolund <erik.sjolund@home.se>
- I downloaded new sources from
  http://www.cse.ohio-state.edu/~gurari/TeX4ht/bugfixes.html.
  # Google gives the first hit on tex4ht as
  # http://www.cse.ohio-state.edu/~gurari/TeX4ht/mn.html
  # That page seems not be the primary source of the latest news about tex4ht.
  # Look instead at http://www.cse.ohio-state.edu/~gurari/TeX4ht/bugfixes.html
  # to get the latest sources.
- I adjusted /usr/src/redhat/SOURCES/tex4ht-redhat.patch to conform to the new
  sources
- There were some new installed files, so I included them in the files section:
  /usr/bin/dbmtexexec
  /usr/bin/dbtexexec
  /usr/bin/htcontext
  /usr/bin/htcontext.unix
  /usr/bin/httexexec
  /usr/bin/mk4ht 
  /usr/bin/mztexexec
  /usr/bin/ootexexec
  /usr/bin/teimtexexec
  /usr/bin/teitexexec
  /usr/bin/xhcontext
  /usr/bin/xhcontext.unix
  /usr/bin/xhmtexexec
  /usr/bin/xhtexexec

- Packager: John Langford 

