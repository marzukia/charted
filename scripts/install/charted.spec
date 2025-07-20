Name:           charted
Version:        0.1.0
Release:        1%{?dist}
Summary:        Native SVG chart generation library
License:        MIT
URL:            https://github.com/marzukia/charted
Source0:        https://github.com/marzukia/charted/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-pip
Requires:       python3

%description
charted is a native SVG chart generation library for creating publication-quality
charts without external dependencies.

%prep
%setup -q

%build
%py3_build

%install
%py3_install

%files
%{python3_sitepackages}/charted/
%{python3_sitepackages}/charted-%{version}-*.dist-info/
%bindir/charted

%changelog
* Mon Apr 22 2026 Janky <janky@example.com> - 0.1.0-1
- Initial package
