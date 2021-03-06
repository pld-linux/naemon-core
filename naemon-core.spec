#
# Conditional build:
%bcond_with	tests		# build with tests
%bcond_with	doc		# build doc

Summary:	Open Source Host, Service And Network Monitoring Program
Name:		naemon-core
Version:	1.0.3
Release:	0.7
License:	GPL v2
Group:		Applications/System
Source0:	http://labs.consol.de/naemon/release/v%{version}/src/%{name}-%{version}.tar.gz
# Source0-md5:	5eb9c6e9be29b993e8488d58f8b3de23
Source1:	naemon.logrotate
URL:		http://www.naemon.org/
BuildRequires:	chrpath
BuildRequires:	gperf
BuildRequires:	help2man
BuildRequires:	perl-ExtUtils-MakeMaker
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	zlib-devel
Provides:	group(naemon)
Provides:	user(naemon)
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		plugindir		%{_prefix}/lib/nagios/plugins
%define		naemonhome		/var/lib/naemon

%description
Naemon is an application, system and network monitoring application.
It can escalate problems by email, pager or any other medium. It is
also useful for incident or SLA reporting. It is originally a fork of
Nagios, but with extended functionality, stability and performance.

%package devel
Summary:	Development Files For Naemon
Group:		Development/Libraries

%description devel
This package contains the header files, static libraries and
development documentation for naemon-core.

If you are a NEB-module author or wish to write addons for Naemon
using Naemons own APIs, you should install this package.

%prep
%setup -q

%build
%configure \
	--with-logrotatedir=%{_sysconfdir}/logrotate.d \
	--with-initdir=%{_initrddir} \
	--with-pluginsdir=%{plugindir} \
	--localstatedir=%{_localstatedir}/lib/naemon \
	--with-lockfile=%{_localstatedir}/run/naemon/naemon.pid \
	--with-checkresultdir=%{_localstatedir}/spool/naemon/checkresults \
	%{__with_without tests} \
	--enable-event-broker \
	--with-naemon-user=naemon \
	--with-naemon-group=naemon \
	--with-mail=/bin/mail

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
    INSTALL_OPTS="" \
    COMMAND_OPTS="" \
    INIT_OPTS="" \
    DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_localstatedir}/{lib/naemon,log/naemon/archives}

%if %{with doc}
### Install documentation
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/search
cp -a Documentation/html/* $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation
chmod 0755 $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/search
rm $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/installdox
%endif

# Put the new RC sysconfig in place
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
cp -p sample-config/naemon.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/naemon

cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/naemon

# Install systemd entry
install -D -p daemon-systemd $RPM_BUILD_ROOT%{systemdunitdir}/naemon.service
install -D -p naemon.tmpfiles.conf $RPM_BUILD_ROOT%{systemdtmpfilesdir}/naemon.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig

%pre
%groupadd -g 321 naemon
%useradd -u 321 -d %{naemonhome} -s /bin/false -c "Naemon Daemon" -g naemon -G naemon naemon

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	%userremove naemon
	%groupremove naemon
fi

%files
%defattr(644,root,root,755)
%doc README.md
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/naemon
%attr(754,root,root) /etc/rc.d/init.d/naemon
%attr(755,root,root) %{_libdir}/libnaemon.so.*.*.*
%ghost %{_libdir}/libnaemon.so.0
%attr(755,root,root) %{_bindir}/naemon
%attr(755,root,root) %{_bindir}/naemonstats
%attr(755,root,root) %{_bindir}/oconfsplit
%attr(755,root,root) %{_bindir}/shadownaemon
%{_mandir}/man8/naemon.8*
%{_mandir}/man8/naemonstats.8*
%{_mandir}/man8/oconfsplit.8*
%{_mandir}/man8/shadownaemon.8*
%{systemdunitdir}/naemon.service
%{systemdtmpfilesdir}/naemon.conf
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/naemon
%dir %{_sysconfdir}/naemon
%dir %{_sysconfdir}/naemon/conf.d
%dir %{_sysconfdir}/naemon/conf.d/templates
%config(noreplace) %{_sysconfdir}/naemon/naemon.cfg
%config(noreplace) %{_sysconfdir}/naemon/resource.cfg
%config(noreplace) %{_sysconfdir}/naemon/conf.d/*.cfg
%config(noreplace) %{_sysconfdir}/naemon/conf.d/templates/*.cfg
%dir %{_localstatedir}/spool/naemon
%attr(2775,naemon,http) %dir %{_localstatedir}/spool/naemon/checkresults
%attr(775,root,naemon) %dir %{_localstatedir}/lib/naemon
%attr(775,root,naemon) %dir %{_localstatedir}/log/naemon
%attr(775,root,naemon) %dir %{_localstatedir}/log/naemon/archives

%if %{with doc}
%attr(-,root,root) %{_datadir}/%{name}/documentation
%endif

%files devel
%defattr(644,root,root,755)
%{_includedir}/naemon
%{_libdir}/libnaemon.a
%{_libdir}/libnaemon.la
%{_libdir}/libnaemon.so
%{_pkgconfigdir}/naemon.pc
