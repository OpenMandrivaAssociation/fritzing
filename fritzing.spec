Name:		fritzing
Version:	1.0.8
Release:	1
Summary:	Electronic Design Automation software
License:	GPL-3.0-or-later AND CC-BY-SA-3.0 AND BSL-1.0
Group:		Sciences/Other
Url:		https://fritzing.org/
# Upstream no longer tags releases. 1.0.8 (2026-08-12) is develop @ 5aa56a5.
# https://github.com/fritzing/fritzing-app
Source0:	https://github.com/fritzing/fritzing-app/archive/refs/heads/develop.tar.gz
# https://github.com/fritzing/fritzing-parts
Source1:	https://github.com/fritzing/fritzing-parts/archive/refs/heads/develop.zip
# Header-only SVG parser (not packaged separately)
Source2:	https://github.com/svgpp/svgpp/archive/refs/tags/v1.3.1/svgpp-1.3.1.tar.gz
# Clipper 6.4.2 sources only (cpp/clipper.{cpp,hpp}); extra-only in OMV
Source3:	clipper-6.4.2.tar.gz
# ngspice sharedspice.h (runtime lib is dlopened; extra-only in OMV)
Source4:	ngspice-sharedspice.tar.gz
# Extra parts
Source10:	https://content.arduino.cc/assets/Arduino%20Nano%2033%20BLE%20Sense.fzpz
Source11:	https://github.com/adafruit/Fritzing-Library/archive/refs/heads/master.tar.gz
Patch0:		0000-disable-autoupdate.patch
Patch2:		0002-remove-twitter4j.patch
Patch3:		0003-maximum-qt-version.patch
Patch4:		0004-qt6-core5compat.patch
Patch5:		0005-gitversion.patch
Patch6:		0006-hardware-platform.patch
Patch10:	0010-quazip-detect.patch
Patch13:	0013-svgpp-detect.patch
Patch20:	0020-ngspice-location.patch

BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(Qt6PrintSupport)
BuildRequires:	pkgconfig(Qt6Svg)
BuildRequires:	pkgconfig(Qt6SvgWidgets)
BuildRequires:	pkgconfig(Qt6Widgets)
BuildRequires:	pkgconfig(Qt6Gui)
BuildRequires:	pkgconfig(Qt6Concurrent)
BuildRequires:	pkgconfig(Qt6Network)
BuildRequires:	pkgconfig(Qt6SerialPort)
BuildRequires:	pkgconfig(Qt6Sql)
BuildRequires:	pkgconfig(Qt6Xml)
BuildRequires:	pkgconfig(Qt6Core)
BuildRequires:	pkgconfig(Qt6Core5Compat)
BuildRequires:	pkgconfig(Qt6OpenGLWidgets)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(quazip1-qt6)
BuildRequires:	qmake-qt6
BuildRequires:	qt6-qttools-linguist-tools
BuildRequires:	boost-devel
# Simulator dlopens libngspice; the library is extra-only
Recommends:	%{_lib}ngspice

%description
Fritzing is an Electronic Design Automation tool for makers and hobbyists.
It offers a breadboard view, a parts library, schematic capture and PCB layout.

%prep
%autosetup -p1 -n fritzing-app-develop
# newer rpm keeps only the last -a on %%autosetup
%setup -q -T -D -a 1
%setup -q -T -D -a 2
%setup -q -T -D -a 3
%setup -q -T -D -a 4
# twitter4j examples have an incompatible license
rm -f sketches/core/Fritzing\ Creator\ Kit\ DE+EN/creator-kit-*/Fritzing/TwitterSaurus.fzz
rm -f sketches/core/Fritzing\ Creator\ Kit\ DE+EN/creator-kit-*/Processing/twitter4j-core-2.2.5.jar
rm -rf sketches/core/Fritzing\ Creator\ Kit\ DE+EN/creator-kit-*/Processing/TwitterSaurus*
rm -f sketches/core/obsolete/TwitterSaurus.fzz
# appstream rejects this url type
sed -e '/<url type="forum">/d' -i org.fritzing.Fritzing.appdata.xml

mv fritzing-parts-develop parts
cp %{S:10} parts/
tar xf %{S:11}
cp -a Fritzing-Library-master/parts/* parts/
cp -a Fritzing-Library-master/*.fzbz parts/bins/more/
cp -a Fritzing-Library-master/RPi_B parts/
rm -rf Fritzing-Library-master parts/.github .github
# cooker/main does not have ngspice or polyclipping
cat > pri/spicedetect.pri << 'EOF'
message("Using bundled ngspice sharedspice.h")
INCLUDEPATH += $$absolute_path($$PWD/../ngspice-include)
EOF
cat > pri/clipper1detect.pri << 'EOF'
message("Using bundled Clipper 1")
CLIPPER1 = $$absolute_path($$PWD/../clipper-6.4.2)
INCLUDEPATH += $$CLIPPER1
SOURCES += $$CLIPPER1/clipper.cpp
EOF

%build
export FRITZING_GIT_VERSION="5aa56a5"
export FRITZING_GIT_DATE="2026-07-28"
export FRITZING_BUILD_DATE="$(date --iso-8601=seconds)"
%if "%{_lib}" == "lib64"
export FRITZING_PLATFORM="LINUX_64"
%else
export FRITZING_PLATFORM="LINUX_32"
%endif

# .qm files are collected at qmake time for make install
lrelease phoenix.pro
%set_build_flags
qmake-qt6 phoenix.pro PREFIX=%{_prefix} \
	QMAKE_CFLAGS="${CFLAGS}" \
	QMAKE_CXXFLAGS="${CXXFLAGS}" \
	QMAKE_LFLAGS="${LDFLAGS}"
%make_build release
./Fritzing -platform offscreen -f . -pp ./parts -db ./parts/parts.db

%install
%make_install INSTALL_ROOT=%{buildroot}
# make install may skip extra files we dropped into parts/
cp -a parts %{buildroot}%{_datadir}/fritzing/
find %{buildroot}%{_datadir}/fritzing -type f -exec chmod 644 '{}' ';'
find %{buildroot}%{_datadir}/fritzing -type d -exec chmod 755 '{}' ';'

%files
%defattr(-,root,root)
%doc README.md LICENSE.CC-BY-SA LICENSE.GPL2 LICENSE.GPL3
%{_datadir}/fritzing
%{_datadir}/pixmaps/fritzing.png
%{_datadir}/applications/org.fritzing.Fritzing.desktop
%{_datadir}/metainfo/org.fritzing.Fritzing.appdata.xml
%{_datadir}/mime/packages/fritzing.xml
%{_bindir}/Fritzing
%{_mandir}/man1/Fritzing.1*
