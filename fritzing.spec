%define debug_package %{nil}

Name: fritzing
Version: 0.9.9
Release: 1
Summary: PCB layout tool
License: CC-Attribution-ShareAlike 3.0 Unported
Group: Sciences/Other
Url: http://fritzing.org/
# https://github.com/fritzing/fritzing-app
# Unfortunately they don't tag releases, so we grab develop snapshots
# close to release date.
Source0: https://github.com/fritzing/fritzing-app/archive/refs/heads/develop.tar.gz
Source1: https://github.com/fritzing/fritzing-parts/archive/refs/heads/develop.zip
# Important extra parts
Source10: https://content.arduino.cc/assets/Arduino%20Nano%2033%20BLE%20Sense.fzpz
Patch0: fritzing-system-libs.patch
Patch1:	https://src.fedoraproject.org/rpms/fritzing/raw/rawhide/f/0000-disable-autoupdate.patch
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(Qt5PrintSupport)
BuildRequires:	pkgconfig(Qt5Svg)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	pkgconfig(Qt5Gui)
BuildRequires:	pkgconfig(Qt5Concurrent)
BuildRequires:	pkgconfig(Qt5Network)
BuildRequires:	pkgconfig(Qt5SerialPort)
BuildRequires:	pkgconfig(Qt5Sql)
BuildRequires:	pkgconfig(Qt5Xml)
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(quazip)
BuildRequires:	qmake5
BuildRequires:	qt5-macros
BuildRequires:	boost-devel

%description
PCB layout tool

%prep
%autosetup -p1 -n fritzing-app-develop -a 1
# Use system quazip
rm -rf pri/quazip.pri src/lib/quazip
sed -i -e 's,quazip5/,QuaZip-Qt5-1.1/quazip/,g' src/utils/folderutils.cpp

LIBGIT_STATIC=false %qmake_qt5 phoenix.pro DEFINES=QUAZIP_INSTALLED
mv fritzing-parts-develop parts

%build
%make_build release
./Fritzing -platform minimal -f ./parts -db ./parts/parts.db

%install
%make_install INSTALL_ROOT=%{buildroot}

%files
%defattr(-,root,root)
%doc LICENSE.CC-BY-SA LICENSE.GPL2 LICENSE.GPL3
%{_datadir}/fritzing
%{_datadir}/pixmaps/fritzing.png
%{_datadir}/applications/org.fritzing.Fritzing.desktop
%{_datadir}/metainfo/org.fritzing.Fritzing.appdata.xml
%{_datadir}/mime/packages/fritzing.xml
%{_bindir}/Fritzing
%{_mandir}/man1/Fritzing.1*
