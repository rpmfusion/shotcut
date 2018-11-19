# This package creates a build time version from the current date and uses it to check
# for updates. See patch1 and prep/build section.
%define _vstring %(echo %{version} |tr -d ".")

Name:           shotcut
Version:        18.11.18
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
# shotcut-noupdatecheck.patch -- Disable automatic update check
Patch1:         shotcut-noupdatecheck.patch

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
BuildRequires:  pkgconfig(mlt++) >= 6.10.0
BuildRequires:  pkgconfig(mlt-framework) >= 6.10.0 
BuildRequires:  x264-devel
BuildRequires:  webvfx-devel

# mlt-freeworld is compellingly necessary otherwise shotcut coredumps
Requires:       qt5-qtquickcontrols
Requires:       qt5-qtgraphicaleffects
Requires:       qt5-qtmultimedia
Requires:       gstreamer1-plugins-bad-free-extras
Requires:       frei0r-plugins
Requires:       ladspa
Requires:       mlt-freeworld >= 6.10.0
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
echo " \"version_number\": %{_vstring}02," >> version.json
echo " \"version_string\": \"%{version}.02\"," >> version.json
echo " \"url\": \"https://shotcut.org/blog/new-release-%{_vstring}/\"" >> version.json
echo "}" >> version.json
echo "" >> version.json

# Postmortem debugging tools for MinGW.
rm -rf drmingw

%build
export _VSTRING="%{version}.02"
%{qmake_qt5} _VSTRING="%{version}.02" \
             PREFIX=%{buildroot}%{_prefix}
%make_build

# update Doxyfile
doxygen -u CuteLogger/Doxyfile
# build docs
doxygen CuteLogger/Doxyfile

%install
%make_install
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

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/org.%{name}.Shotcut.desktop
appstream-util validate-relax --nonet %{buildroot}/%{_metainfodir}/org.%{name}.Shotcut.appdata.xml

%files
%doc README.md
%license COPYING
%{_bindir}/%{name}
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/translations
%{_datadir}/applications/org.%{name}.Shotcut.desktop
%{_datadir}/icons/hicolor/64x64/apps/org.%{name}.Shotcut.png
%{_metainfodir}/org.%{name}.Shotcut.appdata.xml
%{_datadir}/mime/packages/org.%{name}.Shotcut.xml

%files doc
%license COPYING
%doc doc

%changelog
* Mon Nov 19 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.11.18-1
- Update to 18.11.18

* Tue Oct 23 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.10.08-2
- Re-add mlt_path.patch

* Wed Oct 10 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.10.08-1
- Update to 18.10.08
- Dropped mlt_path.patch

* Tue Oct 02 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.10.01-0.1.beta1
- Update to 18.10.01-0.1.beta1

* Tue Oct 02 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.09.16-1
- Update to 18.09.16

* Tue Aug 21 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.08.14-1
- Update to 18.08.14

* Tue Aug 14 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.08.11-1
- Update to 18.08.11

* Tue Aug 07 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.08-1
- Update to 18.08

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 18.07-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jul 03 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.07-1
- Update to 18.07

* Tue Jun 05 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.06.02-1
- Update to 18.06.02

* Sat May 12 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.05.08-1
- Update to 18.05.08

* Fri Apr 27 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.03.06-1
- Update to 18.03.06

* Sun Mar 04 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.03-1
- Update to 18.03

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 18.01-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Jan 08 2018 Martin Gansser <martinkg@fedoraproject.org> - 18.01-1
- Update to 18.01

* Sat Dec 09 2017 Martin Gansser <martinkg@fedoraproject.org> - 17.12-2
- Rebuild

* Fri Dec 08 2017 Martin Gansser <martinkg@fedoraproject.org> - 17.12-1
- Update to 17.12

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
