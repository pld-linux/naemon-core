#
# Conditional build:
%bcond_with	doc		# build doc

Summary:	Open Source Host, Service And Network Monitoring Program
Name:		naemon-core
Version:	1.0.3
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	http://labs.consol.de/naemon/release/v%{version}/src/%{name}-%{version}.tar.gz
# Source0-md5:	5eb9c6e9be29b993e8488d58f8b3de23
URL:		http://www.naemon.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	chrpath
BuildRequires:	doxygen
BuildRequires:	expat-devel
BuildRequires:	gd
BuildRequires:	gd-devel >= 1.8
BuildRequires:	gperf
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
BuildRequires:	libtool
BuildRequires:	logrotate
BuildRequires:	mysql-devel
BuildRequires:	perl
BuildRequires:	perl-ExtUtils-MakeMaker
BuildRequires:	rsync
BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
development documentation for %{name}. If you are a NEB-module author
or wish to write addons for Naemon using Naemons own APIs, you should
install this package.

%prep
%setup -q

%build
%configure \
	--with-initdir="%{_initrddir}" \
	--datadir="%{_datadir}/%{name}" \
	--libdir="%{_libdir}/%{name}" \
	--localstatedir="%{_localstatedir}/lib/%{name}" \
	--enable-event-broker \
	--without-tests \
	--with-pluginsdir="%{_libdir}/%{name}/plugins" \
	--with-tempdir="%{_localstatedir}/cache/%{name}" \
	--with-checkresultdir="%{_localstatedir}/cache/%{name}/checkresults" \
	--with-logdir="%{_localstatedir}/log/%{name}" \
	--with-logrotatedir="%{_sysconfdir}/logrotate.d" \
	--with-naemon-user="naemon" \
	--with-naemon-group="naemon" \
	--with-lockfile="%{_localstatedir}/run/%{name}/%{name}.pid" \
	--with-thruk-user="http" \
	--with-thruk-group="naemon" \
	--with-thruk-libs="%{_libdir}/%{name}/perl5" \
	--with-thruk-tempdir="%{_localstatedir}/cache/%{name}/thruk" \
	--with-thruk-vardir="%{_localstatedir}/lib/%{name}/thruk" \
	--with-httpd-conf="%{_sysconfdir}/httpd/conf.d" \
	--with-htmlurl="/%{name}"

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
    DESTDIR="$RPM_BUILD_ROOT" \
    INSTALL_OPTS="" \
    COMMAND_OPTS="" \
    INIT_OPTS=""

install -d $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}

%if %{with doc}
### Install documentation
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/search
cp -a Documentation/html/* $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation
chmod 0755 $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/search
rm $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/installdox
%endif

# Put the new RC sysconfig in place
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -p sample-config/naemon.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/%{name}
ln -s %{_libdir}/nagios/plugins $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins

# Install systemd entry
install -D -p daemon-systemd $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
install -D -p naemon.tmpfiles.conf $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf
# Move SystemV init-script
#mv -f $RPM_BUILD_ROOT%{_initrddir}/%{name} $RPM_BUILD_ROOT%{_bindir}/%{name}-ctl

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md
%attr(754,root,root) /etc/rc.d/init.d/naemon
%attr(755,root,root) %{_bindir}/naemon
%attr(755,root,root) %{_bindir}/naemonstats
%attr(755,root,root) %{_bindir}/oconfsplit
%attr(755,root,root) %{_bindir}/shadownaemon
%{_mandir}/man8/naemon.8*
%{_mandir}/man8/naemonstats.8*
%{_mandir}/man8/oconfsplit.8*
%{_mandir}/man8/shadownaemon.8*
%{systemdunitdir}/%{name}.service
%{systemdtmpfilesdir}/%{name}.conf
%config(noreplace) /etc/logrotate.d/naemon
%dir %{_sysconfdir}/naemon/
%attr(2775,naemon,naemon) %dir %{_sysconfdir}/naemon/conf.d
%config(noreplace) %{_sysconfdir}/naemon/naemon.cfg
%config(noreplace) %{_sysconfdir}/naemon/resource.cfg
%attr(664,naemon,naemon) %config(noreplace) %{_sysconfdir}/naemon/conf.d/*.cfg
%dir %{_sysconfdir}/naemon/conf.d/templates
%attr(664,naemon,naemon) %config(noreplace) %{_sysconfdir}/naemon/conf.d/templates/*.cfg
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(2775,naemon,http) %dir %{_localstatedir}/cache/%{name}/checkresults
%attr(2775,naemon,naemon) %dir %{_localstatedir}/cache/%{name}
%attr(755,naemon,naemon) %dir %{_localstatedir}/lib/%{name}
%attr(755,naemon,naemon) %dir %{_localstatedir}/log/%{name}
%attr(755,naemon,naemon) %dir %{_localstatedir}/log/%{name}/archives
%if %{with doc}
%attr(-,root,root) %{_datadir}/%{name}/documentation
%endif
%attr(755,root,root) %{_libdir}/%{name}/libnaemon.so.*.*.*
%ghost %{_libdir}/%{name}/libnaemon.so.0
%attr(-,root,root) %{_libdir}/%{name}/plugins

%files devel
%defattr(644,root,root,755)
%{_includedir}/naemon
%{_libdir}/%{name}/libnaemon.a
%{_libdir}/%{name}/libnaemon.la
%{_libdir}/%{name}/libnaemon.so
%{_libdir}/%{name}/pkgconfig/naemon.pc
