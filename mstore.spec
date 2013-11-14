%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: mstore 
Version: 0.1.0
Release: 1%{?dist}
Summary: deploy openstack

Group: Development/Languages
License: BSD
URL: http://rockontrol.com
Source0: http://rockontrol.com/mstore-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
BuildRequires: python-setuptools-devel 
BuildRequires: python-paste python-paste-deploy python-routes


%description
deploy openstack on centos

%prep
%setup -q -n mstore-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
install -p -D -m 755 bin/mstore-server %{buildroot}%{_bindir}/mstore-server
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/mstore/
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/init.d/
install -p -D -m 755 etc/init.d/mstore-server %{buildroot}%{_sysconfdir}/init.d/

mkdir -p -m 755 %{buildroot}/var/run/mstore-server
mkdir -p -m 755 %{buildroot}/var/log/mstore-server
mkdir -p -m 755 %{buildroot}/var/lib/mstore-server


#find %{buildroot} -name "*.py" -exec rm -f {} \;
%check

%clean
rm -rf $RPM_BUILD_ROOT

%post 
chkconfig mstore-server on

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service mstore-server stop >/dev/null 2>&1
    /sbin/chkconfig --del mstore-server 
fi

%files
%defattr(-,root,root,-)
%doc LICENSE README docs
%{python_sitelib}/*
%{_bindir}/mstore-server
%dir %{_sysconfdir}/mstore
%dir /var/log/mstore-server
%dir /var/lib/mstore-server
%dir /var/run/mstore-server
%{_sysconfdir}/init.d/mstore-server


%changelog
* Tue May 28 2013 zhou yu <zhouyu@rockontrol.com> - 0.1.0-1
- Update to 0.1.0
