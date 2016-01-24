#
# spec file for package python-tomate
#
# Copyright (c) 2014 Elio Esteves Duarte <elio.esteves.duarte@gmail.com>
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#
%global debug_package %{nil}

%define real_name tomate
%define module_name %{real_name}_statusicon_plugin

Name: %{real_name}-statusicon-plugin
Version: 0.2.0
Release: 0
License: GPL-3.0+
Summary: Tomate statusicon plugin
Source: %{name}-upstream.tar.gz
Url: https://github.com/eliostvs/tomate-statusicon-plugin

BuildRoot: %{_tmppath}/%{name}-%{version}-build

BuildRequires: python-devel
BuildRequires: python-setuptools
Conflicts: tomate-indicator-plugin

%if 0%{?suse_version} > 1310
BuildRequires: adwaita-icon-theme
%endif

%if 0%{?fedora} > 20
BuildRequires: adwaita-icon-theme
%endif

Requires: tomate-gtk >= 0.4.0

%if 0%{?suse_version}
BuildArchitectures: noarch
BuildRequires: hicolor-icon-theme
%endif

%description
Tomate plugin that shows the session progress in the notification area.

%prep
%setup -q -n %{name}-upstream

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot}

%post
%if 0%{?suse_version}
%icon_theme_cache_post
%endif
%if 0%{?fedora}
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/bin/touch --no-create %{_datadir}/icons/Adwaita &>/dev/null || :
%endif

%postun
%if 0%{?suse_version}
%icon_theme_cache_postun
%endif
%if 0%{?fedora}
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/Adwaita &>/dev/null || :
fi
%endif

%files
%defattr(-,root,root,-)
%dir %{_datadir}/%{real_name}/
%{_datadir}/%{real_name}/plugins/
%{_datadir}/icons/hicolor/*/*/*.*
%{_datadir}/icons/Adwaita/*/*/*.*
%if 0%{?suse_version} == 1310
%dir %{_datadir}/icons/Adwaita/
%dir %{_datadir}/icons/Adwaita/22x22/
%dir %{_datadir}/icons/Adwaita/22x22/status
%endif
%{python_sitelib}/%{module_name}-%{version}-*.egg-info/

%doc AUTHORS COPYING README.md

%changelog