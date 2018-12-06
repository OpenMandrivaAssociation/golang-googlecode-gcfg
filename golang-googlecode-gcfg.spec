%if 0%{?fedora} || 0%{?rhel} == 6
%global with_devel 1
%global with_bundled 0
%global with_debug 0
%global with_check 1
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%define copying() \
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7 \
%license %{*} \
%else \
%doc %{*} \
%endif

%global provider        github
%global provider_tld    com
%global project         go-gcfg
%global repo            gcfg
# https://github.com/go-gcfg/gcfg
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     gopkg.in/gcfg.v1
%global commit          5866678811acbcbc248097f2c524cbc4d13abd8b
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global gc_import_path  code.google.com/p/gcfg
%global gopkg_name      golang-gopkg-gcfg
%global devel_main      golang-gopkg-gcfg-devel

Name:           golang-googlecode-gcfg
Version:        0
Release:        0.15.git%{shortcommit}%{?dist}
Summary:        Gcfg reads INI-style configuration files into Go structs
License:        BSD
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

Provides:      golang(%{gc_import_path}) = %{version}-%{release}
Provides:      golang(%{gc_import_path}/scanner) = %{version}-%{release}
Provides:      golang(%{gc_import_path}/token) = %{version}-%{release}
Provides:      golang(%{gc_import_path}/types) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{gc_import_path} prefix.

%package -n %{gopkg_name}-devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check}
%endif


Provides:      golang(%{import_path}) = %{version}-%{release}
Provides:      golang(%{import_path}/scanner) = %{version}-%{release}
Provides:      golang(%{import_path}/token) = %{version}-%{release}
Provides:      golang(%{import_path}/types) = %{version}-%{release}

%description -n %{gopkg_name}-devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test}
%package unit-test
Summary:         Unit tests for %{name} package
# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{gopkg_name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

%build

%install
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
install -d -p %{buildroot}/%{gopath}/src/%{gc_import_path}/

# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{gc_import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{gc_import_path}/$file
    echo "%%{gopath}/src/%%{gc_import_path}/$file" >> gc_devel.file-list
done
pushd %{buildroot}/%{gopath}/src/%{gc_import_path}
sed -i 's/"gopkg\.in\/gcfg\.v1/"code\.google\.com\/p\/gcfg/g' \
        $(find . -name '*.go')
popd
%endif

# testing files for this project
%if 0%{?with_unit_test}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
for file in $(find testdata -iname "*.gcfg"); do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%ifarch 0%{?gccgo_arches}
function gotest { %{gcc_go_test} "$@"; }
%else
%if 0%{?golang_test:1}
function gotest { %{golang_test} "$@"; }
%else
function gotest { go test "$@"; }
%endif
%endif

export GOPATH=%{buildroot}/%{gopath}:%{gopath}
gotest %{import_path}
gotest %{import_path}/scanner
gotest %{import_path}/token
gotest %{import_path}/types
%endif

%if 0%{?with_devel}
%files devel -f gc_devel.file-list
%copying LICENSE
%doc README
%dir %{gopath}/src/%{gc_import_path}

%files -n %{gopkg_name}-devel -f devel.file-list
%copying LICENSE
%doc README
%dir %{gopath}/src/%{import_path}
%endif

%if 0%{?with_unit_test}
%files unit-test -f unit-test.file-list
%copying LICENSE
%doc README
%endif

%changelog
* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.15.git5866678
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.14.git5866678
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.13.git5866678
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.12.git5866678
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.11.git5866678
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.10.git5866678
- https://fedoraproject.org/wiki/Changes/golang1.7

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.9.git5866678
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.8.git5866678
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Aug 20 2015 jchaloup <jchaloup@redhat.com> - 0-0.7.git5866678
- Choose the corret devel subpackage
  related: #1250517

* Wed Aug 19 2015 jchaloup <jchaloup@redhat.com> - 0-0.6.git5866678
- Update spec file to spec-2.0
  resolves: #1250517

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.5.gitc2d3050
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jan 22 2015 jchaloup <jchaloup@redhat.com> - 0-0.4.gitc2d3050
- Choose the correct architecture
- Add missing tests
  related: #1141880

* Tue Oct 07 2014 jchaloup <jchaloup@redhat.com> - 0-0.3.gitc2d3050
- updating summary of devel subpackage

* Fri Sep 12 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.2gitc2d3050
- don't own dirs owned by golang
- preserve timestamps
- noarch

* Fri Sep 12 2014 Eric Paris <eparis@redhat.com - 0.0.0-0.1.gitc2d30500
- Bump to upstream c2d3050044d05357eaf6c3547249ba57c5e235cb
