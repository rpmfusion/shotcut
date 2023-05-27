Name:           shotcut
Version:        23.05.14
Release:        1%{dist}
#Release:        0.1.beta1%%{dist}
Summary:        A free, open source, cross-platform video editor
# The entire source code is GPLv3+ except mvcp/ which is LGPLv2+
License:        GPLv3+ and LGPLv2+
URL:            http://www.shotcut.org/
Source0:        https://github.com/mltframework/shotcut/archive/v%{version}/%{name}-%{version}.tar.gz
# https://forum.shotcut.org/t/appdata-xml-file-for-gnome-software-center/2742
Source1:        %{name}.appdata.xml
# Force X
Patch0:         Force_X.patch

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  desktop-file-utils
BuildRequires:  doxygen
BuildRequires:  libappstream-glib
BuildRequires:  pkgconfig(Qt6Concurrent)
BuildRequires:  pkgconfig(Qt6Core) >= 6.4.0
BuildRequires:  pkgconfig(Qt6Gui)
BuildRequires:  pkgconfig(Qt6Multimedia)
BuildRequires:  pkgconfig(Qt6Network)
BuildRequires:  pkgconfig(Qt6OpenGL)
BuildRequires:  pkgconfig(Qt6PrintSupport)
BuildRequires:  pkgconfig(Qt6Quick)
BuildRequires:  pkgconfig(Qt6QuickWidgets)
BuildRequires:  pkgconfig(Qt6QuickControls2)
BuildRequires:  pkgconfig(Qt6WebSockets)
BuildRequires:  pkgconfig(Qt6Xml)
BuildRequires:  pkgconfig(Qt6Linguist)
BuildRequires:  pkgconfig(mlt++-7) >= 7.6.0
BuildRequires:  pkgconfig(mlt-framework-7) >= 7.6.0
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  x264-devel
BuildRequires:  webvfx-devel
BuildRequires:  fftw-devel

# mlt-freeworld is compellingly necessary otherwise shotcut coredumps
Requires:       qt5-qtquickcontrols
Requires:       qt5-qtgraphicaleffects
Requires:       qt5-qtmultimedia
Requires:       gstreamer1-plugins-bad-free-extras
Requires:       frei0r-plugins
Requires:       ladspa
Requires:       mlt-freeworld >= 7.6.0
Requires:       lame
Requires:       ffmpeg

# audio filters
Suggests:       ladspa-swh-plugins

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

%lang_subpkg ar Arabic
%lang_subpkg ca Catalan
%lang_subpkg cs Czech
%lang_subpkg da Danish
%lang_subpkg de German
%lang_subpkg el Greek
%lang_subpkg en_GB "(Great Britain)"
%lang_subpkg en English
%lang_subpkg es Spanish
%lang_subpkg et Estonian
%lang_subpkg fi Finnish
%lang_subpkg fr French
%lang_subpkg gd "(Scottish Gaelic)"
%lang_subpkg gl Galician
%lang_subpkg hu Hungarian
%lang_subpkg it Italian
%lang_subpkg ja Japanese
%lang_subpkg ko Korean
%lang_subpkg nb Norwegian
%lang_subpkg ne Nepali
%lang_subpkg nl Dutch
%lang_subpkg nn Norwegian
%lang_subpkg oc Occitan
%lang_subpkg pl Polish
%lang_subpkg pt_BR "Portuguese (Brazil)"
%lang_subpkg pt_PT "Portuguese (Portugal)"
%lang_subpkg ro Romanian
%lang_subpkg ru Russian
%lang_subpkg sk Slovakian
%lang_subpkg sl Slovenian
%lang_subpkg sv Swedish
%lang_subpkg th Thai
%lang_subpkg tr Turkish
%lang_subpkg uk Ukrainian
%lang_subpkg zh_CN "Chinese (S)"
%lang_subpkg zh_TW "Chinese (T)"

%prep
%autosetup -p0

# Postmortem debugging tools for MinGW.
rm -rf drmingw

%build
%cmake -DCMAKE_INSTALL_PREFIX=%{_prefix} \
       -DUNIX_STRUCTURE=1 -GNinja \
       -DCMAKE_BUILD_TYPE=Release \
       -DSHOTCUT_VERSION=%{version} \
       -DDEFINES+=SHOTCUT_NOUPGRADE
%cmake_build

# update Doxyfile
doxygen -u CuteLogger/Doxyfile
# build docs
doxygen CuteLogger/Doxyfile

%install
%cmake_install
chmod a+x %{buildroot}/%{_datadir}/shotcut/qml/export-edl/rebuild.sh
chmod a+x %{buildroot}/%{_datadir}/shotcut/qml/export-chapters/rebuild.sh

# Install language files
langlist="$PWD/%{name}.lang"
langdir="%{_datadir}/%{name}/translations"
basedir=$(basename "$langdir")
pushd $basedir
        for ts in *.ts; do
                [ -e "$ts" ] || continue
                lupdate-qt6 "$ts" && lrelease-qt6 "$ts"
        done
        for qm in *.qm; do
                [ -e "$qm" ] || continue
                if ! grep -wqs "%dir $langdir" "$langlist"; then
                        echo "%dir $langdir" >>"$langlist"
                fi
                install -Dm0644 "$qm" "%{buildroot}/$langdir/$qm"
                lang="${qm%.qm}"
                echo "%lang($lang) $langdir/$qm" >>"$langlist"
        done
popd

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/org.%{name}.Shotcut.desktop
appstream-util validate-relax --nonet %{buildroot}/%{_metainfodir}/org.%{name}.Shotcut.metainfo.xml

%files
%doc README.md
%license COPYING
%{_bindir}/%{name}
%{_libdir}/libCuteLogger.so
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/translations
%{_datadir}/applications/org.%{name}.Shotcut.desktop
%{_datadir}/icons/hicolor/*/apps/org.%{name}.Shotcut.png
%{_metainfodir}/org.%{name}.Shotcut.metainfo.xml
%{_datadir}/mime/packages/org.%{name}.Shotcut.xml
%{_mandir}/man1/%{name}.1.*


%files doc
%license COPYING
%doc doc

%changelog
* Sat May 27 2023 Leigh Scott <leigh123linux@gmail.com> - 23.05.14-1
- Update to 23.05.14

* Thu Dec 22 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.12.21-1
- Update to 22.12.21

* Mon Nov 28 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.11.25-1
- Update to 22.11.25

* Wed Oct 26 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.10.25-1
- Update to 22.10.25

* Mon Oct 24 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.10.22-1
- Update to 22.10.22

* Mon Sep 26 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.09.23-1
- Update to 22.09.23

* Sun Aug 07 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 22.06.23-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Sat Jun 25 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.06.23-1
- Update to 22.06.23

* Fri Jun 24 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.06.07-2
- Add libdir Patch

* Thu Jun 23 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.06.07-1
- Update to 22.06.07
- Use cmake instead of qmake
- Fix libdir install path

* Mon May 02 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.04.25-1
- Update to 22.04.25

* Mon Apr 25 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.04.22-1
- Update to 22.04.22

* Thu Mar 31 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.03.30-1
- Update to 22.03.30

* Wed Feb 09 2022 Martin Gansser <martinkg@fedoraproject.org> - 22.01.30-1
- Update to 22.01.30

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 21.03.21-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Tue Apr 06 2021 Martin Gansser <martinkg@fedoraproject.org> - 21.03.21-2
- Add suggested audio filters ladspa-swh-plugins fix (RBZ#5965)

* Mon Mar 22 2021 Martin Gansser <martinkg@fedoraproject.org> - 21.03.21-1
- Update to 21.03.21

* Sun Feb 28 2021 Martin Gansser <martinkg@fedoraproject.org> - 21.02.27-1
- Update to 21.02.27

* Thu Feb 25 2021 Martin Gansser <martinkg@fedoraproject.org> - 21.02.15-1
- Update to 21.02.15

* Thu Feb 04 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 21.01.29-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sun Jan 31 2021 Martin Gansser <martinkg@fedoraproject.org> - 21.01.29-1
- Update to 21.01.29

* Fri Jan 15 2021 Martin Gansser <martinkg@fedoraproject.org> - 20.11.28-2
- Add shotcut-numeric_limits.patch

* Mon Nov 30 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.11.28-1
- Update to 20.11.28

* Thu Nov 26 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.11.25-1
- Update to 20.11.25
- Add BR pkgconfig(Qt5QuickControls2)

* Mon Nov 02 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.10.31-1
- Update to 20.10.31

* Sun Nov  1 2020 Leigh Scott <leigh123linux@gmail.com> - 20.09.27-2
- Force X (rfbz#5822)

* Mon Sep 28 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.09.27-1
- Update to 20.09.27

* Fri Sep 18 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.09.13-1
- Update to 20.09.13

* Tue Aug 18 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 20.07.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun Jul 12 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.07.11-1
- Update to 20.07.11

* Mon Jun 29 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.06.28-1
- Update to 20.06.28

* Tue Apr 14 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.04.12-1
- Update to 20.04.12

* Tue Feb 18 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.02.17-1
- Update to 20.02.17

* Tue Feb 04 2020 Martin Gansser <martinkg@fedoraproject.org> - 20.02.02-0.1.beta1
- Update to 20.02.02-0.1.beta1

* Wed Jan 01 2020 Martin Gansser <martinkg@fedoraproject.org> - 19.12.31-1
- Update to 19.12.31

* Wed Dec 18 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.12.16-1
- Update to 19.12.16

* Mon Dec 09 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.12.08-0.1.beta1
- Update to 19.12.08-0.1.beta1

* Thu Nov 07 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.10.20-1
- Update to 19.10.20
- Add Galician and Thai translation file

* Tue Sep 17 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.09.14-2
- Add missing translations for ko, nn and sv

* Tue Sep 17 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.09.14-1
- Update to 19.09.14

* Mon Aug 19 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.08.16-1
- Update to 19.08.16

* Fri Aug 09 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 19.07.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jul 19 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.07.15-1
- Update to 19.07.15

* Mon Jun 24 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.06.15-1
- Update to 19.06.15

* Tue Jun 04 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.06.04-1
- Update to 19.06.04

* Thu Mar 21 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.02.28-1
- Update to 19.02.28

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 19.01.27-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 28 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.01.27-1
- Update to 19.01.27

* Fri Jan 25 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.01.24-1
- Update to 19.01.24

* Mon Jan 21 2019 Martin Gansser <martinkg@fedoraproject.org> - 19.01.19-0.1.beta1
- Update to 19.01.19-0.1.beta1

* Wed Jan 02 2019 Martin Gansser <martinkg@fedoraproject.org> - 18.12.23-1
- Update to 18.12.23

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
