# This package creates a build time version from the current date and uses it to check
# for updates. See patch2 and prep/build section.
%define _vstring %(echo %{version} |tr -d ".")

Name:           shotcut
Version:        17.11
Release:        1%{dist}
Summary:        A free, open source, cross-platform video editor
# The entire source code is GPLv3+ except mvcp/ which is LGPLv2+
License:        GPLv3+ and LGPLv2+
URL:            http://www.shotcut.org/
Source0:        https://github.com/mltframework/shotcut/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# https://forum.shotcut.org/t/appdata-xml-file-for-gnome-software-center/2742
Source1:        %{name}.appdata.xml
# Melt patch /usr/bin/mlt-melt
Patch0:         mlt_path.patch
# shotcut-desktopfile.patch -- Fix icon path
Patch1:         shotcut-desktopfile.patch
# shotcut-noupdatecheck.patch -- Disable automatic update check
Patch2:         shotcut-noupdatecheck.patch

BuildRequires:  gcc-c++
BuildRequires:  desktop-file-utils
BuildRequires:  doxygen
BuildRequires:  libappstream-glib
BuildRequires:  pkgconfig(Qt5Concurrent)
BuildRequires:  pkgconfig(Qt5Core) >= 5.9.1
BuildRequires:  pkgconfig(Qt5Gui)
BuildRequires:  pkgconfig(Qt5Multimedia)
BuildRequires:  pkgconfig(Qt5Network)
BuildRequires:  pkgconfig(Qt5OpenGL)
BuildRequires:  pkgconfig(Qt5PrintSupport)
BuildRequires:  pkgconfig(Qt5Quick)
BuildRequires:  pkgconfig(Qt5WebKitWidgets)
BuildRequires:  pkgconfig(Qt5WebSockets)
BuildRequires:  pkgconfig(Qt5X11Extras)
BuildRequires:  pkgconfig(Qt5Xml)
BuildRequires:  qt5-linguist
BuildRequires:  pkgconfig(mlt++)
BuildRequires:  pkgconfig(mlt-framework)
BuildRequires:  x264-devel
BuildRequires:  webvfx-devel

# mlt-freeworld is compellingly necessary otherwise shotcut coredumps
Requires:       qt5-qtquickcontrols
Requires:       qt5-qtgraphicaleffects
Requires:       qt5-qtmultimedia
Requires:       gstreamer1-plugins-bad-free-extras
Requires:       frei0r-plugins
Requires:       ladspa
Requires:       mlt-freeworld
Requires:       lame
Requires:       ffmpeg

%description
Shotcut is a free and open-source cross-platform video editing application for
Windows, OS X, and Linux. 

Shotcut supports many video, audio, and image formats via FFmpeg and screen, 
webcam, and audio capture. It uses a time-line for non-linear video editing of 
multiple tracks that may be composed of various file formats. Scrubbing and 
transport control are assisted by OpenGL GPU-based processing and a number of 
video and audio filters are available.

%package        doc
Summary:        Documentation files for %{name}
BuildArch:      noarch

%description    doc
The %{name}-doc package contains html documentation
that use %{name}.

%define         lang_subpkg() \
%package        langpack-%{1}\
Summary:        %{2} language data for %{name}\
BuildArch:      noarch \
Requires:       %{name} = %{version}-%{release}\
Supplements:    (%{name} = %{version}-%{release} and langpacks-%{1})\
\
%description    langpack-%{1}\
%{2} language data for %{name}.\
\
%files          langpack-%{1}\
%{_datadir}/%{name}/translations/%{name}_%{1}*.qm

%lang_subpkg ca Catalan
%lang_subpkg cs Czech
%lang_subpkg da Danish
%lang_subpkg de German
%lang_subpkg el Greek
%lang_subpkg en English
%lang_subpkg es Spanish
%lang_subpkg fr French
%lang_subpkg gd "(Scottish Gaelic)"
%lang_subpkg hu Hungarian
%lang_subpkg it Italian
%lang_subpkg ja Japanese
%lang_subpkg nb Norwegian
%lang_subpkg nl Dutch
%lang_subpkg oc Occitan
%lang_subpkg pl Polish
%lang_subpkg pt_BR "Portuguese (Brazil)"
%lang_subpkg pt_PT "Portuguese (Portugal)"
%lang_subpkg ru Russian
%lang_subpkg sk Slovakian
%lang_subpkg sl Slovenian
%lang_subpkg tr Turkish
%lang_subpkg uk Ukrainian
%lang_subpkg zh_CN "Chinese (S)"
%lang_subpkg zh_TW "Chinese (T)"

%prep
%autosetup -p0

# Create version.json from current version
echo "{" > version.json
echo " \"version_number\": %{_vstring}04," >> version.json
echo " \"version_string\": \"%{version}.04\"," >> version.json
echo " \"url\": \"https://shotcut.org/blog/new-release-%{_vstring}/\"" >> version.json
echo "}" >> version.json
echo "" >> version.json

# Postmortem debugging tools for MinGW.
rm -rf drmingw

%build
export _VSTRING="%{version}.04"
%{qmake_qt5} _VSTRING="%{version}.04" \
             PREFIX=%{buildroot}%{_prefix}
%make_build

# update Doxyfile
doxygen -u CuteLogger/Doxyfile
# build docs
doxygen CuteLogger/Doxyfile

%install
%make_install
install -D icons/%{name}-logo-64.png %{buildroot}/%{_datadir}/pixmaps/%{name}.png
install -Dm644 %{name}.appdata.xml %{buildroot}/%{_datadir}/appdata/%{name}.appdata.xml
install -Dm644 snap/gui/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
chmod a+x %{buildroot}/%{_datadir}/shotcut/qml/export-edl/rebuild.sh

# Install language files
langlist="$PWD/%{name}.lang"
langdir="%{_datadir}/%{name}/translations"
basedir=$(basename "$langdir")
pushd $basedir
        for ts in *.ts; do
                [ -e "$ts" ] || continue
                lupdate-qt5 "$ts" && lrelease-qt5 "$ts"
        done
        for qm in *.qm; do
                [ -e "$qm" ] || continue
                if ! grep -wqs "%dir\ $langdir" "$langlist"; then
                        echo "%dir $langdir" >>"$langlist"
                fi
                install -Dm0644 "$qm" "%{buildroot}/$langdir/$qm"
                lang="${qm%.qm}"
                echo "%lang($lang) $langdir/$qm" >>"$langlist"
        done
popd
cp -v version.json %{buildroot}%{_datadir}/%{name}

# fixes E: script-without-shebang
chmod a-x %{buildroot}%{_datadir}/%{name}/qml/filters/webvfx_ruttetraizer/ruttetraizer.html
chmod a-x %{buildroot}%{_datadir}/%{name}/qml/filters/webvfx_ruttetraizer/three.js

# fixes E: wrong-script-end-of-line-encoding
sed -i 's/\r$//' src/mvcp/{qconsole.h,qconsole.cpp}

# fixes W: spurious-executable-perm
chmod a-x src/mvcp/{qconsole.cpp,qconsole.h}

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/appdata/%{name}.appdata.xml

%files
%doc README.md
%license COPYING
%{_bindir}/%{name}
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/translations
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/applications/%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml

%files doc
%license COPYING
%doc doc

%changelog
* Sat Nov 04 2017 Martin Gansser <martinkg@fedoraproject.org> - 17.11-1
- Update to 17.11

* Sat Oct 14 2017 Martin Gansser <martinkg@fedoraproject.org> - 17.10-1
- Update to 17.10
- pkgconfig(Qt5Core) >= 5.9.2 is required
- Add LGPLv2+ to license and comment
- Build Doxygen html documentation
- Add BR doxygen

* Fri Sep 08 2017 Martin Gansser <martinkg@fedoraproject.org> - 17.09-1
- Initial build
